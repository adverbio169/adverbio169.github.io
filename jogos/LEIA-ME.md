# Leia-me — a pasta `jogos/`

Páginas independentes, sem relação com o material da Comissão. Cada uma é um
arquivo só, sem servidor e sem instalação.

Este arquivo é o **prático**: o que existe, como mexer, como testar. O raciocínio
de cada decisão — e o registro de cada defeito encontrado — está em
[`COMO-FUNCIONA.md`](COMO-FUNCIONA.md), que é longo de propósito.

---

## Os arquivos

| arquivo | o que é |
|---|---|
| `index.html` | a portinha: lista os jogos |
| `aviao3d.html` | **o jogo principal.** three.js, mundo 3D. Joga-se no computador ou direto no celular |
| `aviao.html` | a versão 2D, mais antiga. É dela que sai o núcleo do `tv.html` |
| `tv.html` + `controle.html` | o arranjo TV + celular: a TV mostra o jogo 2D, o celular é o controle |
| `aviao-tv.html` | o mesmo, num arquivo só que decide sozinho se é tela ou controle |
| `corrida.html`, `rosto.html` | outros dois, independentes |
| `testar-sensor.html` | diagnóstico: mostra o que o sensor do aparelho está mandando |

### Arquivos que NÃO se edita à mão

`aviao3d.html`, `tv.html`, `controle.html` e `aviao-tv.html` são **montados**.
Editar o `.html` funciona até a próxima montagem apagar tudo. Edite o `.modelo.html`:

```
aviao3d.html   ← aviao3d.modelo.html   + three.js
controle.html  ← controle.modelo.html  + PeerJS
tv.html        ← tv.modelo.html        + PeerJS + QR + núcleo de aviao.html
```

E depois rode, dentro de `jogos/`:

```
python3 montar.py
```

Ele precisa achar `node_modules` com `peerjs` e `qrcode-generator`
(`npm install peerjs qrcode-generator`, ou aponte com
`NODE_MODULES=/caminho python3 montar.py`).

### Para testar no celular sem publicar

```
python3 servir.py
```

Serve a pasta por **https** na sua rede — o sensor de inclinação só liga em
https, então um arquivo aberto localmente ou um servidor http comum não servem.

---

## Os três arranjos

O mesmo jogo, três jeitos de jogar. Vale saber qual é qual, porque quase toda
confusão nasce de mexer no arranjo errado.

| arranjo | onde | o painel |
|---|---|---|
| **computador / TV** | `aviao3d.html` num monitor | **2 janelas** de instrumento, canto inferior |
| **celular como visor** | `aviao3d.html` no celular deitado | **1 janela**, sobre o mundo 3D |
| **celular como controle** | `controle.html` + `tv.html` numa TV | o celular **é** o painel inteiro: 2 janelas |

---

## Comandos

### No computador

| tecla | o quê |
|---|---|
| setas | voar |
| **A** / **D** | leme |
| **W** / **S** | acelerador |
| **Shift** | pós-combustão |
| **G** | trem de pouso |
| **F** | flapes |
| **espaço** | atirar |
| **V** | trocar a vista (FORA → CABINE → CAPACETE → …) |
| **1 2 3** | trocar de arma |
| **Z** | chamas de defesa |
| **C** | olhar com a cabeça (precisa de câmera) |

O painel responde ao mouse: arrastar troca de página, clicar numa aba vai
direto, clicar numa linha escolhe (missão, cabeceira, alvo). Os rodapés dizem
**CLIQUE** no computador e **TOQUE** no celular — é o mesmo texto, escolhido
pelo aparelho.

### No celular

Cada movimento do aparelho é um comando: **girar de lado** = aileron, **puxar a
borda de cima** = profundor, **apontar para o lado** = leme. O resto é toque.

**Não existe "enter".** O alvo é o próprio item: o toque já é a escolha.

