# Auditoria de fontes e resultados em ensaios randomizados

Execute estas conferências com as ferramentas disponíveis e autorizadas do host. O helper incluído não lê planilhas, recupera suplementos, executa reanálise ou aplica RoB 2 automaticamente. Registre verificações não realizadas sem inventar seus resultados.

## Fontes antes do julgamento

- Inspecione artigo, apêndices e todas as abas/cabeçalhos das planilhas; uma coluna de seguimento adicional pode estar no suplemento mesmo quando o corpo nega seguimento. Registre o que efetivamente existe e a diferença entre observação e imputação, sem acusar seleção motivada pelo resultado sem evidência.
- Não aceite rótulos “missing data” e “imputed data” como comprovação: confira células, contagens, pares válidos e igualdade dos valores entre arquivos. Célula numérica preenchida não comprova observação clínica; preserve o denominador observado do fluxo até esclarecimento.
- Se o CDN da editora bloquear dados suplementares, procure repositório institucional explicitamente relacionado ao DOI. Valide título/autores, nomes de membros e hashes. Inspecione ZIP antes de extrair, rejeite travessia/arquivos executáveis e não instale macros nem execute conteúdo recuperado. Distinga suplemento recuperado de candidato de URL que falhou.
- Compare a versão atual do registro com o artigo sem atribuir automaticamente seus campos à primeira versão histórica. Registre cronologia disponível, limitações e ausência de SAP; cadastro inicialmente prospectivo não prova imutabilidade do plano.

## Métricas e interpretação clínica

- Confira soma bruta, subescalas, normalização, direção e denominador antes de interpretar um limiar. O mesmo nome de questionário não torna suas agregações intercambiáveis. Transformação linear de total não reconstrói subescalas nem valida importância clínica.
- Revalide a proveniência do limiar: população, intervenção, prazo, mudança individual versus diferença entre grupos e importância clínica versus erro de medida. Não trate MCID/MCII/MDC como sinônimos ou números universais. Quando uma crítica usar guia atualizado, procure apoio contemporâneo ao ensaio para não impor regra posterior silenciosamente.
- Para percentuais, teste a fórmula de mudança de cada participante e a média dessas mudanças; ela não é a razão de médias agregadas. Distinga pontos da escala, percentual individual e diferença em pontos percentuais de mudança relativa. Se a recuperação dos dados resolver uma crítica inicial, retire a crítica do texto ativo.
- Confira a convenção de mudança em cada tabela separadamente. Basal menos pós e pós menos basal invertem o significado do sinal; não propague a legenda da tabela principal aos apêndices.
- Separe medida clínica imediata, avaliação no dia seguinte e tempo recordado pelo questionário. Temperatura cutânea imediatamente após aplicação não é analgesia imediata nem benefício funcional.

## Estatística verificável, sem errata inventada

- Preserve estimativas e ICs publicados em bloco próprio. Rotule comparações independentes de mudanças individuais como auditoria exploratória; exponha fórmula, dados, denominadores e pressupostos. Não anuncie reprodução de ANOVA ou correção autorizada sem código/plano e implementação correspondentes.
- Não considere imputação fixa uma observação real nem finja incorporar sua incerteza em teste simples. Se um intervalo independente atravessar um limiar que o publicado exclui, explicite a dependência da conclusão ao modelo; isso não comprova erro autoral nem benefício clínico.
- Em dados pareados da mesma amostra, confira coerência da dispersão da diferença: o DP não pode exceder a soma dos DP marginais. Verifique primeiro se o número é realmente DP, EP ou intervalo; cabeçalho ambíguo exige ressalva, não substituição por palpite.
- Não transforme pontos anatômicos correlacionados, várias escalas ou seguimentos repetidos em estudos/pacientes independentes. Registre multiplicidade e evite promover IC nominal isolado a eficácia global.

## RoB 2 por resultado

- Declare variante, efeito-alvo, contraste e tempo. Inventarie perguntas no formulário vigente, preencha condições/saltos e aplique algoritmos nativos sem soma ou escore híbrido.
- No autorrelato, o participante é o avaliador do desfecho; coletor cego não cega o respondente. Separe a possibilidade (4.4) da probabilidade de influência (4.5), com inferência explícita e justificativa. Não torne toda falta de cegamento automaticamente alto risco.
- Diferencie autorrelato e teste cronometrado/contado por examinador cego; motivação pode continuar relevante, mas o mesmo julgamento não é transferido mecanicamente.
- Ao avaliar o efeito de pertencer ao grupo definido pelo sorteio, o uso domiciliar permitido, mesmo desigual, pode fazer parte da estratégia prevista; não é automaticamente um desvio causado pelo ensaio. Não penalize D2 automaticamente nem converta análise de aderentes em ITT.
- Seguimento não discutido não prova que o resultado de outro tempo foi selecionado em função do valor. Julgue seleção no resultado-alvo e explique diferenças de relato, sem presumir má conduta.

## Entrega e validação

- Mantenha extrações originais. Em cópias textuais derivadas para o helper, converta form feed em quebra de linha e represente controles proibidos não mapeados explicitamente, com manifesto. Não adivinhe operadores nem substitua globalmente “2” por sinal de menos; confira o PDF visualmente. Não altere o helper para aceitar fonte binária só para passar a validação.
- No Docs com abas, resolva alinhamento/fonte efetivos pelo namedStyle da documentTab quando paragraphStyle omitir o campo. Ausência do campo não significa alinhamento à esquerda. Preserve diferença entre corpo, títulos, tabelas e referências.
- Compare integralmente texto nativo remoto com a origem, confira imagens realmente incorporadas e exporte PDF do alvo exato: capa p1, síntese completa p2 e análise p3. Faça ajustes editoriais finais por operações nativas com revisão/índices UTF-16 e comentários preservados; não reimporte documento comentado.
- Mantenha originais e análises privadas no destino autorizado. Aprimorar o procedimento interno não autoriza publicar PDF, dados individuais, análise ou nova versão do pacote público.
