#!/usr/bin/env python3
"""Local-only article appraisal contract checker; not a medical validator."""
import argparse
import base64
import hashlib
import json
import os
import re
from html import escape
from pathlib import Path
from urllib.parse import quote


SECTIONS = dict(zip(
    ("executive_summary methods intervention results statistical_appraisal "
     "methodological_appraisal clinical_relevance safety authors_conclusion "
     "independent_conclusion limitations").split(),
    ("Resumo executivo", "Métodos", "Intervenção / exposição", "Resultados",
     "Avaliação estatística", "Avaliação metodológica", "Relevância clínica",
     "Segurança", "Conclusão dos autores", "Conclusão independente", "Limitações")))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, where):
    require(isinstance(value, str) and value.strip(), f"{where}: texto obrigatório")


def shape(value, fields, where, optional=""):
    required, allowed = set(fields.split()), set((fields + " " + optional).split())
    require(isinstance(value, dict) and required <= value.keys() <= allowed,
            f"{where}: campos ausentes ou desconhecidos")


def index(rows, fields, where):
    require(isinstance(rows, list) and rows, f"{where}: lista não vazia obrigatória")
    result = {}
    for row in rows:
        shape(row, fields, where)
        text(row["id"], where + ".id")
        require(row["id"] not in result, f"{where}: id duplicado")
        result[row["id"]] = row
    return result


def refs(ids, known, where):
    require(isinstance(ids, list) and ids and all(isinstance(i, str) for i in ids),
            f"{where}: evidence_ids/referências obrigatórias")
    require(len(ids) == len(set(ids)) and set(ids) <= set(known), f"{where}: referências inválidas")


def no_placeholders(value):
    if isinstance(value, str):
        marker = value.strip().upper()
        require(marker not in ("TODO", "TBD", "...", "A PREENCHER") and
                not marker.startswith(("PREENCHER:", "TODO:", "TBD:", "[A PREENCHER]")),
                "placeholder não permitido em registro preenchido")
    elif isinstance(value, (dict, list)):
        for entry in value.values() if isinstance(value, dict) else value:
            no_placeholders(entry)