| o quê | como |
|---|---|
| formato de uma janela | toca na janela, depois no formato na fita de baixo |
| …ou | arrasta de lado **dentro** da janela |
| missão | página **OBJET**, em solo, toca na linha |
| cabeceira de pouso | página **APROX**, toca na linha |
| alvo designado | página **TÁTIC**, toca no contato |
| arma | desliza no poço ARMAMENTO |
| trem e flape | página **SINÓT**, toca no desenho do avião |
| trocar a vista | botão **👁** na faixa de cima do controle (cicla as três) |
| qualidade do desenho | botão **◉** na mesma faixa (alto → médio → baixo) |
| olhar com a cabeça | botão **🧠** na mesma faixa (precisa de câmera **na tela do jogo**) |
| descarregar a aproximação | toca no cabeçalho dela |

---

## As três vistas

| vista | o que é |
|---|---|
| **FORA** | perseguição atrás do avião, a de sempre |
| **CABINE** | de dentro, olhando pelo vidro: o arco fino do para-brisa, o **painel digital do jogo nas telas do avião** (largo e baixo, como caça moderno), os consoles, e o manche e a manete que **se mexem com o comando** |
| **CAPACETE** | logo atrás e acima da cabeça, como a câmera do vídeo: pernas, mãos no manche e na manete, trilhos da capota, painel e o combinador do HUD, com o mundo na metade de cima |

**Na cabine as duas janelas do HUD somem**: elas estão dentro do avião. As
duas telas do painel mostram as mesmas duas páginas, ao vivo, redesenhadas dez
vezes por segundo — é o mesmo código do painel 2D pintando num canvas que vira
textura. A cabine **não foi desenhada agora** — banco, painel, mostradores e manche já
estavam no modelo desde sempre. O que faltava era caber na lente: o plano de
corte da câmera vale 40 unidades e o painel está a 28 do olho. Cada vista
declara o seu corte (`perto`), e a cabine usa 8. Ver
[`COMO-FUNCIONA.md`](COMO-FUNCIONA.md), "A cabine por dentro".

Os números de cada uma (distância, altura, inclinação, campo de visão) estão
numa tabela só, `VISTAS`, no `aviao3d.modelo.html`. Mudar enquadramento é
editar três números — não é procurar onde a câmera é montada.

## O painel

Oito formatos de página, mais o ATITUDE (só no controle):

| formato | o que mostra |
|---|---|
| **SINÓT** | o avião desenhado: trem, flapes, combustível, avarias. Tocar no desenho aciona |
| **MOTOR** | potência, combustível, nitro |
| **MAPA** | o radar: contatos, pista mais perto, alcance |
| **TÁTIC** | os contatos em lista, com distância e solução de tiro. Designa alvo |
| **ARMAS** | munição e trava |
| **APROX** | a aproximação: carrega uma cabeceira e ela guia |
| **OBJET** | os objetivos da missão e a fase dela |
| **VOO** | velocidade, altitude, rumo, razão de subida, G |
| **ATITUDE** | a bola do horizonte (só no celular-controle) |

No celular-controle as janelas são **multifunção**: qualquer formato em qualquer
uma, e a configuração fica guardada.

---

## As missões

Escolhidas na página **OBJET** com o avião **parado na pista**. Decolar é
confirmar.

| sortida | objetivos | quem chama os caças |
|---|---|---|
| **PATRULHA** | os seis de sempre | ninguém — céu limpo |
| **DEFESA AÉREA** | abater 4 caças, voltar e pousar | você subir acima de 350 m |
| **BOMBARDEIO** | destruir 8 alvos, voltar e pousar | a 3ª explosão no chão |
| **INFILTRAÇÃO** | 18 s baixo sobre PORTO ALTO, voltar | você passar de 320 m |

**O combate nunca começa na decolagem.** Há quatro fases, escritas na página
OBJET: `EM SOLO` → `TRÂNSITO` → `CONTATO EM n s` → `QUENTE`. Entre "o céu está
limpo" e "tem caça em cima de você" existem sempre doze segundos de aviso.

---

## Números do envelope (para não inventar limites)

