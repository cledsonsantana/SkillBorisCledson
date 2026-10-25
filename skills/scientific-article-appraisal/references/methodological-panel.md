# Painel metodológico categórico na abertura

Estas orientações descrevem o trabalho editorial do agente com ferramentas autorizadas. O helper JSON → MD/HTML não cria nem verifica sozinho este painel. Sem recursos de layout/exportação, entregue a descrição categórica no artefato disponível e declare o limite; não finja inserção ou paginação verificadas.

## Finalidade e conteúdo
Insira o painel na página 1 imediatamente abaixo da ficha visual, para triagem de leitura por clínicos. Produza um resumo dos julgamentos já fundamentados no corpo, não uma nova escala, classificação automática de eficácia ou selo de validade.

Preencha, nesta ordem:
1. Título curto com o instrumento e objeto avaliado.
2. Componente correspondente à unidade avaliada: faixa única para classificação global nativa, ou pequeno quadrado colorido à esquerda do rótulo de cada resultado/grupo, conforme a regra de formato abaixo. Não use somente cor.
3. Uma linha com o julgamento, incluindo unidade, momento e ressalva decisiva quando necessários.
4. Justificativa breve: problemas metodológicos determinantes e sua consequência, em linguagem clínica.
5. Uma frase sobre o papel do artigo na leitura/decisão e uma nota curta sobre o significado da classificação, sem siglas evitáveis.

Não atribua nota 0–100, percentual de qualidade, probabilidade de resultado verdadeiro, média de domínios ou equivalência entre instrumentos. Não use significância ou direção favorável do efeito para escolher a categoria. O painel não substitui magnitude, precisão, aplicabilidade e certeza do conjunto de evidências.

## Regra estável de escolha do formato
Mantenha a mesma linguagem visual, mas organize o painel pela unidade nativa da avaliação, não pelo tema clínico nem por uma mudança estética oportunista.

- **Classificação global nativa da revisão — AMSTAR 2 e ROBIS:** preserve a faixa única já aprovada, com uma categoria destacada e justificativa. Não converta esses painéis em linhas por desfecho só porque um ensaio recebeu esse formato.
- **Avaliação por resultado — RoB 2 e outras ferramentas quando aplicadas nessa unidade:** use linhas independentes em fundo branco, com um pequeno quadrado colorido à esquerda, rótulo/categoria em texto neutro e explicação imediatamente abaixo. Não pinte a linha inteira, não use faixas vermelhas/amarelas por resultado e não selecione duas categorias na mesma régua.
- Agrupe resultados somente se tiverem julgamentos idênticos, sem ocultar diferenças relevantes. O número de linhas depende dos resultados avaliados: RoB 2 não significa necessariamente dois blocos. Mesmo quando todos tiverem o mesmo julgamento, identifique o grupo avaliado e não invente uma classificação global do artigo.
- **Sem classificação global nativa ou adaptação não validada:** mantenha indicação cinza e explicação da limitação, sem fabricar categoria ou nota.

Mudar a regra na skill não autoriza editar retroativamente todos os documentos. Preserve os formatos e conteúdos aprovados; altere apenas os alvos autorizados.

## Categorias e cores editoriais
- AMSTAR 2: confiança na revisão criticamente baixa (vermelho), baixa (laranja), moderada (amarelo) e alta (verde). Siga as falhas críticas e a regra oficial; nunca some itens. Mantenha condicionantes de materiais inacessíveis, sem afirmar inexistência do que não pôde ser verificado.
- ROBIS: alto risco (vermelho), incerto (cinza) e baixo risco (verde). Incerto não é um nível intermediário de risco. O objeto é a revisão, não a certeza clínica de cada resultado.
- RoB 2: alto risco (vermelho), algumas preocupações (amarelo) e baixo risco (verde), na unidade resultado/desfecho e tempo. Quando os julgamentos diferirem, use blocos/linhas separados por resultado ou grupo de resultados com julgamento idêntico, cada qual com seu rótulo e uma única seleção. Nunca marque duas categorias na mesma faixa: parece uma classificação contraditória do artigo e exige decodificação do texto. Preserve a aplicação completa por resultado no corpo, sem fabricar nota global.
- Auditorias adaptadas ou ferramentas sem classe global nativa: use cinza com `SEM CLASSIFICAÇÃO GLOBAL NATIVA`, explicando a limitação e apresentando síntese descritiva. Falta de classe não significa ausência total de qualidade. Não chame adaptação de aplicação nativa validada.