def validate(record, base):
    shape(record, "article scope sources evidence claims sections assessment human_review", "record", "visuals")
    no_placeholders(record)
    shape(record["article"], "id title reference design", "article")
    for key, value in record["article"].items():
        text(value, "article." + key)
    sources = index(record["sources"], "id label kind path", "sources")
    evidence = index(record["evidence"], "id source_id locator quote", "evidence")
    source_texts = {}
    visuals = record.get("visuals", [])
    require(isinstance(visuals, list), "visuals: lista obrigatória")
    if visuals:
        index(visuals, "id kind source_id source_page label path sha256 caption analysis evidence_ids section", "visuals")
    require(sum(v["kind"] == "article_header" for v in visuals) <= 1,
            "visuals: no máximo um article_header")
    for visual in visuals:
        for field in ("label", "caption", "analysis"):
            text(visual[field], "visuals." + field)
        require(visual["kind"] in ("article_header", "figure", "table"), "visuals.kind inválido")
        require(isinstance(visual["section"], str) and visual["section"] in SECTIONS
                and (visual["kind"] != "article_header" or visual["section"] == "executive_summary"),
                "visuals.section: seção nativa obrigatória; article_header usa executive_summary")
        require(isinstance(visual["source_id"], str) and visual["source_id"] in sources
                and sources[visual["source_id"]]["kind"] == "full_text",
                "visuals.source_id: fonte full_text existente obrigatória")
        require(type(visual["source_page"]) is int and visual["source_page"] > 0,
                "visuals.source_page: inteiro positivo obrigatório (não bool)")
        refs(visual["evidence_ids"], evidence, "visuals.evidence_ids")
        name = visual["path"]
        text(name, "visuals.path")
        require(not any(c in name for c in (":", "\\", "\x00"))
                and not Path(name).is_absolute() and ".." not in Path(name).parts
                and Path(name).suffix.lower() == ".png",
                "visuals.path: PNG local relativo sem traversal obrigatório")
        path = base / name
        require(path.resolve().is_relative_to(base.resolve()) and path.is_file(),
                "visuals.path: arquivo PNG deve existir dentro da base do registro")
        data = path.read_bytes()
        require(len(data) >= 33 and data[:8] == b"\x89PNG\r\n\x1a\n"
                and data[8:16] == b"\x00\x00\x00\rIHDR"
                and int.from_bytes(data[16:20], "big") > 0
                and int.from_bytes(data[20:24], "big") > 0,
                "visuals.path: PNG com assinatura e IHDR completos obrigatório")
        require(isinstance(visual["sha256"], str)
                and re.fullmatch(r"[0-9a-f]{64}", visual["sha256"]) is not None
                and hashlib.sha256(data).hexdigest() == visual["sha256"],
                "visuals.sha256: hash inválido ou diferente do arquivo")
    for sid, source in sources.items():
        for key in ("label", "path"):
            text(source[key], "sources." + key)
        require(source["kind"] in ("full_text", "abstract", "supplement", "registry", "other"),
                "sources.kind inválido")
        path = base / source["path"]
        require(":" not in source["path"] and not source["path"].startswith("//")
                and path.suffix.lower() in (".txt", ".text", ".md") and path.is_file(),
                "sources.path: arquivo local de texto obrigatório (.txt/.text/.md)")
        source_texts[sid] = path.read_text(encoding="utf-8")
        require(all(c >= " " or c in "\n\r\t\f" for c in source_texts[sid]),
                "sources.path: conteúdo binário não permitido")
    for entry in evidence.values():
        for key in ("source_id", "locator", "quote"):
            text(entry[key], "evidence." + key)
        require(entry["source_id"] in sources, "evidence.source_id desconhecido")
        require(" ".join(entry["quote"].split()) in
                " ".join(source_texts[entry["source_id"]].split()),
                "evidence.quote ausente na fonte declarada")
    claims = index(record["claims"], "id text evidence_ids kind", "claims")
    for claim in claims.values():
        text(claim["text"], "claims.text")
        require(claim["kind"] in ("extracted", "interpretation"), "claims.kind inválido")
        refs(claim["evidence_ids"], evidence, "claims.evidence_ids")
    sections = record["sections"]
    require(isinstance(sections, dict) and set(sections) == set(SECTIONS), "sections incompletas")
    for key, ids in sections.items():
        refs(ids, claims, f"sections.{key}")
    scope = record["scope"]
    shape(scope, "status protocol_version reason criteria", "scope")
    require(scope["status"] in ("eligible", "ineligible", "uncertain", "undefined"), "scope.status inválido")
    text(scope["reason"], "scope.reason")
    require(isinstance(scope["protocol_version"], str), "scope.protocol_version: texto obrigatório")
    if scope["status"] == "undefined":
        require(scope["protocol_version"] == "", "scope.protocol_version deve ser vazio com undefined")
    else:
        text(scope["protocol_version"], "scope.protocol_version")
    require(isinstance(scope["criteria"], list), "scope.criteria: lista obrigatória")
    decisions, names = [], set()
    for criterion in scope["criteria"]:
        shape(criterion, "criterion status evidence_ids", "scope.criteria")
        text(criterion["criterion"], "scope.criteria.criterion")
        require(criterion["criterion"] not in names, "scope.criteria: critério duplicado")
        names.add(criterion["criterion"])
        require(criterion["status"] in ("met", "not_met", "uncertain"), "scope.criteria.status inválido")
        refs(criterion["evidence_ids"], evidence, "scope.criteria.evidence_ids")
        decisions.append(criterion["status"])
    verdict = ("ineligible" if "not_met" in decisions else "uncertain" if "uncertain" in decisions
               else "eligible" if decisions else "undefined")
    require(scope["status"] == verdict, "scope.status incompatível com critérios de elegibilidade")
    assessment = record["assessment"]
    shape(assessment, "instrument version status items", "assessment", "coverage")
    require(assessment["status"] in ("complete", "limited", "not_applicable"), "assessment.status inválido")
    for key in ("instrument", "version"):
        text(assessment[key], "assessment." + key)
    items = index(assessment["items"], "id domain judgment reason evidence_ids", "assessment.items")
    for item in items.values():
        for key in ("domain", "judgment", "reason"):
            text(item[key], "assessment.items." + key)
        refs(item["evidence_ids"], evidence, "assessment.items.evidence_ids")
    require(assessment["status"] != "complete" or "coverage" in assessment,
            "assessment.coverage obrigatória para complete")
    if "coverage" in assessment:
        coverage = assessment["coverage"]
        shape(coverage, "expected_ids answered_ids", "assessment.coverage")
        refs(coverage["expected_ids"], coverage["expected_ids"], "assessment.coverage.expected_ids")
        refs(coverage["answered_ids"], coverage["expected_ids"], "assessment.coverage.answered_ids")
        require(set(coverage["answered_ids"]) == set(items), "assessment.coverage difere dos items")
        if assessment["status"] == "complete":
            require(set(coverage["expected_ids"]) == set(items), "assessment.coverage: itens omitidos")
    if assessment["status"] == "complete":
        cited = [eid for item in assessment["items"] for eid in item["evidence_ids"]]
        require(any(eid in evidence and sources[evidence[eid]["source_id"]]["kind"] == "full_text"
                    for eid in cited), "assessment complete requer evidência full_text citada")
    review = record["human_review"]
    shape(review, "status reviewer notes", "human_review")
    require(review["status"] in ("pending", "reviewed"), "human_review.status inválido")
    for key in ("reviewer", "notes"):
        require(isinstance(review[key], str), "human_review." + key + ": texto obrigatório")
    if review["status"] == "reviewed":
        text(review["reviewer"], "human_review.reviewer")


