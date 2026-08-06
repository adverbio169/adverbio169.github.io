# IA como ferramenta de apoio à decisão na gestão pública

Proposta de painel de indicadores sobre os dados abertos do Estado de Roraima,
em três eixos: **alcance da estratégia**, **redução de riscos** e **avanço da
maturidade**.

| arquivo | o que é |
|---|---|
| `painel-ia.html` | protótipo navegável do painel (arquivo único, autocontido) |
| `README.md` | esta proposta: fontes, catálogo de indicadores e plano de implantação |

Este material **não faz parte** da publicação da Comissão Mista do Subsídio que
ocupa a raiz do repositório. É trabalho separado e não é referenciado pela
`index.html` — o endereço impresso no QR Code do relatório continua levando
apenas ao material da Comissão.

---

## Antes de tudo: o que está verificado e o que não está

O protótipo foi montado num ambiente **sem acesso de rede a `*.rr.gov.br`**. As
chamadas de API foram bloqueadas pela política de egresso antes de sair
(HTTP 403 no túnel), tanto por `curl` quanto pelo buscador.

Consequências, ditas com todas as letras:

- **Nenhum endpoint foi executado.** Os caminhos listados adiante vieram da
  documentação publicada e de resultados de busca, não de resposta de servidor.
- **Nenhum número do painel é real.** Toda a série é ilustrativa e está isolada
  no objeto `DADOS`, no topo do `<script>`. O aviso no alto da página diz isso ao
  leitor, e ele deve continuar lá até que a primeira fonte real seja ligada.
- **Os nomes de campo são suposição.** A forma de cada resposta (nomes de
  atributos, paginação, formato de data, unidade monetária) precisa ser lida no
  Swagger antes de qualquer código de integração.

O primeiro passo da implantação é, portanto, verificação — não desenvolvimento.

---

## Fontes de dados

Ponto de partida: o Swagger do Portal da Transparência de Roraima, em
`transparencia.rr.gov.br/transparencia/swagger-ui/`.

| Fonte | Caminho levantado | Alimenta |
|---|---|---|
| Arrecadação e repasse (SEFAZ) | `servicos.sefaz.rr.gov.br/apiarrecadacaorepasse/public/api/getportalarrecadacaobycodmunicipio` | E1, E2, E3, E5 |
| Contratos — Fiplan-RR | `transparencia.rr.gov.br/api-transparencia/public/dashboard/contratos/api` | R1, R2, R7 |
| Despesas por credor | `/api-transparencia/public/dashboard/despesas/…` | E4, E6, R3, R4 |
| Diárias | `/api-transparencia/public/dashboard/diarias/…` | R5 |
| Remunerações | `/api-transparencia/public/dashboard/remuneracao/…` | M3 |
| Obras | `/api-transparencia/public/dashboard/obras/…` | R6 |
| Unidades orçamentárias | `/api-transparencia/public/dashboard/unidades/…` | filtro global |
| Patrimônio | `/api-transparencia/public/dashboard/patrimonio/…` | M2 |

Duas fontes externas fecham o conjunto:

- **IPCA / IBGE** (`servicodados.ibge.gov.br`) — para deflacionar a série de
  receita. Sem isso, E2 mede inflação e chama de crescimento.
- **Siconfi / Tesouro Nacional** (`apidatalake.tesouro.gov.br/ords/siconfi`) —
  RREO e RGF de todas as unidades da federação, para comparação. É a mesma base
  usada no painel da Comissão, na raiz deste repositório.

Há ainda uma `api-batimento.sefaz.rr.gov.br` anunciada como ambiente de teste;
vale confirmar com a SEFAZ se ela é o caminho recomendado para desenvolvimento.

---

## Os três eixos

### Eixo 1 — Alcance da estratégia

Chegamos onde dissemos que iríamos chegar? Mede o quanto dos objetivos
declarados foi atingido e a que distância está o que ficou para trás. Todo
indicador deste eixo sai de dado orçamentário e tributário já público, o que o
torna conferível por terceiros.

