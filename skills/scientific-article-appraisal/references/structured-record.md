# Gerador local de análise crítica — contrato v1

Helper local instalado nesta skill. Requer somente Python 3.10+ (biblioteca padrão). Não requer integração externa. Produza Markdown e HTML pt-BR locais a partir de um registro preenchido. Trate-os como artefatos de análise, não como documento final paginado de três camadas. Exportação para Word/Google Docs/PDF e verificação de layout, justificação e permissões dependem de capacidades opcionais do host; consulte `agent-capabilities.md`. Não envia documentos nem acessa contas, credenciais, rede, APIs ou formulários oficiais.

**Limite indispensável:** “Registro válido” significa conformidade estrutural, referências internas consistentes e presença literal das citações no arquivo de fonte declarado. **Não certifica correção médica, correspondência entre afirmação e citação, classificação correta do desenho/fonte, fidelidade ao checklist oficial, algoritmos nativos, autenticidade da fonte, localização da citação, versão vigente ou adequação do instrumento.** Verifique esses aspectos independentemente no original e registre limites para a revisão humana. Correspondência literal com uma transcrição local inexata não certifica fidelidade ao PDF. O script não calcula estatísticas nem escores, não agrega instrumentos e não inventa dados.

## Uso

```sh
python3 scripts/appraisal_report.py validate caminho/record.json
python3 scripts/appraisal_report.py render caminho/record.json --output-prefix saida/artigo
python3 -m unittest discover -s scripts -v
```

- `validate`: saída 0 se o contrato for atendido; saída 2 e mensagem em stderr se não for. Não escreve relatórios.
- `render`: valida primeiro e escreve `saida/artigo.md` e `saida/artigo.html`, em UTF-8. Cria diretórios necessários. O sufixo é **acrescentado** ao prefixo, não substituído. Não escreve relatório de registro inválido. É obrigatório fornecer `--output-prefix` para renderizar.
- O prefixo é relativo ao diretório de execução. Fontes relativas são resolvidas a partir do diretório do JSON, não do diretório de execução. Caminhos absolutos locais também são aceitos.
- Relatórios existentes no mesmo prefixo são sobrescritos. Colisões com caminhos resolvidos do JSON e das fontes são recusadas. Use uma pasta de saída dedicada; a dupla de arquivos não constitui uma transação atômica se houver erro de disco/permissão durante a escrita.
- O módulo também oferece `validate(record, base: pathlib.Path)` e `render(record) -> (markdown, html)`. A função `render` pressupõe registro já validado; prefira a CLI para impor a validação. Para imagens, consulte a assinatura ampliada em `visuals-contract.md`.

## Modelo em branco versus registro utilizável

`templates/appraisal-record.json` é **um modelo instrucional propositalmente inválido**, não uma análise. Cada `PREENCHER:` explica o conteúdo esperado, sem inventar fatos clínicos. Substitua todos os marcadores, expanda evidências, afirmações, critérios e itens conforme as fontes; não mantenha uma única evidência genérica para tudo. Os IDs iniciais de afirmações são referências de organização, não IDs oficiais de instrumentos.

O validador recusa os marcadores convencionados `PREENCHER:`, `TODO:`, `TBD:`, `[A PREENCHER]` no início de strings e as strings inteiras `TODO`, `TBD`, `...`, `A PREENCHER`. Não detecta automaticamente toda formulação possível de lacuna disfarçada. Um registro real deve estar integralmente preenchido, com julgamentos justificados, sem instruções de preenchimento, e nunca ser apresentado como clinicamente validado por este programa.

Os testes usam exclusivamente documentos explicitamente **SYNTHETIC**, instrumentos e IDs declaradamente sintéticos, sem resultados clínicos. As fontes temporárias geradas pela suíte são demonstrações sintéticas — não avaliações de artigos reais nem modelos oficiais.

## Contrato JSON explícito

Todos os campos abaixo são obrigatórios e objetos rejeitam campos extras, exceto `assessment.coverage`, opcional nas condições indicadas. Chaves JSON duplicadas são recusadas. Strings devem ser não vazias após remover espaços para testar preenchimento, sem alterar o valor; exceções: `scope.protocol_version` com escopo indefinido e `human_review.reviewer`/`notes` quando permitido abaixo. Identificadores são strings literais, únicas dentro de sua coleção; não são corrigidos, convertidos em minúsculas ou normalizados.

### `article`

`{id, title, reference, design}`: quatro strings. `id` preserva o identificador estável do acervo; `title` identifica o artigo; `reference` registra a referência bibliográfica; `design` descreve o desenho efetivamente identificado. Não é uma classificação automática.

### `sources`

Lista não vazia de `{id, label, kind, path}`:

