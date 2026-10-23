"""Contract tests; every source and record here is explicitly SYNTHETIC."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("appraisal_report.py")
SECTION_KEYS = (
    "executive_summary methods intervention results statistical_appraisal "
    "methodological_appraisal clinical_relevance safety authors_conclusion "
    "independent_conclusion limitations"
).split()
QUOTE = "SYNTHETIC: documento de teste sem dados clínicos."


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "synthetic.txt").write_text(
            QUOTE + "\nNão informado: informação ausente neste texto de teste.\n",
            encoding="utf-8",
        )
        self.record = {
            "article": {"id": "SYNTHETIC-ONLY", "title": "Documento sintético de teste",
                        "reference": "SYNTHETIC — não é um artigo real", "design": "Sintético"},
            "scope": {"status": "undefined", "protocol_version": "",
                      "reason": "Protocolo não fornecido; sem decisão de elegibilidade.", "criteria": []},
            "sources": [{"id": "S1", "label": "Fonte exclusivamente sintética",
                         "kind": "full_text", "path": "synthetic.txt"}],
            "evidence": [{"id": "E1", "source_id": "S1", "locator": "Linha 1", "quote": QUOTE}],
            "claims": [{"id": "C1", "text": "Conteúdo exclusivamente sintético de teste.",
                        "evidence_ids": ["E1"], "kind": "extracted"}],
            "sections": {key: ["C1"] for key in SECTION_KEYS},
            "assessment": {"instrument": "Instrumento sintético de teste", "version": "fixture-1",
                           "status": "complete", "coverage": {"expected_ids": ["SYNTHETIC-D1"],
                           "answered_ids": ["SYNTHETIC-D1"]}, "items": [{"id": "SYNTHETIC-D1", "domain": "Domínio sintético",
                           "judgment": "Não informado", "reason": "Fonte exclusivamente sintética.",
                           "evidence_ids": ["E1"]}]},
            "human_review": {"status": "pending", "reviewer": "", "notes": "Revisão humana posterior."},
        }
        self.record_path = self.root / "record.json"

    def cli(self, *args):
        self.record_path.write_text(json.dumps(self.record, ensure_ascii=False), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), *args], text=True,
                              capture_output=True, cwd=self.root)

    def validate(self):
        return self.cli("validate", str(self.record_path))

    def test_valid_synthetic_record_with_known_quote(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Registro válido: SYNTHETIC-ONLY", result.stdout)

    def test_quotes_must_exist_in_the_declared_source(self):
        for quote in ("Citação inventada", QUOTE.lower()):
            with self.subTest(quote=quote):
                self.record["evidence"][0]["quote"] = quote
                result = self.validate()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("quote", result.stderr)
        (self.root / "other.txt").write_text("SYNTHETIC: outra fonte.", encoding="utf-8")
        self.record["sources"].append({"id": "S2", "label": "Outra fonte sintética",
                                       "kind": "other", "path": "other.txt"})
        self.record["evidence"][0].update(quote=QUOTE, source_id="S2")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("quote", result.stderr)

    def test_quote_whitespace_normalization_preserves_case(self):
        self.record["evidence"][0]["quote"] = QUOTE.replace(" ", " \n\t ")
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sections_must_be_complete_nonempty_claim_references(self):
        original = self.record["sections"]
        for key in SECTION_KEYS:
            for mode in ("missing", "empty", "unknown_claim", "string"):
                with self.subTest(section=key, mode=mode):
                    self.record["sections"] = dict(original)
                    if mode == "missing":
                        del self.record["sections"][key]
                    else:
                        self.record["sections"][key] = {"empty": [], "unknown_claim": ["C999"],
                                                        "string": "C1"}[mode]
                    result = self.validate()
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("sections", result.stderr)

    def test_claims_require_unique_ids_text_kind_and_evidence(self):
        original = self.record["claims"][0]
        for field, value in (("evidence_ids", []), ("evidence_ids", ["E999"]),
                             ("evidence_ids", ["E1", "E1"]), ("text", " "),
                             ("kind", "opinion"), ("id", "")):
            self.record["claims"] = [dict(original, **{field: value})]
            result = self.validate()
            self.assertEqual(result.returncode, 2, (field, result.stderr))
            self.assertIn("claims", result.stderr)
        self.record["claims"] = [original, original]
        self.assertEqual(self.validate().returncode, 2)
        self.record["claims"] = []
        self.assertEqual(self.validate().returncode, 2)

    def test_root_article_source_and_evidence_contract(self):
        original = copy.deepcopy(self.record)
        for area in ("root", "article", "sources", "evidence"):
            target = original if area == "root" else original[area]
            if isinstance(target, list):
                target = target[0]
            for key in target:
                self.record = copy.deepcopy(original)
                altered = self.record if area == "root" else self.record[area]
                if isinstance(altered, list):
                    altered = altered[0]
                del altered[key]
                result = self.validate()
                self.assertEqual(result.returncode, 2, (area, key, result.stderr))
                self.assertNotIn("Traceback", result.stderr)
        for area, key, value in (("article", "title", ""), ("sources", "label", ""),
                                  ("sources", "kind", "pdf"), ("evidence", "locator", ""),
                                  ("evidence", "quote", " "), ("evidence", "source_id", "S999")):
            self.record = copy.deepcopy(original)
            target = self.record[area]
            if isinstance(target, list):
                target = target[0]
            target[key] = value
            self.assertEqual(self.validate().returncode, 2, (area, key))
        for area in ("sources", "evidence"):
            self.record = copy.deepcopy(original)
            self.record[area] *= 2
            self.assertEqual(self.validate().returncode, 2, area)

    def test_sources_are_regular_local_utf8_text_only(self):
        (self.root / "binary.txt").write_bytes(QUOTE.encode("utf-8") + b"\x00")
        (self.root / "https:synthetic.txt").write_text(QUOTE, encoding="utf-8")
        (self.root / "source.pdf").write_text(QUOTE, encoding="utf-8")
        (self.root / "invalid.txt").write_bytes(b"\xff" + QUOTE.encode("utf-8"))
        for path in ("binary.txt", "https:synthetic.txt", "source.pdf", "invalid.txt",
                     "https://invalid.example/source.txt", "missing.txt", "."):
            self.record["sources"][0]["path"] = path
            result = self.validate()
            self.assertEqual(result.returncode, 2, (path, result.stderr))
            self.assertNotIn("Traceback", result.stderr)

    def test_scope_requires_protocol_for_any_eligibility_verdict(self):
        original = copy.deepcopy(self.record["scope"])
        for status in ("eligible", "ineligible", "uncertain"):
            self.record["scope"] = dict(original, status=status)
            result = self.validate()
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("protocol_version", result.stderr)
        self.record["scope"] = dict(original, protocol_version="Protocolo sintético v1")
        self.assertEqual(self.validate().returncode, 2)
        for field, value in (("status", "approved"), ("reason", ""),
                             ("protocol_version", None), ("criteria", None)):
            self.record["scope"] = dict(original, **{field: value})
            self.assertEqual(self.validate().returncode, 2, field)
        for field in original:
            self.record["scope"] = dict(original)
            del self.record["scope"][field]
            self.assertEqual(self.validate().returncode, 2, field)

    def test_scope_verdict_must_match_sourced_criteria(self):
        scope = self.record["scope"]
        scope.update(status="eligible", protocol_version="SYNTHETIC-P1")
        self.assertEqual(self.validate().returncode, 2)
        criterion = {"criterion": "Critério exclusivamente sintético", "status": "met", "evidence_ids": ["E1"]}
        scope["criteria"] = [criterion]
        for verdict in ("eligible", "ineligible", "uncertain"):
            for decision in ("met", "not_met", "uncertain"):
                scope["status"], criterion["status"] = verdict, decision
                expected = 0 if (verdict, decision) in (("eligible", "met"),
                    ("ineligible", "not_met"), ("uncertain", "uncertain")) else 2
                self.assertEqual(self.validate().returncode, expected, (verdict, decision))
        scope["status"], criterion["status"] = "eligible", "met"
        for field, value in (("criterion", ""), ("status", "approved"), ("evidence_ids", []),
                             ("evidence_ids", ["E999"])):
            scope["criteria"] = [dict(criterion, **{field: value})]
            self.assertEqual(self.validate().returncode, 2, field)
        scope["criteria"] = [criterion, criterion]
        self.assertEqual(self.validate().returncode, 2)
        scope.update(status="undefined", protocol_version="", criteria=[criterion])
        self.assertEqual(self.validate().returncode, 2)

    def test_complete_assessment_requires_cited_full_text(self):
        self.record["sources"][0]["kind"] = "abstract"
        result = self.validate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("full_text", result.stderr)
        self.record["sources"].append({"id": "S2", "label": "Texto sintético não citado",
                                       "kind": "full_text", "path": "synthetic.txt"})
        self.assertEqual(self.validate().returncode, 2)
        self.record["assessment"]["status"] = "limited"
        self.assertEqual(self.validate().returncode, 0)
        self.record["assessment"]["status"] = "invented"
        self.assertEqual(self.validate().returncode, 2)

    def test_methodological_judgments_require_reasons_and_sources(self):
        original = copy.deepcopy(self.record["assessment"])
        for field, value in (("judgment", ""), ("reason", ""), ("domain", ""), ("id", ""),
                             ("evidence_ids", []), ("evidence_ids", ["E999"])):
            self.record["assessment"] = copy.deepcopy(original)
            self.record["assessment"]["items"][0][field] = value
            result = self.validate()
            self.assertEqual(result.returncode, 2, field)
            self.assertNotIn("Traceback", result.stderr)
        for field in ("instrument", "version", "items"):
            self.record["assessment"] = copy.deepcopy(original)
            self.record["assessment"][field] = [] if field == "items" else ""
            self.assertEqual(self.validate().returncode, 2, field)
        self.record["assessment"] = copy.deepcopy(original)
        self.record["assessment"]["items"] *= 2
        self.assertEqual(self.validate().returncode, 2)
        self.record["assessment"] = copy.deepcopy(original)
        self.record["assessment"].update(status="not_applicable")
        self.assertEqual(self.validate().returncode, 0)
        self.record["assessment"]["items"][0]["reason"] = ""
        self.assertEqual(self.validate().returncode, 2)

    def test_complete_assessment_requires_exact_official_inventory_coverage(self):
        original = copy.deepcopy(self.record["assessment"])
        del self.record["assessment"]["coverage"]
        result = self.validate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("coverage", result.stderr)
        for coverage in ({}, {"expected_ids": [], "answered_ids": []},
                         {"expected_ids": ["SYNTHETIC-D1", "SYNTHETIC-D2"], "answered_ids": ["SYNTHETIC-D1"]},
                         {"expected_ids": ["SYNTHETIC-D1"], "answered_ids": ["SYNTHETIC-D2"]},
                         {"expected_ids": ["SYNTHETIC-D1"] * 2, "answered_ids": ["SYNTHETIC-D1"]},
                         {"expected_ids": ["SYNTHETIC-D1"], "answered_ids": ["SYNTHETIC-D1"] * 2}):
            self.record["assessment"] = dict(original, coverage=coverage)
            self.assertEqual(self.validate().returncode, 2, coverage)
        self.record["assessment"] = copy.deepcopy(original)
        self.record["assessment"].update(status="limited")
        self.record["assessment"]["coverage"]["expected_ids"].append("SYNTHETIC-D2")
        self.assertEqual(self.validate().returncode, 0)
        del self.record["assessment"]["coverage"]
        self.assertEqual(self.validate().returncode, 0)

    def test_reviewed_status_requires_named_reviewer(self):
        review = self.record["human_review"]
        review["status"] = "reviewed"
        self.assertEqual(self.validate().returncode, 2)
        review["reviewer"] = "Revisor sintético de teste"
        self.assertEqual(self.validate().returncode, 0)
        for field, value in (("status", "approved"), ("reviewer", None), ("notes", [])):
            original = copy.deepcopy(review)
            review[field] = value
            self.assertEqual(self.validate().returncode, 2, field)
            review.clear()
            review.update(original)
        for field in tuple(review):
            value = review.pop(field)
            self.assertEqual(self.validate().returncode, 2, field)
            review[field] = value

    def test_generated_documents_identify_ai_authorship(self):
        prefix = self.root / "ai-authorship"
        result = self.cli("render", str(self.record_path), "--output-prefix", str(prefix))
        self.assertEqual(result.returncode, 0, result.stderr)
        for suffix in (".md", ".html"):
            content = Path(str(prefix) + suffix).read_text(encoding="utf-8")
            self.assertIn("Análise elaborada por agente de IA.", content)
            self.assertIn("Revisão humana: pendente", content)

    def test_cli_render_writes_complete_final_format_with_pending_footnote(self):
        prefix = self.root / "reports" / "SYNTHETIC-ONLY"
        result = self.cli("render", str(self.record_path), "--output-prefix", str(prefix))
        self.assertEqual(result.returncode, 0, result.stderr)
        for suffix in (".md", ".html"):
            content = Path(str(prefix) + suffix).read_text(encoding="utf-8")
            for heading in ("Resumo executivo", "Métodos", "Intervenção / exposição", "Resultados",
                            "Avaliação estatística", "Avaliação metodológica", "Relevância clínica", "Segurança",
                            "Conclusão dos autores", "Conclusão independente", "Limitações", "Elegibilidade",
                            "Julgamentos metodológicos", "Registro de evidências", "Fontes consultadas"):
                self.assertIn(heading, content)
            for value in ("C1", "E1", "S1", QUOTE, "Linha 1", "synthetic.txt", "SYNTHETIC-D1",
                          "Instrumento sintético de teste", "fixture-1", "undefined", "Não informado"):
                self.assertIn(value, content)
            self.assertIn("Revisão humana: pendente", content)
            self.assertNotIn("rascunho", content.lower())
            self.assertNotIn("draft", content.lower())
            self.assertNotIn("PREENCHER", content)
        html = Path(str(prefix) + ".html").read_text(encoding="utf-8")
        self.assertIn('<html lang="pt-BR">', html)
        self.assertIn('<footer>Revisão humana: pendente</footer>', html)
        self.assertIn('<table>', html)

    def test_render_escapes_all_untrusted_html_and_markdown(self):
        payload = '<svg onload="x">&\' | *bold* [x](https://invalid.example)\n## injected'
        for key in self.record["article"]:
            self.record["article"][key] += payload
        self.record["scope"].update(status="eligible", protocol_version="SYNTHETIC-P1" + payload,
            reason=payload, criteria=[{"criterion": payload, "status": "met", "evidence_ids": ["E1"]}])
        self.record["sources"][0]["label"] = payload
        self.record["evidence"][0]["locator"] = payload
        self.record["evidence"][0]["quote"] = payload
        (self.root / "synthetic.txt").write_text(payload, encoding="utf-8")
        self.record["claims"][0]["text"] = payload
        for key in ("instrument", "version"):
            self.record["assessment"][key] = payload
        for key in ("domain", "judgment", "reason"):
            self.record["assessment"]["items"][0][key] = payload
        self.record["human_review"].update(status="reviewed", reviewer=payload, notes=payload)
        prefix = self.root / "escaped"
        result = self.cli("render", str(self.record_path), "--output-prefix", str(prefix))
        self.assertEqual(result.returncode, 0, result.stderr)
        html = prefix.with_suffix(".html").read_text(encoding="utf-8")
        self.assertNotIn('<svg', html)
        self.assertIn('&lt;svg onload=&quot;x&quot;&gt;&amp;&#x27;', html)
        self.assertNotIn('src=', html)
        md = prefix.with_suffix(".md").read_text(encoding="utf-8")
        self.assertNotIn('<svg', md)
        self.assertIn(r'\| \*bold\* \[x\]', md)

    def test_valid_records_cannot_contain_template_placeholders(self):
        original = copy.deepcopy(self.record)
        for area, field, value in (("article", "title", "TODO"),
                                  ("claims", "text", "PREENCHER: síntese baseada nas fontes"),
                                  ("assessment", "instrument", "[A PREENCHER]"),
                                  ("human_review", "notes", "TBD")):
            self.record = copy.deepcopy(original)
            target = self.record[area][0] if area == "claims" else self.record[area]
            target[field] = value
            result = self.validate()
            self.assertEqual(result.returncode, 2, field)
            self.assertIn("placeholder", result.stderr)

    def test_render_never_overwrites_supplied_evidence(self):
        protected = self.root / "protected.md"
        protected.write_text(QUOTE, encoding="utf-8")
        self.record["sources"][0]["path"] = protected.name
        result = self.cli("render", str(self.record_path), "--output-prefix", str(protected.with_suffix("")))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(protected.read_text(encoding="utf-8"), QUOTE)
        self.assertFalse(protected.with_suffix(".html").exists())
        self.assertIn("entrada", result.stderr)

    def test_duplicate_json_fields_are_rejected_not_silently_overwritten(self):
        text = json.dumps(self.record, ensure_ascii=False)
        self.record_path.write_text('{"article": {}, ' + text[1:], encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "validate", str(self.record_path)],
                                text=True, capture_output=True, cwd=self.root)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicada", result.stderr)

    def test_abstract_only_report_explicitly_describes_source_limit(self):
        self.record["sources"][0]["kind"] = "abstract"
        self.record["assessment"]["status"] = "limited"
        del self.record["assessment"]["coverage"]
        self.record["claims"][0].update(text="Não informado no resumo sintético consultado.", kind="interpretation")
        prefix = self.root / "abstract-only"
        result = self.cli("render", str(self.record_path), "--output-prefix", str(prefix))
        self.assertEqual(result.returncode, 0, result.stderr)
        html = prefix.with_suffix(".html").read_text(encoding="utf-8")
        for text in ("Texto completo não fornecido", "Resumo (abstract)", "Referência bibliográfica",
                     "Limitada", "cobertura não verificada", "Não informado no resumo sintético consultado.",
                     "Interpretação", "Revisão humana: pendente", "undefined"):
            self.assertIn(text, html)


if __name__ == "__main__":
    unittest.main()