### Eixo 2 — Redução de riscos

O uso de IA aqui é de **triagem**: o modelo ordena o que merece olhar humano,
não decide. Por isso o eixo mede duas coisas ao mesmo tempo — a exposição a
risco caiu, **e** o alerta emitido é confiável o bastante para justificar o
tempo de um auditor. Um painel que mostrasse só a primeira metade esconderia o
caso em que o modelo produz muito ruído e ninguém mais olha para ele.

### Eixo 3 — Avanço da maturidade

Escala 0–5 em seis dimensões, no espírito do diagnóstico de maturidade em IA que
o TCU aplicou à administração pública federal — levantamento em que cerca de
38% das organizações federais apareceram no nível zero. Mede se a capacidade
ficou instalada na instituição, não se um piloto deu certo: piloto que depende
de uma pessoa não é maturidade.

---

## Catálogo de indicadores

18 indicadores. Todo indicador tem fórmula explícita, fonte nomeada e
periodicidade — sem os três, não entra no painel.

### Estratégia

| Cód. | Indicador | Fórmula | Fonte | Periodicidade |
|---|---|---|---|---|
| E1 | Realização da arrecadação | Arrecadado ÷ meta LOA | Arrecadação e Repasse | Mensal |
| E2 | Crescimento real da receita própria | (Rec.ₜ deflacionada ÷ Rec.ₜ₋₁) − 1 | Arrecadação + IPCA | Mensal |
| E3 | Participação da receita própria | Receita própria ÷ receita total | Arrecadação + Fiplan | Mensal |
| E4 | Execução orçamentária | Liquidado ÷ dotação atualizada | Despesas — Fiplan | Mensal |
| E5 | Repasse constitucional a municípios | Repassado ÷ devido (25% ICMS) | Arrecadação e Repasse | Mensal |
| E6 | Prazo médio de pagamento | Média(data pagamento − data liquidação) | Despesas por credor | Mensal |
| E7 | Alcance dos objetivos estratégicos | Média ponderada do alcance por OE | Plano estratégico | Trimestral |

### Risco

| Cód. | Indicador | Fórmula | Fonte | Periodicidade |
|---|---|---|---|---|
| R1 | Concentração de fornecedores (HHI) | Σ(participação do credor)² | Contratos + despesas | Mensal |
| R2 | Contratos a vencer sem renovação | Fim ≤ 90d sem aditivo ÷ total | Contratos — Fiplan | Semanal |
| R3 | Indício de fracionamento | Mesmo credor + objeto, valores logo abaixo do limite | Despesas por credor | Mensal |
| R4 | Despesa fora do padrão histórico | \|z\| > 3 na série da rubrica × unidade | Despesas — Fiplan | Mensal |
| R5 | Diária em desvio de padrão | Frequência ou valor > p99 da unidade | Diárias | Mensal |
| R6 | Obra com atraso de cronograma | Execução física < prevista em > 20% | Obras | Mensal |
| R7 | **Precisão dos alertas** | Alertas confirmados ÷ alertas emitidos | Registro de verificação | Mensal |
| R8 | Tempo médio até a detecção | Média(data do alerta − data do fato) | Registro de verificação | Mensal |

R7 e R8 não saem de API: dependem de um **registro de verificação** — cada
alerta anotado como procedente ou improcedente por quem o analisou. É o item
mais fácil de deixar para depois e o mais caro de não ter, porque sem ele não
existe como saber se o modelo está ajudando ou atrapalhando.

### Maturidade

| Cód. | Indicador | Fórmula | Fonte | Periodicidade |
|---|---|---|---|---|
| M1 | Nível de maturidade em IA | Média das 6 dimensões (0–5) | Autoavaliação + evidência | Semestral |
| M2 | Prontidão da base de dados | Cobertura × completude × atualidade | Todas as APIs | Mensal |
| M3 | Institucionalização da governança | Marcos concluídos ÷ marcos previstos | Registro do comitê | Trimestral |