- `id`: identificador usado por `evidence.source_id`.
- `label`: descrição/proveniência do documento efetivamente lido.
- `kind`: exatamente `full_text`, `abstract`, `supplement`, `registry` ou `other`.
- `path`: arquivo regular local UTF-8 `.txt`, `.text` ou `.md`. URLs, esquemas de URI, caminhos com `:`, caminhos iniciados com `//`, diretórios e conteúdo com caracteres de controle binários são recusados. Não lê PDFs, DOCX, HTML ou imagens diretamente; forneça previamente a transcrição textual local, com proveniência em `label` e localizadores claros.

O tipo declarado não é inferido do conteúdo. Nunca reclassifique um resumo como `full_text` para contornar a regra de avaliação completa. A existência do arquivo não demonstra sua autenticidade.

### `evidence`

Lista não vazia de `{id, source_id, locator, quote}`:

- `source_id` deve identificar uma fonte existente.
- `locator` é obrigatório: página, seção, tabela, parágrafo ou linha que permita localizar o trecho. O script o preserva, mas **não verifica o localizador**.
- `quote` é um trecho literal não vazio. Após normalizar somente sequências de espaços/brancos, deve ocorrer no texto da **fonte específica indicada**. A comparação é sensível a maiúsculas, acentos e pontuação. Não procura a citação em outra fonte para compensar proveniência errada.

### `claims`

Lista não vazia de `{id, text, evidence_ids, kind}`:

- `text`: afirmação preenchida, sem marcador de modelo.
- `kind`: `extracted` (extração) ou `interpretation` (interpretação independente).
- `evidence_ids`: lista não vazia, sem repetições, de IDs existentes em `evidence`. Ambos os tipos de afirmação precisam de apoio rastreável.

`evidence_ids` referencia **evidências**, não fontes diretamente: a cadeia é `claim → evidence → source → arquivo local`. A mera existência dessa cadeia não prova que o trecho sustenta a afirmação.

**Dados indisponíveis:** registre explicitamente no texto, por exemplo, “Não informado no resumo consultado”, e cite o trecho/localizador do material efetivamente examinado que contextualiza essa limitação. Ausência de informação não é zero, ausência de evento ou ausência de procedimento. Não invente estimativas, denominadores, intervalos, números ou citações para preencher a lacuna. Uma citação não pode provar, sozinha, a ausência global de informação; a adequação dessa conclusão exige apreciação humana. `Não informado` não é placeholder: é uma afirmação específica que também precisa de fonte e contexto.

### `sections`

Objeto com **exatamente** estas chaves, cada uma contendo lista não vazia e sem repetições de IDs existentes em `claims`:

| Chave | Seção no relatório |
| --- | --- |
| `executive_summary` | Resumo executivo |
| `methods` | Métodos |
| `intervention` | Intervenção / exposição |
| `results` | Resultados |
| `statistical_appraisal` | Avaliação estatística |
| `methodological_appraisal` | Avaliação metodológica |
| `clinical_relevance` | Relevância clínica |
| `safety` | Segurança |
| `authors_conclusion` | Conclusão dos autores |
| `independent_conclusion` | Conclusão independente |
| `limitations` | Limitações |

Uma afirmação pode ser reutilizada onde justificado. A conclusão dos autores e a independente são seções distintas. O programa não avalia a qualidade da síntese ou a cobertura semântica de cada seção.

### `scope`

`{status, protocol_version, reason, criteria}`:

- `status`: `eligible`, `ineligible`, `uncertain` ou `undefined`.
- `protocol_version`: string não vazia para qualquer decisão definida, inclusive `uncertain`. Sem protocolo, não há aprovação/reprovação de elegibilidade.
- `reason`: justificativa não vazia do estado de escopo; não inserir afirmações clínicas sem sua correspondente afirmação/evidência nas seções.
- `criteria`: lista de `{criterion, status, evidence_ids}`; `criterion` é descrição não vazia e não repetida; `status` é `met`, `not_met` ou `uncertain`; `evidence_ids` segue a regra das afirmações.

**Coerência determinística:** um `not_met` exige `ineligible`; sem `not_met`, qualquer `uncertain` exige `uncertain`; somente `met` exige `eligible`. Estados definidos exigem pelo menos um critério. Os critérios devem ser requisitos de inclusão já orientados positivamente: “não apresenta condição de exclusão”, por exemplo. Não use `met` para indicar que uma condição excludente está presente. O script não interpreta a redação nativa de critérios.

**Sem escopo formal:** use `status: "undefined"`, `protocol_version: ""`, `criteria: []` e motivo explícito. O veredito renderizado será sempre indefinido, sem aprovação de elegibilidade. Não existe campo separado `verdict` que possa contradizer `status`. Esse estado **não impede análise integral baseada nas fontes**, inclusive documento final com revisão humana pendente. O programa rejeita inconsistências em vez de corrigir silenciosamente o registro.