| | |
|---|---|
| teto do avião | **585 m** |
| tanque | ~8 min de cruzeiro, 3 de pós-combustão, 20 de marcha lenta |
| chão | `CHAO = -700` em unidades de mundo; 1 m = `METRO` = 20 |
| alcance do radar | **1,3 km** (`RADAR_ALC = 26000` unidades de mundo) |
| rampa de aproximação | 3° |
| alvos no chão | 26 |
| caças no céu ao mesmo tempo | 2 ou 3, conforme a sortida |

O teto de 585 m já causou **três** defeitos: limiares escritos com números de
avião de verdade (900 m, 1200 m, 700 m) que nunca podiam acontecer. Antes de
escrever uma altura, confira contra o teto.

E o quarto erro de unidade nasceu de um **nome**: a constante chamava-se
`RADAR_KM` e valia 26000 — que são unidades de mundo, 1,3 km. Eu li o nome e
escrevi "26 km" na primeira versão deste arquivo. **Unidade no nome ou unidade
nenhuma**; meio-termo engana. Hoje é `RADAR_ALC`.

---

## Testes

Não há suíte no repositório: os testes são scripts de Playwright que vivem no
scratchpad da sessão de trabalho. Os que importam, e o que cada um prova:

| script | prova |
|---|---|
| `sortida.js` | as fases da missão, a cota de inimigos, a designação que morre com o piloto |
| `escolhe.js` | a seleção de missão dentro do painel |
| `carrega.js` | a aproximação que se carrega, e a cruz que só aparece depois |
| `ctlpainel.js` | cada instrumento está **dentro** do poço que o desenho abriu |
| `ctlsobre.js` | nenhum comando encosta em outro, em quatro aparelhos |
| `multi.js` | as janelas multifunção e a troca de formato |
| `adivivo.js` | a bola do horizonte se mexe (por pixel, não por estado) |
| `radarpac.js` | o contato cai no lado certo do disco, na TV **e** no celular |
| `decola.js` | a decolagem é contínua: mede a velocidade vertical quadro a quadro e cobra que o degrau na saída do chão seja pequeno |
| `pisca.js` | o eco atrasado da TV não desfaz a escolha de formato feita no celular |
| `vistas.js` | as três vistas existem, pintam quadros diferentes, **V** cicla e o pacote leva qual é |
| `monitor.js` | o arranjo de **computador**, com mouse de verdade: clicar escolhe missão, clicar numa aba pula, clicar carrega aproximação, arrastar troca página |
| `arrasta.js` | o arrasto troca o formato **em cada lugar onde a mão pousa** — inclusive em cima da bola |
| `visao.js` | o botão de vista cabe na faixa em três aparelhos e manda `t:visao` |
| `pacote.js` | o pacote do jogo leva a vista (`cab`), interceptando o envio de verdade |
| `cabine.js` | a vista de dentro existe: raio do olho em nove direções (bate na cabine embaixo, no céu em cima), contagem de pixel escuro, as telas do painel pintadas, e a fita de alarmes acendendo com o estado |
| `cabfora.js` | e de fora nada do que entrou fura a lataria ou o vidro, em cinco ângulos |
| `rotulo.js` | o rótulo cabe na coluna que tem, medindo o texto no momento em que ele é desenhado |

**Lição cara, repetida:** asserção de estado não pega "desenhado num ramo que
nunca roda". Quando o defeito é visual, **conte pixels**.

**A terceira:** antes de fotografar um `<canvas>`, **desenhe**. Sem o laço de
animação rodando (ligar `jogando` na mão não o inicia — quem o inicia é
`comeca()`), a tela guarda o último quadro e a foto mostra um estado que já
não existe. Três screenshots seguidas me mostraram a câmera no lugar errado
enquanto a medição dizia o lugar certo — e a medição estava certa.

**A outra, igualmente cara:** quando algo é desenhado com a origem transladada
(cada janela do painel é), tudo o que o desenho **guardar** precisa sair em
coordenada de TELA. Guardar em coordenada de janela é a mesma armadilha de
calcular o radar num lugar e pintar noutro — e ela não dá erro, dá um número
plausível no lugar errado.

---

## Leva: os travamentos e os vazamentos (o "lote 1")