As seis dimensões de M1: governança e estratégia; dados e infraestrutura;
pessoas e competências; tecnologia e ferramentas; ética, risco e conformidade;
geração de valor.

### O índice composto

O número de abertura do painel é o **Índice de Gestão Orientada por Evidência**,
0–100:

```
IGE = 0,40 × (alcance da estratégia)
    + 0,30 × (redução de riscos)
    + 0,30 × (avanço da maturidade, reescalado de 0–5 para 0–100)
```

Os pesos são uma escolha, não um achado, e por isso ficam impressos ao lado do
número na própria página. Índice cuja composição não é aberta não serve para
decidir — serve para encerrar a discussão, que é o contrário do que se quer.

---

## Ligar o painel aos dados reais

A camada de dados está isolada. No `painel-ia.html`, procure o comentário
`INÍCIO DA CAMADA DE DADOS`: tudo que o desenho consome está no objeto `DADOS`,
e nada mais no arquivo lê da rede.

Sequência sugerida:

1. **Confirmar os endpoints no Swagger** e registrar, para cada um: caminho
   real, parâmetros, formato de data, unidade monetária, paginação, e se há
   limite de requisições.
2. **Escrever um coletor** (fora desta página) que consulta as APIs e grava um
   `dados.json` com exatamente a forma do objeto `DADOS`. Manter a forma estável
   é o que permite trocar a fonte sem mexer no desenho.
3. **Trocar a constante por um fetch** desse `dados.json`, mantendo o restante
   do arquivo intacto.
4. **Remover o aviso de dados ilustrativos** — e só então, porque enquanto
   houver um número inventado na tela o aviso é a parte mais importante da
   página.

Sobre a autocontenção: o `painel-ia.html` não usa CDN, fonte, script nem imagem
externa, pela mesma regra do `painel.html` da raiz. Se o passo 3 introduzir um
`fetch`, a página deixa de abrir por `file://` e passa a exigir servidor — é uma
troca consciente, e a alternativa é embutir o JSON no próprio arquivo a cada
publicação, como já se faz com o painel da Comissão.

---

## Plano de implantação

| Fase | O que entrega | Depende de |
|---|---|---|
| 1. Verificação | Endpoints confirmados, dicionário de dados, medição real de M2 | acesso de rede à SEFAZ |
| 2. Fundação | Coletor, `dados.json`, eixos 1 e 3 com dado real | fase 1 |
| 3. Triagem | Regras determinísticas de R1–R6 (sem modelo estatístico ainda) | fase 2 |
| 4. Verificação humana | Registro de alertas procedentes/improcedentes → R7, R8 | fase 3 |
| 5. Modelo | Detecção estatística onde a regra determinística se mostrar insuficiente | fase 4 |

A ordem importa. As fases 3 e 4 vêm antes da 5 de propósito: regra simples
com resultado medido é melhor ponto de partida do que modelo sem linha de base
para comparar. Sem a fase 4, a fase 5 não tem como ser avaliada.

---

## Limites e proteção de dados

**O painel não decide.** Não classifica pessoa, não produz ato administrativo e
não substitui motivação. Ele ordena evidência para que a decisão — humana e
motivada — seja tomada com o que já se sabe. Todo alerta é hipótese a verificar,
e a taxa de acerto do modelo (R7) é publicada no próprio painel exatamente para
que ninguém trate a saída como veredito.

**Dados pessoais.** Todas as fontes previstas são de publicidade obrigatória e
já divulgadas em dados abertos. A série de remunerações entra apenas agregada,
para dimensionamento de equipe; nenhum indicador do catálogo requer dado pessoal
sensível nem identificação de servidor. Avaliação de impacto à proteção de dados
por solução consta como marco de governança em M3.

---

## Nota sobre o protótipo

Paleta categórica e de estado validadas para separação sob daltonismo e
contraste, nos modos claro e escuro. Todo gráfico tem tabela equivalente
(botão "Tabela"), legenda quando há duas ou mais séries, e rótulo de texto junto
a qualquer cor de estado — cor nunca é o único portador de significado. A página
imprime com as tabelas abertas.
