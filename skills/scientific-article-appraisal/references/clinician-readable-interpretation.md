# Interpretação técnica legível para clínicos

## Público e finalidade

Escreva para fisioterapeutas e outros profissionais de saúde que atendem pacientes, sem presumir familiaridade com estatística ou instrumentos de avaliação. Preserve o dado técnico e forneça a explicação necessária para conferir a análise e fundamentar decisões; não transfira o trabalho básico de interpretação ao revisor humano. Simplifique a linguagem, não o rigor nem a incerteza.

## Unidade editorial: dado → significado → consequência

Para cada resultado ou crítica importante, entregue no mesmo bloco ou imediatamente abaixo:

1. **Dado técnico:** estimativa, unidade, comparador, tempo, intervalo, denominador e p quando reportado e pertinente. Não retire informação essencial para deixar a frase fácil.
2. **Leitura prática:** explique direção, magnitude e incerteza com frases curtas. Diga se o número representa diferença média entre grupos, mudança individual ou medida sem unidade. Se usar analogia, preserve o que ela não permite concluir.
3. **Consequência para a leitura clínica:** responda o que esse achado permite ou não afirmar para a população estudada, sem prescrever conduta ou aprovar protocolo automaticamente.

Use pequenas chamadas como `Em termos práticos`, `Como ler` e `O que isso muda`. Não escreva um curso paralelo de estatística; priorize o que esclarece aquele resultado. Um glossário final pode complementar, mas não substituir a explicação ao lado do dado.

## Siglas e jargão

- Expanda siglas no próprio trecho na primeira ocorrência de cada bloco que pode ser lido isoladamente: síntese, seção de resultados, figura/tabela e anexo. Repita quando o leitor mudará de contexto; não acrescente uma definição longa após cada repetição numérica na mesma frase.
- Exemplos: MD (diferença média); SMD (diferença média padronizada, sem unidade); IC95% (intervalo de confiança de 95%); I² (medida de inconsistência entre estudos); RoB (risco de viés). Expansão do nome não dispensa dizer o significado do valor observado.
- Explique também termos de método e fonte: comparador é o grupo usado para comparação; sham é o procedimento simulado; metanálise combina estatisticamente estudos; protocolo é o plano prévio da pesquisa; OSF é a plataforma pública de registro/documentação; API é a forma de o sistema consultar diretamente a mesma plataforma, não outro estudo; editora não é uma ferramenta de avaliação; DOI é um identificador persistente.
- Defina a sigla conforme o contexto, não por substituição cega. PEDro pode designar uma base de dados em uma lista de fontes de busca ou a escala metodológica ao avaliar ensaios; não expandir o nome da base como se fosse a escala. Preserve siglas/cabeçalhos em citações literais e explique-os na camada editorial, sem alterar a fonte.
- Não assuma que rótulos como `pool`, `estimando`, `heterogeneidade`, `análise de sensibilidade` ou `crítico` se explicam sozinhos. Prefira português ou acrescente explicação breve na primeira utilização pertinente.

## Precisão ao simplificar estatística

- Diferença média entre grupos não é redução garantida para cada paciente. SMD não é número de pontos da escala de dor e não vira percentual de melhora.
- Explique intervalo de confiança como expressão da incerteza/precisão da estimativa no modelo adotado; não afirme probabilidade de 95% de o valor verdadeiro estar naquele intervalo observado. Intervalo cruzando zero não comprova equivalência ou ausência de efeito.
- Valor de p não mede importância clínica nem a probabilidade de o tratamento funcionar ou o resultado ser apenas acaso. Quando necessário, descreva o teste sob seus pressupostos sem atribuir probabilidades erradas à hipótese.
- I² descreve inconsistência da variação entre resultados, não porcentagem de pacientes sem resposta ou probabilidade de o artigo estar errado. Não use um corte isolado para decidir aplicabilidade.
- Limiar de mudança clinicamente importante depende de escala, população, método e contraste. Não transforme limiar de mudança individual em regra universal para a diferença média de grupos; não invente proporção de respondedores.
- Seguimentos repetidos não são pessoas novas; vários relatos/revisões dos mesmos ensaios não são confirmações independentes.

## Instrumentos e julgamentos