Uma leva inteira de defeito, não de enfeite. Nada aqui muda o que o jogo
parece; tudo muda o que ele faz quando dá errado. Saiu de uma revisão do
jogo inteiro, e passou por duas rodadas de conserto com uma revisão
adversarial no meio.

**O que entrou, e onde mora** (tudo em `jogos/aviao3d.modelo.html` salvo
onde disser outra coisa):

- **`LEME_MIN`/`LEME_MAX` passaram a existir.** Eram usadas como globais e só
  existiam em `controle.modelo.html`. Todo celular lançava `ReferenceError`
  umas 60 vezes por segundo no `devicemotion`, antes mesmo de tocar em
  "Jogar", e o leme por deslize nunca tinha funcionado. Agora são
  propriedades de `Controle`, com os mesmos valores do controle (1,3 e 7,0).
- **`voltaCurta` e `anguloCurto` não travam mais.** Eram `while (g > 180) g -= 360;`
  — com um valor enorme ou infinito, o laço não termina e a aba congela de
  vez. Agora saem por `%`, e devolvem 0 se a entrada não for número finito.
  O mesmo conserto entrou em `aviao.html` (linhas 441 e 1007), que é a fonte
  que a `montar.py` copia para a TV, e em `controle.modelo.html`.
- **A entrada de rede é validada.** `numeroDeRede(x, min, max, padrao)`
  filtra `d.v`, `d.m`, `d.r`, `d.p`, `visao` e `flap` do piloto e do
  artilheiro. Um pacote estragado virava NaN, e em 60 passos a posição, a
  proa, a atitude e os eixos eram todos NaN, sem volta a não ser
  reiniciando. `endireitaEixos()` ganhou a mesma defesa. O mesmo filtro
  entrou em `tv.modelo.html` (linha 381).
- **O botão do sensor não roda o jogo duas vezes.** O sensor do Android leva
  até 5 s para acordar e a tela não dizia nada: a pessoa tocava de novo e
  duas cadeias de quadros ficavam vivas. Agora o botão sai de uso e mostra
  "esperando o sensor… N s", e a trava `lacoVivo` cobre todos os pontos que
  pedem quadro. E se o sensor acordar depois de a pessoa desistir e tocar em
  "dedo", o jogo **não reinicia** mais a partida em andamento: só passa para
  o sensor.
- **Combustível e munição infinitos desligados.** Estavam ligados no que foi
  publicado — as teclas I e M de teste continuavam valendo e tiravam toda a
  pressão do jogo.
- **Geometria deixou de vazar.** `liberaNo`/`liberaNos` liberam geometria e
  material antes de cada `cena.remove` nas sete funções que remontam o mundo
  (`montaPista`, `montaRuas`, `montaAlvos`, `montaNuvens`, `montaGaragem`,
  `montaTrafego`, `montaTrilhos`), sem tocar no que outra peça ainda usa.
  Eram +15 geometrias por partida e +47 por troca de avião. A textura das
  nuvens passou a ser uma só, para sempre, e os inimigos liberam os
  materiais que clonam.
- **Trocar de aba pausa.** Antes o motor continuava roncando e o avião caía
  sem ninguém olhando. Agora o jogo para, o motor desliga e o tom de alvo
  travado e o alarme calam junto — senão o telefone apitava até você voltar.
  Ao voltar, a orientação é reavaliada: girar o celular com a aba escondida
  não religa mais o jogo atrás da tela "gire o celular".
- **O celular abre em médio.** Antes abria em alto em qualquer aparelho (422
  chamadas de desenho e 408 mil triângulos, contra 333 e 232 mil no médio).
  A queda automática agora desce um degrau por vez até o baixo.
- **Sua escolha de qualidade vence.** Se você mexeu no botão alguma vez, a
  queda automática não desfaz mais. Quando ela quereria descer e não desce,
  aparece um aviso âmbar uma vez por partida.
- **A fita de páginas pelo celular passou a funcionar.** O jogo testava o
  campo errado da mensagem (`m.c`, que é a conexão, em vez de `d.c`), então
  rolar as páginas pelo controle nunca tinha feito nada.