def markdown_text(value):
    return re.sub(r"([\\`*_{}\[\]()#|])", r"\\\1", escape(" ".join(value.split())))


def render(record, base=Path("."), *, output_base=None):
    """Render a validated record; base reads assets, output_base locates MD links."""
    article, scope, assessment, review = (record[k] for k in ("article", "scope", "assessment", "human_review"))
    claims = {c["id"]: c for c in record["claims"]}
    references = lambda ids: "; ".join("[" + i + "]" for i in ids)
    metadata = {"id": "Identificador no acervo", "reference": "Referência bibliográfica", "design": "Desenho"}
    source_kinds = {"full_text": "Texto completo", "abstract": "Resumo", "supplement": "Suplemento",
                    "registry": "Registro", "other": "Outro"}
    blocks = [("h1", "Análise crítica de artigo científico"), ("h2", article["title"]),
              ("p", "Análise elaborada por agente de IA."),
              ("table", (["Metadado", "Registro"], [[label, article[k]] for k, label in metadata.items()]))]
    if not any(s["kind"] == "full_text" for s in record["sources"]):
        blocks.append(("p", "Texto completo não fornecido; julgamentos restritos ao material disponível."))
    visuals = record.get("visuals", [])
    blocks = [("visual", v) for v in visuals if v["kind"] == "article_header"] + blocks
    for key, heading in SECTIONS.items():
        blocks.append(("h2", heading))
        for cid in record["sections"][key]:
            claim = claims[cid]
            kind = "Extração" if claim["kind"] == "extracted" else "Interpretação"
            blocks.append(("p", f'[{cid}] {kind}: {claim["text"]} — {references(claim["evidence_ids"])}'))
        blocks += [("visual", v) for v in visuals if v["kind"] != "article_header" and v["section"] == key]
    verdicts = {"eligible": "Elegível", "ineligible": "Inelegível — excluído do escopo",
                "uncertain": "Incerto", "undefined": "Indefinido — sem decisão de elegibilidade"}
    blocks += [("h2", "Elegibilidade"), ("p", f'Veredito: {verdicts[scope["status"]]} ({scope["status"]})'),
               ("p", "Protocolo: " + (scope["protocol_version"] or "Não definido")), ("p", scope["reason"])]
    if scope["criteria"]:
        labels = {"met": "Atendido", "not_met": "Não atendido", "uncertain": "Incerto"}
        blocks.append(("table", (["Critério", "Situação", "Evidências"],
            [[c["criterion"], labels[c["status"]], references(c["evidence_ids"])] for c in scope["criteria"]])))
    else:
        blocks.append(("p", "Critérios não definidos; não há aprovação de elegibilidade."))
    statuses = {"complete": "Completa — inventário declarado", "limited": "Limitada", "not_applicable": "Não aplicável"}
    blocks += [("h2", "Julgamentos metodológicos"),
               ("p", f'Instrumento: {assessment["instrument"]} · Versão: {assessment["version"]}'),
               ("p", "Situação: " + statuses[assessment["status"]]),
               ("table", (["ID", "Domínio", "Julgamento", "Justificativa", "Evidências"],
                [[i["id"], i["domain"], i["judgment"], i["reason"], references(i["evidence_ids"])]
                 for i in assessment["items"]]))]
    if "coverage" in assessment:
        for key, label in (("expected_ids", "Itens esperados"), ("answered_ids", "Itens respondidos")):
            blocks.append(("p", label + ": " + "; ".join(assessment["coverage"][key])))
    else:
        blocks.append(("p", "Inventário oficial não fornecido; cobertura não verificada."))
    blocks += [("h2", "Registro de evidências"),
               ("table", (["ID", "Fonte", "Localizador", "Citação literal"],
                [[e[k] for k in ("id", "source_id", "locator", "quote")] for e in record["evidence"]])),
               ("h2", "Fontes consultadas"), ("table", (["ID", "Fonte", "Tipo", "Arquivo local"],
                [[s["id"], s["label"], source_kinds[s["kind"]] + " (" + s["kind"] + ")", s["path"]]
                 for s in record["sources"]]))]
    if review["notes"]:
        blocks.append(("p", "Notas de revisão: " + review["notes"]))
    footer = ("Revisão humana: pendente" if review["status"] == "pending"
              else "Revisão humana: revisado por " + review["reviewer"])
    blocks.append(("footer", footer))
    md, html = [], []
    for kind, data in blocks:
        if kind == "visual":
            source = next(s for s in record["sources"] if s["id"] == data["source_id"])
            caption = data["label"] + " — " + data["caption"]
            provenance = (f'Fonte: {data["source_id"]} — {source["label"]}; página {data["source_page"]}. '
                          + "Evidências: " + references(data["evidence_ids"]))
            analysis = "Análise: " + data["analysis"]
            image = base64.b64encode((base / data["path"]).read_bytes()).decode("ascii")
            output_directory = (base if output_base is None else output_base).resolve()
            relative_image = Path(os.path.relpath((base / data["path"]).resolve(), output_directory)).as_posix()
            link = quote(relative_image, safe="/")
            md += [f'![{markdown_text(data["label"])}]({link})', "",
                   markdown_text(caption), "", markdown_text(provenance), "", markdown_text(analysis), ""]
            html.append('<figure><img src="data:image/png;base64,' + image + '" alt="'
                        + escape(data["label"]) + '" style="max-width:100%;height:auto">'
                        + '<figcaption>' + escape(caption) + '</figcaption><p>'
                        + escape(provenance) + '</p><p>' + escape(analysis) + '</p></figure>')
        elif kind == "table":
            headers, rows = data
            md += [" | ".join(map(markdown_text, headers)), " | ".join(["---"] * len(headers))]
            md += [" | ".join(map(markdown_text, row)) for row in rows] + [""]
            html.append("<table><thead><tr>" + "".join("<th>" + escape(c) + "</th>" for c in headers)
                        + "</tr></thead><tbody>" + "".join("<tr>" + "".join("<td>" + escape(c) + "</td>" for c in row)
                        + "</tr>" for row in rows) + "</tbody></table>")
        else:
            md += [("# " if kind == "h1" else "## " if kind == "h2" else "") + markdown_text(data), ""]
            html.append(f"<{kind}>{escape(data)}</{kind}>")
    css = ("body{font:16px/1.6 Arial,sans-serif;color:#334155;max-width:1050px;margin:40px auto;padding:24px}"
           "h1,h2{color:#1e3a5f}h2{border-bottom:1px solid #cbd5e1;padding-top:20px}"
           "table{width:100%;border-collapse:collapse;margin:16px 0}th{background:#e2e8f0;color:#1e3a5f}"
           "td,th{border:1px solid #cbd5e1;padding:10px;text-align:left;overflow-wrap:anywhere}"
           "footer{border-top:1px solid #cbd5e1;margin-top:32px;font-size:13px;color:#64748b}"
           "@media print{body{margin:0;max-width:none}tr{break-inside:avoid}thead{display:table-header-group}}")
    document = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>Análise crítica de artigo científico</title><style>' + css
                + '</style></head><body>' + "\n".join(html) + '</body></html>\n')
    return "\n".join(md), document


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "chave JSON duplicada: " + key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "render"])
    parser.add_argument("record", type=Path)
    parser.add_argument("--output-prefix", type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        validate(record, args.record.resolve().parent)
        if args.command == "render":
            require(args.output_prefix is not None, "render requer --output-prefix")
            md, html = render(record, args.record.resolve().parent, output_base=args.output_prefix.parent.resolve())
            outputs = [Path(str(args.output_prefix) + suffix) for suffix in (".md", ".html")]
            inputs = {args.record.resolve()} | {
                (args.record.resolve().parent / s["path"]).resolve() for s in record["sources"]}
            inputs |= {(args.record.resolve().parent / v["path"]).resolve() for v in record.get("visuals", [])}
            require(all(p.resolve() not in inputs for p in outputs), "saída colide com arquivo de entrada")
            args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
            for path, content in zip(outputs, (md, html)):
                path.write_text(content, encoding="utf-8")
                print(path)
        else:
            print("Registro válido: " + record["article"]["id"])
    except (ValueError, OSError) as error:
        parser.exit(2, f"Erro: {error}\n")


if __name__ == "__main__":
    main()