- Em posição estratégica, antes do primeiro julgamento detalhado, explique o que o instrumento avalia, por que cabe naquele desenho e quem o aplicou.
- Preserve o rótulo nativo e acrescente a tradução: `Yes (Sim)`, `Partial Yes (Parcialmente sim)`, `No (Não)`. Diga que a resposta se refere ao critério específico e à documentação disponível, não diretamente à eficácia clínica.
- Diferencie `domínio crítico` (aspecto metodológico de especial importância, mesmo quando bem atendido) e `falha crítica` (problema encontrado nesse domínio). Explique a categoria global com a regra nativa, sem transformar avaliação em soma ou porcentagem.
- Separe qualidade da revisão, risco de viés dos estudos e certeza da evidência por desfecho. Esclareça se estamos apenas relatando o GRADE/RoB/PEDro dos autores ou aplicando uma avaliação nova. Não apresente avaliação indireta como releitura dos estudos primários.
- No AMSTAR 2, separe os 16 itens oficiais da regra de confiança global: a regra não é um 17º item nem deve entrar em contagens/somas nativas. Se um registro legado guardar o agregado em `assessment.items`, preserve o julgamento e confira a cobertura pelos IDs oficiais; use um inventário de auditoria separado quando o esquema estrito não admitir outro campo, sem mudar os julgamentos para acomodar o formato.
- Ao final da análise principal, inclua uma síntese curta dos instrumentos utilizados, sua finalidade, a justificativa de escolha e as fontes oficiais. Não chamar instrumento apenas citado de instrumento reaplicado.

## Figuras e tabelas: leitura guiada preenchida

- Mantenha a imagem original íntegra. Acrescente legenda com origem e página, uma orientação de leitura e interpretação dos valores daquela imagem, não apenas advertência genérica.
- Forest plot: explique quadrado/linha horizontal/zero/diamante, direção favorável conforme a legenda, medida e unidade; diferencie estudos individuais, subgrupos de tempo e efeito global. Aplique ao resultado real e explicite discrepâncias, dependência e o limite de um único ensaio.
- Matriz de viés: traduza linhas/colunas, cores e símbolos segundo a fonte. Verde não é certificado global; amarelo/incerto não é viés demonstrado. Não some cores para criar uma escala nova.
- Perfil GRADE: traduza cabeçalhos e categorias; explique o que rebaixou a certeza e de quem é a avaliação. `No` numa coluna de problema não equivale a `No` no AMSTAR. Ausência de teste ou de evidência de viés não prova sua ausência.

## Rastreabilidade compreensível

Explique cedo como usar os códigos de evidência e dê um exemplo completo: código → artigo/PDF ou fonte externa → página/seção → trecho original no anexo. Diferencie resultado do artigo, regra do manual, registro público e log de recuperação da IA. Log interno não é evidência clínica; um código só localiza suporte, não certifica a conclusão. Quando útil, dê página e figura em linguagem humana no próprio bloco.

## Alinhamento editorial

Use alinhamento justificado nos textos corridos do padrão aprovado, mantendo títulos, ficha de capa, rótulos breves e componentes de tabelas/gráficos no alinhamento que preserve legibilidade. Não estique títulos nem altere as imagens científicas para justificar o documento. Confirme o alinhamento na estrutura do documento e no PDF exportado real: a síntese deve continuar inteira em uma página, com fonte legível. Sem capacidade de exportação/inspeção, declare esse limite; o helper MD/HTML não aplica nem verifica essa diagramação.

## Revisões comentadas

Leia todos os comentários, respostas e sugestões atuais; salve snapshot e mapa comentário → alteração. Preserve âncoras e comentários abertos até decisão registrada do revisor responsável. Prefira inserções/edições pontuais; não reimporte DOCX sobre documento anotado. Preserve a capa/organização já aprovadas e a síntese em uma página. Confira o Doc real e o PDF exportado, inclusive texto, figuras, comentários, paginação e acesso privado. Não anunciar revisão humana concluída apenas porque houve comentários.

Ao consolidar edições concorrentes, confira no formato/API do host o contrato das âncoras: índice absoluto ou relativo, unidade de indexação (por exemplo UTF-16, quando aplicável) e inserção antes ou depois. Valide contra o snapshot e simule o resultado completo antes da escrita. Reduza substituições ao fragmento efetivamente diferente para preservar estilos e quebras. Em empates de índice, aplique a ordem coerente com a posição pretendida; ler o documento remoto de volta deve reproduzir exatamente o texto simulado, sem alterar o anexo literal de fontes.