**Como desfazer.** Cada item é independente e pequeno; o conjunto inteiro sai
com `git revert` do commit desta leva. Se for só um:

- infinitos de volta: `infinito` e `munInfinita` em `let` perto da linha 1430;
- celular em alto de novo: o bloco de abertura da qualidade, no fim do script;
- pausa ao trocar de aba: o ouvinte de `visibilitychange` com a trava
  `pausadoDeAba`;
- a queda automática voltar a mandar: tirar a consulta a `qualidadeSalva()`.

**A prova.** `scratchpad/lote1.js`, 147 asserções, terminando em `FALHAS: 0`.
Cada bloco foi rodado também contra a montagem anterior e **reprova** lá —
asserção que passa nos dois lados não prova nada. Os testes antigos
continuam verdes (`quadros.js` e `ad02-jogo.js` falham por ambiente, como já
falhavam).

**O que não foi provado aqui:** som em aparelho real, sensor real de Android
ou iPhone, o pedido de permissão do iOS, o ganho de quadros de abrir em médio
e a memória de vídeo de verdade. A renderização desta máquina é por software:
quadros por segundo medidos aqui não valem nada, por isso tudo foi medido em
contagem de chamadas, de triângulos e de geometrias.

---

## A cabine pintada do dragão

A cabine do dragão deixou de ser feita de malha: ela agora é uma **ilustração
fixa na tela**, com a área de vidro recortada. O mundo 3D aparece pelo buraco,
o HUD é desenhado por cima, e as três telas pretas da arte recebem os
instrumentos de verdade — combustível, alvos, pista, alcance —, pintados ao
vivo a cada quadro.

Foi o dono que achou o caminho, depois de cinco levas tentando esculpir uma
cabine com caixa arredondada e tinta chapada: *"eu mandei a foto da porra de
uma cabine para você, era só copiar"*. Ele tinha razão. Fica igual à
referência porque **é** a referência.

**Onde mora:** `jogos/cabine-lucas.webp` é a arte; `CABINE_PINTADA`,
`CAB_PINT_TELAS`, `usaCabinePintada()` e `desenhaCabinePintada()` em
`jogos/aviao3d.modelo.html`; `montar.py` embute a imagem no HTML como data URI,
pela mesma razão do three.js — o jogo tem de abrir sem depender de mais nada.

