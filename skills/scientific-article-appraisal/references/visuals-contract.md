# Ilustrações opcionais — contrato do relatório

Extensão opcional do contrato de `structured-record.md`, com testes exclusivamente sintéticos. O helper não modifica artigos nem publica no Drive. Usa apenas biblioteca padrão, sem Pillow, rede ou APIs. As ilustrações complementam a análise humana/IA existente; o helper não seleciona, recorta, interpreta nem cria imagens científicas.

## JSON

O objeto raiz mantém os oito campos obrigatórios originais e aceita somente mais um campo opcional: `visuals`. Omitir `visuals` ou usar `[]` preserva a saída original, inclusive autoria, todas as seções e o rodapé de revisão humana. Quando presente, `visuals` deve ser uma lista. Cada entrada tem **exatamente**:

```text
{id, kind, source_id, source_page, label, path, sha256,
 caption, analysis, evidence_ids, section}
```

| Campo | Regra |
| --- | --- |
| `id` | String não vazia, única dentro de `visuals`; preservada sem normalização. |
| `kind` | Exatamente `article_header`, `figure` ou `table`. No máximo um `article_header`. |
| `source_id` | ID existente em `sources`, cuja fonte declarada tenha `kind: "full_text"`. Resumo, suplemento ou registro isolado não satisfazem essa exigência. |
| `source_page` | Inteiro positivo, iniciando em 1. Booleanos, strings e números fracionários não são aceitos. Registrar a página efetivamente usada; o helper não confere o PDF. |
| `label` | Texto não vazio com o rótulo nativo do artigo, por exemplo o identificador da figura/tabela. Para cabeçalho, identificar o cabeçalho original, sem inventar numeração de figura. |
| `path` | Arquivo PNG local existente, com caminho **relativo à pasta do JSON**. Extensão `.png` sem distinção de caixa. Não aceita URL/esquema, `:`, caminho absoluto/UNC, barras invertidas, NUL nem qualquer componente `..`. Links simbólicos são aceitos somente se o destino resolvido permanecer dentro da base do registro. |
| `sha256` | Exatamente 64 caracteres hexadecimais minúsculos. Deve corresponder a `hashlib.sha256(bytes_originais).hexdigest()`. Não há correção automática de caixa ou digest. |
| `caption` | Legenda descritiva não vazia: explicar o que está reproduzido e seu contexto. Não usar apenas “imagem” ou decoração. |
| `analysis` | Justificativa analítica não vazia: explicar por que a imagem é útil para a seção e a interpretação crítica. Não substituir a análise do relatório por uma ilustração. |
| `evidence_ids` | Lista não vazia, sem duplicatas, de IDs existentes em `evidence`. Não são IDs de fontes. |
| `section` | Uma chave nativa de `SECTIONS`; para `article_header`, obrigatoriamente `executive_summary`. Não aceita títulos traduzidos nem novas seções. |

Seções nativas: `executive_summary`, `methods`, `intervention`, `results`, `statistical_appraisal`, `methodological_appraisal`, `clinical_relevance`, `safety`, `authors_conclusion`, `independent_conclusion`, `limitations`.

Todos os campos de texto obrigatórios são conferidos quanto a tipo/preenchimento, e os marcadores de template continuam proibidos. Verifique a qualidade descritiva da legenda e a utilidade analítica e explicite-as para revisão humana; **esses aspectos não são critérios semânticos certificados pelo programa**. Campos extras, inclusive escores, são recusados.

### Conferência técnica do arquivo

O validador lê os bytes locais, exige a assinatura PNG de oito bytes, pelo menos 33 bytes, primeiro chunk `IHDR` com comprimento declarado 13 e largura/altura positivas. Confere o SHA-256 calculado dos bytes completos, não só do cabeçalho.

Essa é uma verificação **mínima de formato e integridade declarada**, não um decodificador completo de PNG: não valida CRC, todos os chunks, descompressão, conteúdo dos pixels ou renderização por todos os leitores. Não certifica autenticidade, fidelidade do recorte, correspondência ao PDF/página, integridade de eixos/notas/legendas, privacidade, direitos de reprodução, pertinência das evidências nem significado médico. Um hash válido não prova proveniência científica. Conferir visualmente recortes, unidades e contexto antes de publicar.

## Renderização

- O `article_header` aparece no início do corpo, **antes do h1 principal**, independentemente de sua posição na lista. Não é repetido no resumo executivo.
- Figuras e tabelas aparecem imediatamente após todos os parágrafos da seção indicada e antes da próxima seção. Múltiplas ilustrações de uma seção preservam a ordem da lista.
- Cada ilustração inclui imagem, rótulo nativo + legenda, ID/nome da fonte, página, referências às evidências e análise de utilidade. Não é uma imagem decorativa isolada.
- HTML: `<figure>`, `<img>` com os bytes originais em `data:image/png;base64,...`, legenda e parágrafos. Nenhum download, script, fonte remota ou recurso de rede é acrescentado. Todos os textos e atributos textuais são escapados.
- Markdown: link relativo ao PNG local, com caracteres especiais percent-encoded; legenda, proveniência e análise são preservadas como texto escapado. Não é autocontido: manter os arquivos no caminho apontado. Somente o HTML incorpora a imagem.
- Autoria, texto original, ausência de pontuações agregadas e rodapé humano não são alterados. Não é acrescentado selo de validação científica ou revisão humana.

## API e CLI

```python
validate(record, base)  # base: pathlib.Path da pasta do JSON
markdown, html = render(record, base=Path("."), output_base=None)
```

`render(record)` continua compatível para registros sem ilustrações. A função pressupõe registro já validado, com a **mesma base e arquivos inalterados**; não é fronteira de validação para dados arbitrários. Para ilustrações, `base` resolve a leitura dos PNGs; o padrão `Path('.')` usa o diretório atual. `output_base`, somente por palavra-chave, determina a pasta relativa dos links Markdown; quando omitido, os links são relativos a `base`.

```sh
python3 scripts/appraisal_report.py validate /pasta/record.json
python3 scripts/appraisal_report.py render /pasta/record.json --output-prefix /saida/relatorio
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

A CLI valida primeiro; fontes e imagens são resolvidas a partir da pasta do JSON, não do diretório de execução. `--output-prefix` continua relativo ao diretório de execução quando não absoluto. Os links Markdown são recalculados relativamente à pasta de saída, podendo conter `../` **gerado pelo renderer** para alcançar os arquivos de entrada; isso não permite traversal no `visuals.path` recebido. Colisões das saídas resolvidas com JSON, fontes ou PNGs são recusadas, inclusive através de symlink. Nenhum arquivo de imagem é copiado ou regravado. Permanecem as regras originais de sobrescrita de relatórios e escrita não atômica da dupla Markdown/HTML.

## Verificação

A suíte reúne os 20 testes originais e dez testes de ilustrações. Execute `python3 -m unittest discover -s scripts -p 'test_appraisal*.py' -v`. A validação estrutural não certifica fidelidade do recorte nem interpretação científica. Preserve os ativos PNG ao entregar Markdown; para incorporação em documento externo privado, siga `visual-evidence.md` e verifique as capacidades do host em `agent-capabilities.md`.
