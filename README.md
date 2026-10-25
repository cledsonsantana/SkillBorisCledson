# SkillBorisCledson

**Uma skill para agentes de IA produzirem análises críticas rastreáveis e compreensíveis para clínicos.**

Agent-first: o agente faz a instalação e o trabalho técnico; o humano define a pergunta, confere a ciência e toma as decisões. O nome instalado é **`scientific-article-appraisal`**.

## Para instalar, entregue este link ao seu agente

> Instale a skill deste repositório: https://github.com/cledsonsantana/SkillBorisCledson. Leia primeiro AGENTS.md e INSTALL.md, identifique o meu ambiente, inspecione o código, faça o dry-run, instale e verifique. Não sobrescreva adaptações nem configure contas sem minha autorização. Ao final, informe o destino, os testes e qualquer limitação.

**Agente instalador: [comece em AGENTS.md](AGENTS.md) e execute o [roteiro de instalação](INSTALL.md).** Não devolva o roteiro ao humano como se a instalação tivesse sido feita.

## Para quem quer entender

- [Método, etapas e resultado final](docs/METODO.md)
- [Instrumentos metodológicos e suas funções](docs/INSTRUMENTOS.md)
- [Limites, privacidade e segurança](SECURITY.md)
- [Licença e materiais de terceiros](THIRD_PARTY.md)

A análise separa **dados dos autores, conclusão dos autores e interpretação crítica**. O texto mantém o dado técnico e acrescenta significado e consequência clínica próximos dele. Elegibilidade, risco de viés e certeza da evidência são decisões diferentes.

## Resultado pretendido

1. Capa limpa com referência e painel metodológico categórico, respeitando o instrumento; ficha separada reaproveitável em slides quando os direitos permitirem.
2. Síntese objetiva de uma página para apoiar a seleção e a apresentação.
3. Análise integral: métodos, resultados, interpretação estatística/clínica, instrumentos, figuras/tabelas originais pertinentes e anexos com fontes localizáveis.

A saída deve estar preenchida, não ser um formulário para o humano completar. Revisão humana permanece pendente até confirmação real. A avaliação pode sustentar uso favorável, discussão crítica/desfavorável ou não inclusão do artigo — não há aprovação automática de tratamento.

## O que o pacote executa

- Instruções e referências que orientam o agente a ler, extrair, avaliar e explicar.
- Helper Python local para validar registros e gerar Markdown/HTML.
- Instalador explícito com dry-run, check e proteção de adaptações.
- Testes e um exemplo **sintético, sem evidência clínica**.

O helper **não lê o PDF sozinho, não aplica instrumentos automaticamente e não gera por si a diagramação final em três páginas/camadas**. Exportar Word/PDF/Google Docs e conferir a paginação depende das ferramentas autorizadas do agente. Sem isso, ele informa o artefato realmente produzido e sua limitação.

## Compatibilidade e custos de entrada

Python 3.10+ e biblioteca padrão para os scripts: sem `pip`, token ou conta deste projeto. O agente/LLM e eventuais conectores são fornecidos pelo usuário. Há destinos de instalação para Hermes, Codex e Claude Code e um destino explícito para outros hosts. A documentação não promete execução nativa em todo agente ou sistema operacional.

Português é o idioma editorial inicial; o agente adapta idioma, especialidade, escopo e entrega conforme o pedido. Não há instituição, serviço ou população local predefinidos: o contexto-alvo é informado por quem solicita a análise. [Preferências de exemplo](examples/adaptation.example.json) são orientação para o agente, não configuração automática.

## Atualização editorial

A versão 0.7.0 torna obrigatória a revisão clínica integral, acrescenta painéis nativos por instrumento e reforça a auditoria de fontes/resultados de ensaios randomizados. Preserva a identidade real do agente, os comentários e as decisões humanas. Veja o [histórico de mudanças](CHANGELOG.md). O helper e o instalador continuam com o mesmo alcance técnico; não foi acrescentado um avaliador científico automático.

## Estado e autoria

**Versão pública 0.7.0 — experimental.** Testes de código não são validação científica. A apresentação deriva de uma calibração editorial limitada; não anuncia validação geral em todos os desenhos ou equivalência a revisores humanos independentes.

Criado por **Cledson Santana**, com **Boris (agente de IA)** como colaborador. Sem endosso institucional ou dos criadores dos instrumentos.

O conteúdo original está sob [MIT](LICENSE). Artigos, figuras e instrumentos externos mantêm seus próprios direitos e licenças. Nenhum acervo privado ou credencial faz parte deste pacote.

Para melhorias: [CONTRIBUTING.md](CONTRIBUTING.md). Para uso por agentes, o contrato operacional está em [AGENTS.md](AGENTS.md).