### `assessment`

`{instrument, version, status, items, coverage?}`:

- `instrument`: nome/variante do instrumento selecionado por desenho e objetivo.
- `version`: versão oficial efetivamente consultada; sua vigência deve ser verificada fora deste helper local.
- `status`: `complete`, `limited` ou `not_applicable`.
- `items`: lista não vazia de `{id, domain, judgment, reason, evidence_ids}`. Cada item tem ID único, domínio, julgamento, justificativa não vazia e referências válidas. O julgamento é texto porque categorias e algoritmos pertencem ao instrumento nativo, não a uma escala híbrida deste programa.
- Mesmo `not_applicable` exige pelo menos um item justificado e evidenciado de não aplicabilidade. Não é uma rota para omitir a apreciação.
- **`complete` exige texto completo efetivamente citado em pelo menos um item**, não apenas um arquivo `full_text` não citado na lista. Somente resumos, suplementos ou registros não permitem esse estado.
- Sem texto completo, use `limited` quando aplicável e explicite o que não pôde ser avaliado nos julgamentos e limitações. O relatório registra automaticamente que o texto completo não foi fornecido. Todas as seções continuam presentes, sem uma falsa avaliação metodológica completa.

`coverage`, quando presente, tem exatamente `{expected_ids, answered_ids}`, duas listas não vazias de strings, sem duplicatas:

1. **`expected_ids` deve vir do inventário aplicável do formulário/modelo oficial vigente efetivamente consultado, nunca de itens adivinhados.** O helper não fornece esse inventário, não acessa fonte oficial e não pode verificar sua completude, variante, condicionalidade ou vigência.
2. `answered_ids` deve corresponder exatamente ao conjunto de `items[].id` e ser subconjunto de `expected_ids`.
3. Para `complete`, `coverage` é obrigatória e os três conjuntos devem ser iguais: sem IDs omitidos, extras ou repetidos.
4. Para `limited`/`not_applicable`, `coverage` é opcional. Pode declarar inventário maior que o conjunto respondido. Se o inventário oficial não foi obtido, **omita `coverage`**, não fabrique IDs; isso será transparente no relatório e não permite `complete`.

Igualdade de conjuntos confere somente o inventário declarado. Não certifica a aplicação dos critérios/algoritmos oficiais, julgamentos válidos, instrumento apropriado ou uma avaliação independente completa. Não há campo de pontuação, nota global, soma ou escore híbrido; campos extras de score são rejeitados.

### `human_review`

`{status, reviewer, notes}`:

- `status`: `pending` ou `reviewed`.
- `reviewer`: string; pode ser vazia quando pendente. Para `reviewed`, é obrigatório nome não vazio.
- `notes`: string, pode ser vazia; se preenchida, aparece como metadado de revisão no corpo.

O estado não é promovido automaticamente. Um nome preenchido não comprova identidade ou revisão real. Com pendência, o único rodapé é **“Revisão humana: pendente”**, sem marca d’água ou rótulo de rascunho. Com revisão declarada, o rodapé identifica o revisor. Documento em formato final não equivale a certificação médica.

## Conteúdo e segurança de apresentação

Ambos os formatos incluem todas as seções, IDs/tipo de afirmações e referências a evidências, veredito e critérios de elegibilidade, instrumento/versão, tabela de julgamentos e justificativas, inventário declarado quando disponível, registro de evidências com citações e localizadores, fontes/proveniência/caminhos e metadados humanos. O HTML é autocontido, azul/cinza, com tratamento básico para impressão, sem scripts, fontes remotas ou recursos de rede; PNGs locais opcionais são incorporados. Não há garantia de paginação em três camadas ou justificação editorial no helper. Todos os valores são escapados como texto HTML; Markdown também neutraliza HTML e delimitadores de formatação/tabelas. As saídas não executam nem reinterpretam HTML fornecido nos dados.

## Verificação técnica

Execute a partir da pasta desta skill, com `terminal`: `python3 -m unittest discover -s scripts -p 'test_appraisal_report.py' -v`. A suíte usa fontes sintéticas em diretórios temporários e não acessa o Drive. Conferência técnica não é calibração científica em artigos reais. O helper identifica autoria genérica: `Análise elaborada por agente de IA.` Identifique o agente real na camada editorial ou em metadados de trabalho fora deste esquema estrito; não atribua a análise ao autor da skill ou a uma instituição. Só declare revisão humana após confirmação externa real.


## Ilustrações opcionais
O campo opcional `visuals` conserva o contrato sem imagens. Consulte `visuals-contract.md` para campos, proveniência, arquivos PNG locais, SHA-256 e renderização autocontida. As regras editoriais, ficha 16:9, recortes e publicação privada estão em `visual-evidence.md`.