As cores são uma convenção editorial de leitura, não uma nova validação ou uma régua comparável entre desenhos. Em outras ferramentas, consulte o manual e mantenha a saída nativa; não improvise cortes para caber no semáforo.

## Linguagem e apresentação
- Escolha a ferramenta pelo desenho e pela pergunta, não pelo tema terapêutico. Explique brevemente mudanças de instrumento entre revisão e ensaio, inclusive em linhas de pesquisa independentes; não imponha agulhamento seco como escopo de todo artigo.
- Ao usar cinza por adaptação, explique que o limite é a aplicabilidade/classificação do instrumento, não qualidade mediana do artigo nem falta de leitura crítica concluída.
- Prefira nomes clínicos dos grupos de desfechos, como dor/questionários e testes de desempenho, em vez de siglas sem definição na abertura. Mantenha identificação técnica completa no corpo.
- Use texto claro sobre o objeto: confiança nos métodos de uma revisão não é GRADE; risco alto não prova que todo achado seja falso; qualidade metodológica favorável não garante precisão ou aplicabilidade.
- Mantenha título, faixa e explicação como um bloco visual compacto. Confira contraste das etiquetas (ao menos 4,5:1 para fonte pequena), marcadores e fontes legíveis. Não deixe parágrafos vazios herdarem o grande espaçamento da capa.
- Preserve a ficha 16:9 separada, limpa e reutilizável. O painel do documento não autoriza sobrepor julgamentos à imagem original nem alterar o PNG para slides.
- Preserve capa/painel na página 1, síntese completa na 2 e análise integral a partir da 3. Confira a exportação real; não resolva excesso de texto com fonte microscópica.

## Edição de documentos existentes
Leia texto e comentários atuais; guarde snapshots, exportações e backup nativo privado. Insira apenas o painel por edição nativa com índices UTF-16 e requiredRevisionId; não reconverta documento comentado. Preserve IDs, imagens, originais, permissões e revisão humana. Validação humana prévia não será removida por uma alteração de apresentação, nem estendida a outros artigos.

Uma tabela nativa de uma linha pode formar a faixa sem hospedar imagem publicamente. Na Docs API, omita pageBreakBefore em parágrafos dentro de células, inclusive quando false. Aplique namedStyleType e demais estilos de parágrafo antes dos estilos explícitos de texto: mudar o estilo nomeado depois pode apagar cor, fonte e negrito da etiqueta. Formate os vazios ao redor da tabela para evitar espaçamento herdado da capa.

Para resultados independentes, mantenha o fundo branco e aplique cor somente ao glifo quadrado `■`, antes do rótulo neutro; não use `shading.backgroundColor` colorido no título inteiro. Prefira caixa normal e negrito ao excesso de maiúsculas. Alinhe a explicação abaixo ao início do texto do rótulo, não ao quadrado. Na leitura remota de cores, compare equivalência RGB em 8 bits: a API pode quantizar componentes enviados como decimais, sem mudança visual de cor. Ao substituir um painel com tabela, exclua a tabela inteira e o conteúdo do bloco, mas preserve a última quebra de parágrafo antes da legenda seguinte. Insira o novo texto sem quebra final duplicada e aplique estilos somente aos novos parágrafos. Compare também os estilos de texto/parágrafo fora do painel e as páginas seguintes, não apenas as palavras, para comprovar preservação.

## Verificação de conclusão
- Cada painel corresponde aos julgamentos existentes, com fonte/âncora registrada no inventário local; nenhum julgamento foi recalculado por contagem de itens.
- Todas as unidades/desfechos distintos e condicionantes determinantes estão preservados.
- Leia o alvo remoto exato: apenas um painel, categorias e cores corretas; conteúdo anterior integralmente preservado ao excluir o bloco inserido; mesmos comentários/âncoras e imagens.
- Confira privacidade e estado de revisão. Preserve originais e PNGs por ID, nome, pasta e checksum.
- Exporte PDF e DOCX do Google Doc, inspecione a capa e valide a estrutura; compare páginas 2 em diante e a posição da síntese/análise.
- Em lotes, persista resultados por documento e confira programaticamente a contagem esperada antes de declarar conclusão. Não publique o acervo nem o pacote público por consequência dessa edição privada.