**Como se faz uma nova:** a arte vem com toda a área de vidro em **magenta
chapado** (#FF00FF) e as telas em **preto chapado**, sem HUD e sem texto. O
recorte é feito fora do jogo, por `scratchpad/cabines/exporta.js`, que troca o
magenta por transparência de verdade e grava WebP. As frações das três telas
saem de `scratchpad/cabines/acha-telas.js`, que varre as regiões pretas da
imagem — medidas, não estimadas. O prompt usado para gerar a arte está no
histórico da conversa.

**Peso:** 258 KB nas quatro imagens (base 193, manche 30, manetes 24, flape 11),
no tamanho original da arte (1846 px) e em qualidade alta —
a 1266 px ela era esticada em monitor e saía borrada. Em PNG seriam 1,8 MB. O
jogo montado foi de 1.681 para 1.963 KB.

**Como desfazer:** `CABINE_PINTADA = false` devolve a cabine de malha, que
continua inteira no código. Apagar `jogos/cabine-lucas.webp` faz o mesmo
sozinho: sem a imagem o jogo cai na de malha e avisa na montagem.

**Ela treme com o avião.** Na cabine de malha isso era de graça: o sacolejo
mexe a posição da CÂMERA, e a cabine de malha é um objeto da cena. A pintada
está colada na tela, fora da cena, então ficava parada enquanto o mundo
sacudia atrás — metade da imagem dizia "levei um tranco" e a outra metade
dizia que não. `tremorDaCabine()` converte o mesmo sacolejo para pixel pela
projeção em perspectiva (a 26 unidades do olho, que é onde o painel está), e a
arte é desenhada com 3% de folga para o tremor não descobrir a borda.
Provado em `scratchpad/tremor.js`, que mede o conteúdo do quadro: parada sem
motivo, seis quadros diferentes com motivo, e parada de novo quando o motivo
acaba.

### As peças que se mexem

> "Cada ação nossa tem que algo se mexendo lá... o trem de pouso, acelerar,
> freiar, flaps, tudo tem que mover na cabine."

Uma pintura é uma folha só, então cada peça que se mexe tem de existir
separada. A arte veio em quatro imagens — a cabine **sem** as peças, mais o
manche, as manetes e a alavanca de flape — e o jogo as empilha:

| peça | comando | o que faz |
|------|---------|-----------|
| manche | `eixos().lat` e `.ver` | gira no pé ao rolar, encurta ao cabrar |
| manetes | `motor` e `turbinando` | correm para a frente do console; pós-combustão leva ao batente |
| flape | `flapAnim` | desce girando no pé, um degrau por posição |

**A ordem de desenho importa e custou uma foto para eu ver:** base → telas
vivas → peças. O manche fica NA FRENTE do painel e as telas estão EMBUTIDAS
nele; desenhadas depois das peças, elas pintavam por cima do punho e o manche
só aparecia do cano para baixo.

**As caixas de cada peça são escolha, não medida.** As peças voltaram
redesenhadas em outra escala e outro lugar — não recortadas no lugar —, então
não havia de onde ler a posição: foram postas olhando, e o manche encolheu
depois de uma foto de perto mostrar que o punho tapava os alvos e a distância
da pista na tela do meio.

Provado em `scratchpad/pecas.js`, que mede pixel na região de cada peça: cada
comando mexe a SUA peça e **não mexe nenhuma outra**, e o mesmo comando duas
vezes dá a mesma imagem.

### Virando a cabeça

Ela era desenhada **colada na tela do navegador**. O mundo girava, o HUD
girava com o nariz, e ela ficava parada — metade da imagem dizia "virei a
cabeça" e a outra metade dizia que não. É a mesma contradição que este arquivo
já tinha diagnosticado para o HUD, e que deu o `presoNoAviao()`.

Agora ela anda junto com o avião, pelo mesmo deslocamento. E some ao virar
muito, porque uma pintura é chata e não tem lateral para mostrar: inteira até
26°, sumindo entre 26° e 42°. Os 26° vieram de olhar a foto — começando em 18°
ela ficava **fantasma** a 25°, com o chão aparecendo através da chapa do
painel, e painel transparente é pior que painel parado.

Provado em `scratchpad/olhar.js`, que mede o painel com e **sem** a cabine:
a 15° os dois quadros diferem (ela está lá), a 50° são idênticos (ela saiu
inteira). Comparar brilho com o mundo não serviria — a 14.000 de altura o
mundo é mais escuro que o painel, e a minha primeira asserção reprovou por
supor o contrário.

**O caça também usa a cabine pintada** agora. Ela valia só no dragão porque a
arte é a do Lucas, azul e amarela; vendo as duas lado a lado, a pintada é tão
melhor que a de malha que a troca de cor vale o preço. Quando o caça tiver a
arte dele, é só escolher a imagem pelo `tipoDeAviao` dentro de
`usaCabinePintada()`.

**O que ela ainda não faz:** a manopla do trem não veio na arte, então o trem
ainda não mexe nada na cabine; os outros botões pintados não fazem nada; e os
controles de toque do celular (PÓS-COMB, METRALHADORA, DEFESA, FOGO e a barra
de potência) são desenhados por cima dela — são botões e precisam ficar
alcançáveis, mas cobrem a cabine e ainda não foram repensados.

### E a cabine de malha melhorou junto
- A lona do painel era 700x178 — proporção de tarja. Com 29 unidades de
  largura isso dava 7,4 de altura, e nenhuma cor nem luz salva sete unidades.
  Agora é 700x300, com três telas no lugar de duas.
- A vista de cabine **nunca teve inclinação de câmera**: havia um
  `if (!cockpit && CAM_INCL)` que a excluía de propósito, e por isso painel,
  manche e console ficavam todos abaixo da linha de visão, fora do quadro.
  São 7 graus, escolhidos varrendo e olhando.
- `CAM_INCL` só era escrito pelas vistas de perseguição, então a vista do
  capacete vinha **herdando** os 3 graus que a vista de fora deixava na
  variável. Agora toda vista escreve o seu, e o capacete declara os 3 que já
  tinha na prática.

---

## O céu ficou alto e o estol afrouxou

> "Melhora a experiência de voo. Tá com muita restrição de queda. Deixe mais
> livre."

**O teto foi de 550 para 3.000 metros.** A faixa de voo inteira tinha 585 m —
menos que a altura de dois prédios do mapa — e dava para encostar no teto numa
subida só. Pior: o "AR RAREFEITO" não era aviso, era uma parede, com o avião
travado em `aviaoY = TETO`.

Agora o limite não é mais parede. Acima do **teto de serviço** (1.500 m) o
motor entrega cada vez menos, até 45% no limite: a subida fica pesada e acaba
sozinha quando a potência deixa de pagar o custo dela. Abaixo disso nada mudou
— e o teto de serviço sozinho já é quase três vezes a faixa de voo antiga.

`TETO_CENA` é novo e guarda a altura antiga: é até onde o mundo é POVOADO
(tambores, helicópteros, aviões parados, caça inimigo). Subido junto com o
teto, o céu de cima ficaria vazio e a subida não teria o que encontrar.

**O estol afrouxou um degrau.** `SUBIDA_CUSTO` foi de 5.800 para 5.200 e
`AFUNDA` de 900 para 680. A escada medida, com manete de cruzeiro, segurando o
ângulo por 6 segundos:

| ângulo | antes  | agora |
|--------|--------|-------|
| 45°    | 1752   | 1921  |
| 55°    | 1492   | 1688  |
| 65°    | 1289   | 1507  |
| 75°    | 1151   | 1383  |
| 90°    | ESTOLA | 1312  |

Ou seja: agora dá para subir na vertical com potência de cruzeiro. A nota
anterior deste arquivo dizia que 5.200 "apagava a gravidade do jogo" — e
dizia certo. **Foi escolha do dono, não descuido**, e fica registrado para
quem vier depois não "consertar" de volta sem saber.

**O que continua doendo:** puxar 40° com a manete fechada ainda estola. Era a
condição que eu não deixaria cair, porque é o erro de verdade.

**Como desfazer:** `SUBIDA_CUSTO` volta a 5800, `AFUNDA` a 900*VEL, `TETO` a
11000, e some o bloco do ar rarefeito. Cada um é independente.

**Medido em** `scratchpad/voo-livre.js`, que roda a montagem publicada e a nova
lado a lado e imprime a tabela acima — a escada não foi sentida, foi medida.

---

## O que está em aberto

- **O jogo não tem nome.** A capa de compartilhamento ainda diz "Avião 3D".
- **A página APROX não baixa o trem.** Na final você está nela e precisa rolar
  até a SINÓT. O checklist TREM/FLAPE/VEL já está lá; falta deixar tocar.
- **O limiar de 350 m da DEFESA AÉREA** pode ser apertado demais para um avião
  de teto 585. Só voando para saber.
- **As duas janelas da TV andam grudadas** ao carrossel: não dá para escolher o
  formato de cada uma, como já dá no celular.
- **`trem.js` acusa três falhas** e já acusava antes desta leva: rajada em
  vagão e em locomotiva não tira vida nem dá ponto. Não é regressão nova; é
  defeito do trem, esperando a vez.
- **Não se vê o bico do avião da cabine**, e não é defeito: o topo do casco
  cai a 20° abaixo da linha do olho e o painel ocupa de 14° a 34°. No vídeo
  do F-16 que serviu de referência também não se vê. Levantar o nariz oito
  unidades resolveria — e seria outro avião.
- **O piloto é só pernas e mãos.** Falta o tronco e o capacete, que só
  aparecem de fora pelo vidro (e na vista do capacete teriam de sumir, senão
  tapam a lente).
- **De cabine, na final, a pista fica baixa.** O painel tapa de uns 15° para
  baixo. Dá para pousar de olho no HUD e na página APROX, mas quem quiser ver
  a pista usa a vista de fora. 
