# Instalação — instruções para o agente

**Público executor: agente de IA com leitura de arquivos e execução local autorizada.** O humano pode fornecer só o link e o pedido “instale esta skill”. Se você só dispõe de chat, não afirme instalação: informe a falta de ferramentas. Não peça ao humano para implementar scripts que já estão neste pacote.

## 1. Obter e inspecionar

Use suas ferramentas para escolher uma pasta de trabalho nova e clonar:

```text
git clone https://github.com/cledsonsantana/SkillBorisCledson.git
```

Entre na pasta clonada, leia AGENTS.md, este arquivo, o instalador e o SKILL.md. Registre `git rev-parse HEAD`. A URL e o commit inspecionado definem a origem; o check de hashes posterior não substitui confiança no código de origem. Se Git não estiver disponível, obtenha o arquivo-fonte por meios autorizados e inspecione-o antes de executar; não instale dependências de sistema silenciosamente.

Identifique o interpretador Python disponível e confirme versão >=3.10. Os exemplos abaixo usam `python3`; adapte para um interpretador **verificado** do host, como `py -3` no Windows. Não troque apenas o nome do comando sem checar.

## 2. Identificar destino — não adivinhar

Escolha o agente pelo contexto real da sessão. Se for ambíguo, faça uma única pergunta curta. O instalador exige escolha explícita:

- **Hermes:** `--agent hermes`. Usa `$HERMES_HOME/skills/scientific-article-appraisal` se HERMES_HOME estiver definido; caso contrário, a pasta `.hermes/skills/scientific-article-appraisal` do usuário atual. Para perfil ativo, confirme que HERMES_HOME aponta para o perfil autorizado. Não instale em outro perfil.
- **Codex:** `--agent codex`. Usa a pasta pessoal `.agents/skills/scientific-article-appraisal`. Não assume a pasta legada `.codex/skills`.
- **Claude Code:** `--agent claude`. Usa a pasta pessoal `.claude/skills/scientific-article-appraisal`.
- **Outro agente, escopo de projeto ou diretório personalizado:** confirme o local na documentação/configuração do host e use `--target-dir CAMINHO`. Esse caminho é a **pasta final** `scientific-article-appraisal`, não a pasta pai. Não combine com `--agent`.

As convenções de destino são adaptadores de arquivos. Copiar a pasta não instala um plugin, não habilita conectores e não prova reconhecimento por toda versão de cada produto. Para ferramentas sem suporte a skills, o agente pode ler o SKILL.md diretamente, declarando essa diferença.

## 3. Conferir antes da escrita

Execute os testes a partir da raiz do clone:

```text
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s skills/scientific-article-appraisal/scripts -p 'test_appraisal*.py' -v
python3 scripts/install_skill.py --agent hermes --dry-run
```

Troque `hermes` pela escolha confirmada. Para destino explícito, troque a opção inteira por `--target-dir CAMINHO`. Dry-run não deve criar diretórios nem modificar arquivos. Se os testes falharem, investigue antes de instalar; não remova os testes para ocultar o erro.

## 4. Instalar e verificar

```text
python3 scripts/install_skill.py --agent hermes
python3 scripts/install_skill.py --agent hermes --check
```

Interprete o JSON e o código de saída, não apenas a ausência de mensagem no terminal. Um destino idêntico é reutilizado; uma versão diferente/customizada é recusada. Se o humano autorizar substituição, use `--replace`, preserve o backup retornado e repita o check. Não use `--replace` por padrão.

O instalador só copia a árvore da skill; não muda chaves, modelos, arquivos globais AGENTS/CLAUDE, contas Google, diretórios de outros agentes ou documentos do usuário. Links simbólicos, junções e outros reparse points são recusados por segurança; escolha um destino físico autorizado em vez de contornar a proteção. Atualizações são explícitas, pelo mesmo processo de inspeção/check/backup.

## 5. Smoke test instalado

Com o **caminho real** retornado pelo instalador, use o helper instalado e o exemplo do clone:

```text
python3 CAMINHO_DA_SKILL/scripts/appraisal_report.py validate examples/synthetic/record.json
python3 CAMINHO_DA_SKILL/scripts/appraisal_report.py render examples/synthetic/record.json --output-prefix DIRETORIO_TEMPORARIO/demo
```

Crie o diretório temporário com as ferramentas do host. Verifique que os arquivos `.md` e `.html` existem, identificam a natureza sintética e mantêm revisão humana pendente. Não grave saídas sobre fontes, scripts ou o próprio registro. Esse teste demonstra execução técnica, não análise científica real nem diagramação final de PDF/Google Docs.

## 6. Confirmar descoberta nativa

No Hermes, consulte a lista de skills no perfil escolhido; confirme o nome `scientific-article-appraisal`. A lista/contexto pode exigir uma nova sessão. Não use reset nem invalidação do cache sem autorização. Em Codex e Claude, consulte a descoberta de skills oferecida pelo host e, se necessário, informe a necessidade de nova sessão. Se só foi possível verificar os arquivos, diga **arquivos instalados e verificados; descoberta nativa não confirmada**.

## 7. Adaptar e entregar

Leia `examples/adaptation.example.json` como exemplo de preferências para o agente; **não é um arquivo de configuração consumido automaticamente pelo instalador/helper**. Registre preferências fora da pasta instalada ou em uma cópia de trabalho, com autorização, para evitar perdê-las em atualizações. Ausência de protocolo não autoriza criar critérios de inclusão.

Conectores PDF/Word/Google Docs são opcionais e dependem do host. Não exija as contas do autor nem prometa produzir Google Docs sem integração autorizada. Consulte `references/agent-capabilities.md` na skill. Instalar não autoriza ler qualquer pasta, analisar dados de pacientes, enviar documentos ou publicar conteúdo.

Encerre com versão/commit, agente e destino, check de integridade, resultados dos testes/smoke, backup se houver e limitações reais. O humano recebe o resultado, não uma lista de comandos ainda por executar.

## Fontes das convenções

- [Hermes](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills)
- [Codex](https://developers.openai.com/codex/skills)
- [Claude Code](https://code.claude.com/docs/en/skills)
- [Formato Agent Skills](https://agentskills.io/specification)

Revalide essas convenções quando houver mudança do host; não confunda documentação consultada com compatibilidade executada em todas as plataformas.
