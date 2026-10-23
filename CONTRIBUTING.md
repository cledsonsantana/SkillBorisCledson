# Contribuições — roteiro para agentes

1. Leia AGENTS.md e a skill. Limite o escopo da mudança; preserve a separação entre relato, viés, certeza e decisão humana.
2. Para comportamento de código, escreva teste que falha pelo motivo esperado antes da correção; implemente o mínimo e rode os testes completos.
3. Para método, consulte a versão oficial e justifique a mudança com fonte localizável. Não substitua instrumento nativo por score próprio.
4. Não inclua PDFs/figuras de terceiros, dados pessoais, endpoints privados, credenciais, logs ou exemplos clínicos disfarçados. Use fixtures sintéticas identificadas.
5. Preserve o padrão de entrega completa e as capacidades/limites reais do host. Não prometa que o helper monta Google Docs ou confere ciência automaticamente.
6. Execute as duas suítes descritas em INSTALL.md e o smoke test com instalação temporária. Para mudar o instalador, teste destino já existente, adaptações, backup, symlinks, dry-run, check e caminhos inseguros.
7. Faça uma contribuição pequena, com descrição do problema, decisão, testes realmente executados e limitações. Não alegue CI verde sem consultar o resultado remoto.

Mudanças de versão precisam manter README e metadados da skill coerentes. Não rode instalações de teste sobre perfis reais. Não publique commits/releases sem autorização do responsável pelo repositório.
