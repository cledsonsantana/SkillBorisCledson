# Método e resultado — leitura para humanos

A skill orienta um agente de IA a preparar uma análise crítica completa, rastreável e legível para profissionais que atendem pacientes. Não é um instrumento metodológico validado novo, não é um avaliador automático de eficácia e não dispensa revisão humana.

## O humano e o agente

O humano informa o artigo, o objetivo, o escopo e as autorizações; depois confronta a análise e decide seu uso. O agente obtém os materiais autorizados, conduz a extração e avaliação, escreve, executa verificações e entrega o resultado. Instruções operacionais estão em AGENTS.md e INSTALL.md — não é necessário o humano implementar scripts.

## A sequência

**Identificar pergunta e fontes.** Confirmar desenho pelos métodos, não pelo título; ler texto, tabelas e figuras; procurar protocolo, registro e suplementos. Delimitar o material de fato acessível e o que falta. Não fingir texto completo a partir de abstract.

**Examinar elegibilidade.** Comparar com critérios fornecidos. Sem escopo formal, declarar elegibilidade indeterminada e explicar pertinência temática. Fragilidade metodológica não cria automaticamente critério de exclusão.

**Extrair características e resultados.** Preservar população, comparadores, dose quando pertinente, desfechos, tempo, denominadores, unidades, direção, estimativas e incerteza. Não transformar seguimentos repetidos em participantes novos ou silêncio sobre danos em ausência de risco.

**Avaliar método e estatística.** Escolher instrumento pela pergunta/desenho, consultar manual e preencher itens com julgamentos nativos, justificativas e fontes. Não somar ferramentas distintas ou compensar falha crítica por média. Examinar limitações que possam mudar a interpretação, sem exigir o mesmo modelo estatístico para todo estudo.

**Interpretar e redigir.** Separar extração, conclusão dos autores e julgamento independente. Em cada resultado relevante, manter dado técnico → significado em linguagem clara → consequência/limite clínico. Explicar siglas por contexto e a leitura dos gráficos/tabelas utilizados.

**Revisar a linguagem integralmente.** Além de expandir siglas, explicar quem fez o procedimento, qual comparação foi feita, o que o número significa e por que a limitação importa. Isso vale para síntese, corpo, leitura de figuras e justificativas dos anexos. Preservar dados e fontes é necessário, mas não garante que a reescrita tenha preservado o sentido; conferir os pares alterados e documentar correções antes de aplicar. Instituição e população-alvo não são predefinidas.

**Conferir e entregar.** Comparar afirmações com fontes, validar estrutura, reler o arquivo realmente entregue e conferir as permissões. Confirmar paginação quando houver PDF/Doc paginado, sem confundir geração de HTML com verificação visual. O status de revisão humana muda só com confirmação real, restrita à análise correspondente.

## A apresentação final

- Página 1: capa limpa com cabeçalho/referência e painel categórico dos julgamentos já fundamentados; respeitar direitos de reprodução e entregar ficha separada para slides quando viável e autorizado.
- Página 2: síntese objetiva completa em uma página, para apoiar seleção e apresentação.
- Página 3 em diante: análise integral, figuras/tabelas originais úteis e anexos com instrumentos, justificativas e evidências localizáveis.

Textos corridos justificados; títulos e elementos visuais mantêm alinhamento que preserve legibilidade. A abertura não substitui a análise; a crítica pode justificar uso favorável, discussão de limitações/resultados desfavoráveis ou não inclusão nos slides. Revisar a análise não aprova automaticamente o artigo, protocolo ou recomendação institucional.

Essa organização paginada exige ferramentas de edição/exportação e conferência no host. Se elas faltarem, o agente entrega o formato realmente disponível, como Markdown/HTML, identifica a limitação e não anuncia falsamente um Google Doc ou PDF verificado.

## Painel metodológico, sem nota universal

AMSTAR 2 e ROBIS podem produzir um julgamento global nativo da revisão: uma faixa única mostra essa categoria. RoB 2 avalia resultados específicos: cada resultado ou grupo com julgamento idêntico recebe um pequeno quadrado colorido, rótulo neutro e explicação em fundo branco. O número de linhas depende dos resultados, não de uma regra de sempre dois blocos. Sem classe global nativa, o cinza explica a limitação, não qualidade mediana.

Não há conversão legítima universal para nota 0–100 ou percentual de resultado verdadeiro. Painéis não substituem magnitude, incerteza, aplicabilidade ou certeza do conjunto de evidências. A diagramação exige recursos de edição/exportação do host.

## O papel do código

O helper lê um registro JSON preenchido pelo agente. Confere estrutura, referências entre registros, citações em textos locais, consistência do inventário declarado e integridade de imagens; pode gerar Markdown/HTML. Não escolhe ferramenta, não decide risco de viés e não confirma sozinho que a citação foi fielmente transcrita da página ou sustenta a conclusão.

Os testes sintéticos confirmam comportamento técnico. Não comprovam validação científica da skill, independência entre revisores ou capacidade universal para todos os desenhos. Antes de produzir grandes lotes, o agente e o responsável devem calibrar o procedimento com materiais reais, sem publicar fontes privadas.
