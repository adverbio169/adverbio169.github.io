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
| `tv3d.js` | **o celular como controle do jogo 3D, de ponta a ponta**: duas abas de verdade e um PeerJS local, do QR até decolar, rolar, recolher o trem e atirar |
| `acesa.js` | a tela não apaga no meio do voo — contra a API de verdade, mais a recusa simulada |
| `pista.js` | sonda: a corrida na pista, para saber quem segura a velocidade (resposta: ninguém) |
| `fumaca.js` | a cabine pintada continua inteira depois de mexer em `comeca()`/`fim()` |

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

**As caixas de cada peça são escolha, não medida** — as peças voltaram
redesenhadas em outra escala e outro lugar, não recortadas no lugar, então não
havia de onde ler a posição. Mas a segunda leitura foi feita com uma GRADE por
cima da arte (`scratchpad/grade.html`), não no olhômetro, e ela mostrou três
coisas:

- o manche estava centrado em 0,491 e o eixo da cabine é 0,500 — um por cento
  à esquerda, o bastante para parecer torto;
- as manetes começavam em 0,660, mas a superfície do console esquerdo só
  começa perto de 0,86: elas **flutuavam**, encostando na moldura da tela da
  esquerda em vez de pousadas na bancada;
- a alavanca de flape estava em 0,660, que ainda é painel — o vão dela começa
  depois de 0,70.

E uma terceira leitura, com os consoles **ampliados**
(`scratchpad/zoom.html`), trouxe a informação que faltava desde o começo: **a
base não tem vão nenhum.** Ao remover as peças, o desenho preencheu os dois
consoles inteiros de chave. Não existe lugar "certo" onde encaixar, e onde
quer que se ponha, a peça pousa em cima de interruptor. O critério deixou de
ser "achar o buraco" e passou a ser **onde uma manete e uma alavanca de flape
são montadas de verdade**: na borda interna do console, junto do fio de luz
azul. Para a cabine ficar perfeita nesse ponto seria preciso pedir ao desenho
uma base com placas lisas e vazias onde as peças se encaixam.

O manche também encolheu, depois de uma foto de perto mostrar que o punho
tapava os alvos e a distância da pista na tela do meio. E o curso dele foi de
12° para **23°**: doze graus é o curso de um manche de verdade e é pouco demais
para ler numa tela de celular com a peça medindo oito por cento da largura.

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

### O acelerador mudou de endereço

A barra de potência do celular ficava na borda direita, **por cima da
cabine**, repetindo o que as manetes pintadas e a tela MOTOR já mostram. Era
o "HUD passando por cima do painel".

Apagá-la deixaria o celular sem acelerador, então ela virou uma **zona
invisível em cima da própria manete desenhada**: o dedo arrasta a alavanca que
está ali, e a alavanca anda. É o mesmo controle de sempre, com o mesmo código
de arrasto — só mudaram o endereço e a aparência (`aceleradorNaManete()` e a
classe `naCabine`).

Dois detalhes que só apareceram testando:

- `valorDoDedo` decide pela FORMA da caixa se o arrasto é vertical ou
  horizontal. Com respiro igual dos quatro lados a zona saía mais larga que
  alta, e o acelerador virou horizontal: tocar no alto da alavanca deixava a
  potência em 0,49. O respiro é desigual de propósito — pouco nos lados,
  bastante em cima e mais embaixo.
- A zona é presa à tela. A sobra de baixo caía fora do visível, e alvo de dedo
  fora da tela não só não existe como encolhe a parte útil do curso, porque o
  valor é lido em fração da caixa inteira.
- **A caixa é garantida em pé por construção**, não por sorte. Ajustar o
  respiro no olhômetro não resolveu: consertada uma vez, ela voltou a ficar
  deitada quando a caixa da manete desceu para o console e encolheu, e o
  acelerador travou em 0,5 de novo. Agora a altura é o que for maior entre o
  desenho com respiro e 1,25 vez a largura, crescendo para cima, onde sobra
  painel e não há nada que o dedo comande.
- A arrumação roda **antes** de qualquer saída da função: trocando para a
  vista de fora, a zona ficava pregada em cima do nada e a barra sumida para
  sempre.

Provado em `scratchpad/acel.js`: a zona contém a manete, está em pé, não passa
da tela, tocar no alto leva a potência a 0,96 e embaixo a 0,04, a alavanca
desenhada anda junto, e sair da cabine devolve a barra ao canto.

### Os botões saíram de cima do painel

> "Retira os botões de cima do painel."

Apagar o controle não dava: no celular deitado o polegar vive nas duas pontas
de baixo, que é justamente onde a cabine está — levar o FOGO para o meio da
tela deixaria o jogo pior de jogar. Então o que sai é o **desenho**. Dentro da
cabine, `#dedos` ganha a classe `semCara`: o vidro, a borda, a sombra e o
texto de PÓS-COMB, DEFESA, FOGO e da caixa da arma somem, e a **área continua
respondendo exatamente no mesmo lugar**. Ao encostar, o botão reaparece, para
o dedo saber que pegou.

Um aviso sai **uma vez por partida** na primeira vez que a cabine aparece:
botão invisível que ninguém avisou é botão perdido.

Provado em `scratchpad/invisivel.js`, que não se contenta com "não é
desenhado": ele pergunta ao navegador quem está no ponto do botão
(`elementFromPoint`) — invisível não pode virar inalcançável — e depois
**aperta cada um**. O FOGO é de segurar, e a primeira versão do teste
reprovou um botão que funcionava porque usava um toque curto, que liga e
desliga antes de dar para medir.

**O que ela ainda não faz:** a manopla do trem não veio na arte, então o trem
ainda não mexe nada na cabine; os outros botões pintados não fazem nada; e
PÓS-COMB, METRALHADORA, DEFESA e FOGO continuam desenhados por cima dela.

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

## O celular como controle do jogo 3D (e a tela que não apaga)

> "Me manda o link para colocar na TV"

**Não precisou ser construído: já estava pronto.** O jogo 3D fala o mesmo
protocolo do jogo 2D, e o `controle.html` que já existia conecta nele sem uma
linha de mudança — está escrito na própria página, perto de `const Tripulacao`.
Vale mais que no 2D, aliás: ali o celular manda inclinação, acelerador, arma e
gatilho; aqui ele manda também **trem, flape, defesa, vista, qualidade do
desenho e o olhar com a cabeça**.

Como se liga: a TV abre `aviao3d.html`, que já abre uma sala com um código de
quatro letras e desenha o QR. O celular lê o QR, cai em
`controle.html?sala=XXXX` com a sala preenchida, e toca em CONECTAR. O primeiro
celular é o **piloto**; um segundo entra como **artilheiro**.

O que eu fiz foi **provar**, e consertar o que a prova achou.

### A prova: `tv3d.js`

Nada de simular o rádio. Um servidor PeerJS local (`broker.js`, o pacote
`peer`) e o jogo apontado para ele com `?servidor=127.0.0.1:9000` — o
parâmetro já existia. Duas abas de navegador de verdade, uma com a TV e outra
com o celular, conversando. Vinte e oito verificações, do QR desenhado até
fechar o celular e o jogo pausar.

Inclusive a **decolagem inteira pelo celular**: acelerar, passar da velocidade
de estol, puxar o manche, sair do chão.

### Duas falhas que eram do teste, não do jogo

A primeira versão reprovou o **rolamento** e o **trem de pouso**. Os dois
estavam certos: o avião ainda estava **no chão**, onde as rodas seguram as
asas niveladas e `mexeTrem` recusa recolher ("no chão, não!"). O teste passou
a decolar antes de cobrar.

A segunda reprovou a corrida na pista com `voo > 1500` — número meu, inventado.
Medido sozinho em `pista.js`, o avião passa do estol em 8 s e decola a 1862,
com nada segurando a velocidade. Quem sabe qual é a velocidade de voo é o
jogo: o teste agora pergunta `velMin()`.

E ainda assim falhava, porque **25 s de relógio não são 25 s de jogo**: `dt` é
limitado a 0,1 s por quadro, então com duas abas em renderização por software o
tempo do jogo corre umas 2,5 vezes mais devagar. O orçamento também não podia
ser chutado.

### O defeito de verdade: a tela apagando no meio do voo

O teste acusou um erro sem dono no celular, e ele era real.

`try { navigator.wakeLock.request('screen') } catch(e){}` **não pega nada**:
`request()` devolve promessa, e a recusa escapa do `try`. O `catch` era
enfeite. Pior: o bloqueio é **solto pelo navegador** quando a aba esconde e
nunca voltava — bastava trocar de aba uma vez para a tela voltar a apagar pelo
resto da partida.

E o buraco maior, que é justo o desta leva: **o jogo 3D não pedia bloqueio
nenhum**. Ele é o que vai para a TV, onde ninguém toca na tela — para o
aparelho, é uma pessoa que foi embora, e o descanso entra no meio da partida.

Agora existe `TelaAcesa` (o mesmo objeto nos três arquivos): pede ao começar,
solta ao acabar, e **pede de novo quando a aba reaparece** — mas só se alguém
tinha pedido antes, senão a capa ficaria com a tela presa à toa.

Onde está: `TelaAcesa` em `aviao3d.modelo.html` (chamado em `comeca()` e
`fim()`), em `controle.modelo.html` e em `aviao-tv.modelo.html` (chamado ao
conectar). **Para desfazer:** apague o objeto e as chamadas; no 3D some o
bloqueio (volta como era), nos outros dois volte a linha única.

Provado em `acesa.js` — contra a **API de verdade**, que existe sim neste
navegador. Minha primeira sonda disse que não existia e estava errada: ela
rodou em `about:blank`, que não é contexto seguro. Servido em `127.0.0.1` a
trava é um `WakeLockSentinel` de verdade. Outro tropeço do mesmo dia:
`navigator.wakeLock = {...}` **não cola** (acessor nativo, não gravável,
falha calada fora do modo estrito) — quem substitui é `Object.defineProperty`.

### Cuidado ao reconstruir: as versões das bibliotecas

O container reiniciou e levou o `node_modules`. Reinstalado solto, o
`montar.py` gerou páginas **4 KB menores** — era `peerjs` 1.5.5 no lugar da
1.5.4 publicada, e `qrcode-generator` 2.0.4 (que mudou `qrcode.js` de lugar,
para `dist/`) no lugar da 1.4.4.

Fixadas em **`peerjs@1.5.4`** e **`qrcode-generator@1.4.4`**, o `tv.html`
reconstruído saiu **byte a byte igual** ao publicado — que é a prova de que as
versões batem. Use isso como conferência sempre que reconstruir: um arquivo
que você não tocou tem de sair com `delta=0`.

---

## A grande revisão — lote 1: os defeitos graves de voo e de combate

> "Revisa aí o jogo que tô tentando fazer. Deixa ele top. Retira os bugs."

Cinco revisores independentes foram soltos sobre o jogo, cada um numa zona.
Dois entregaram antes de o limite de uso da conta cortar os outros três (voo e
combate): 27 achados, **todos reproduzidos rodando o jogo** — os scripts deles
estão em `scratchpad/revisao/voo/` e `scratchpad/revisao/combate/`, e os
relatórios inteiros em `scratchpad/specs/revisao-voo.md` e `revisao-combate.md`.

O que entrou neste lote (tudo em `aviao3d.modelo.html`):

| defeito | causa | onde mora o conserto |
|---|---|---|
| depois da 1ª decolagem, todo toque na pista **relançava o avião** (com 30% de manete: 69 "pousos" e 28 mil pontos em 8 s) | `altChao`/`vyChao` nunca zeravam | `aterra()` zera; `rolagemDePouso` tira a asa na corrida de pouso; pouso só conta depois de 3 s de voo (`tNoAr`) |
| buzina de estol, ronco e tremor **presos no chão** depois de tocar em buffet | só eram desligados no ramo do ar | `calaAsa()`, chamada por `derruba()` e `aterra()` |
| toda morte terminava com **"Acabou o combustível"** | `motivoQueda` era usado como trava e apagava o motivo | `quedaAcabou`; `fim()` ganhou os motivos que faltavam |
| com as rodas no chão **o mundo congelava** (caças, balas, alerta, trem, tráfego) e não se batia em prédio | um `return` antes do fim de `atualiza` | `passoDoMundo(dt)`, chamada do ar e do chão |
| míssil **não travava** e metralhadora não dava solução nos caças da máquina | `Inimigos.lista` não entrava no buscador | `inimigosRede()`; caça ganha `vx/vy/vz` e `vivo = false` ao sair |
| míssil **atravessava o chão** e os prédios, e destruía alvo de chão passando a 450 m | `atingeAlvo` só mede x e z | ramo do míssil em `atualizaTiros` |
| míssil em jogador de rede tirava **135, não 45** | três recados de dano pelo mesmo acerto | `estouraMissil(..., direto)` e `atingeAr(..., semGente)` |
| tiro no vagão feria **o vizinho** (era a pendência do `trem.js`) | volume de acerto cilíndrico maior que o passo entre vagões | caixa alinhada ao trilho em `atingeAr` |
| a nuclear não atingia os caças da máquina | lista não era varrida | `nuclear()` |
| trocar de sortida chamava os caças do BOMBARDEIO com 0/8 | o gatilho lia o contador do voo | `Sortida.alvos0` |

Prova: os scripts dos próprios revisores (`revisao/combate/varios.js`,
`revisao/voo/t3.js`) rodados antes e depois; a régua `envelope.js` mostra o voo
**idêntico** ao de antes (este lote não mexe na física); `fumaca.js`, `acesa.js`
e `tv3d.js` com `FALHAS: 0`.

**Para desfazer:** `git revert` do commit deste lote. Não há chave: são defeitos.

**Ficou para os lotes seguintes** (confirmado pelos revisores, ainda não feito):
caças que matam por abalroamento e quase não ferem na bala; voar abaixo de 45 m
é imunidade; caças não enxergam prédio; não existe vitória de sortida; pane seca
é explosão instantânea; o critério de toque aceita mergulho; e a física inteira
(ver a régua em `scratchpad/envelope-antes.json`).

---

## A grande revisão — lote 2: a física refeita ("Física 2")

> "Refaça a física."

**O que era.** Um avião-flecha: a velocidade *perseguia* um número da manete em
0,4 s, subir descontava uma taxa fixa, e o chão tinha uma aceleração e o ar
outra, sete vezes maior. Inclinar não virava. Medido antes de mexer, na build
publicada (`scratchpad/envelope-antes.json`, régua em `scratchpad/envelope.js`).

**O que é.** A velocidade sai de **uma conta só, a mesma no chão e no ar**:

    dv/dt = RITMO × ( empuxo − arrasto − arrasto induzido − peso na subida )

e a inclinação passou a curvar a trajetória. A *gramática do comando* não
mudou (manche manda taxa, mesmas curvas e zonas mortas): foi afinada com o dono
em várias rodadas. Plano e constantes vieram do revisor de voo
(`scratchpad/specs/revisao-voo.md`), que as derivou das velocidades de hoje.

| medição | antes | agora |
|---|---|---|
| velocidade nivelada, manete 30 / 50 / 70 / 100% | 2048 / 2720 / 3392 / 4400 | 2065 / 2723 / 3392 / 4400 |
| inclinar 60° e **soltar** o manche | 0 °/s, 0,5 g (uma reta inclinada) | **19 °/s, nivelado, 2,0 g** |
| inclinar 45° e soltar | 0 °/s | 10,9 °/s, nariz não cai |
| de faca (90°), mão solta, 3 s | voa de lado para sempre | o nariz cai 22° |
| curva de 60° puxando tudo, 5 s | a velocidade **sobe** 3392 → 3781; 11,7 g | **cai** 3310 → 2075; 7,1 g |
| subida de impulso (cruzeiro, manete fechada, 60°) | estola em 0,6 s | estola em 3,5 s |
| ganhar 500 de cruzeiro com manete cheia | 0,28 s | 2,3 s |
| perder 1000 de cruzeiro fechando a manete | 0,23 s | 1,6 s |
| aceleração logo depois / logo antes de sair do chão | 7,2 vezes | **0,65** |
| sai do chão (manete cheia, meio manche) | 3,8 s | 3,3 s |
| 10% de manete no chão | decola sozinho em 14 s | táxi a 607 |
| manete cheia sem puxar | decola sozinho | não decola |
| tanque seco | explode no ar (e parado na pista) | motor apaga, **plana**; a 10° de nariz baixo voa a 1273 |
| sair do estol (manete cheia, mão solta) | — | 0,9 s |
| looping de cruzeiro | 4,3 s | 4,6 s |
| rolagem com comando cheio | 194 °/s | 195 °/s |

Mais três coisas que deixaram de ser defeito de passagem: o **afundamento**
perto do estol virou velocidade de verdade (`vAfunda` — o variômetro, o alarme
de solo e a régua do toque agora enxergam; cair estolado não rende mais "POUSO
DE MANUAL"); a régua do toque olha o **nariz** ("DE NARIZ NO CHÃO!" abaixo de
12°); e o **leme** perde força com a velocidade em vez de mandar 31 °/s
estolado.

**Onde mora:** o bloco "FÍSICA 2" logo depois de `ACEL_CHAO` (constantes
`F2_*`, `giraMotorF2`, `aceleraF2`); em `atualiza()` os trechos marcados
`if (FISICA2)` (autoridade do profundor, "INCLINAR VIRA", leme, afundamento,
pane seca); em `rolaNoChao()` o motor único e a base de sustentação.

**Os botões que valem a pena conhecer:**
- `F2_RITMO` (2,0) — o "peso" do avião. Multiplica empuxo, arrasto e gravidade
  juntos: encurta ou alonga todos os tempos sem mexer em nenhuma velocidade de
  regime. Achou a manete lenta? Suba. Achou nervoso? Desça.
- `F2_K_IND` (0,28) — quanto a curva apertada cobra em velocidade.
- `F2_FREIO_AR` (1,5) — o freio aerodinâmico que abre com a manete fechada.

**Para desfazer tudo:** `const FISICA2 = false;`. O modelo antigo continua
inteiro nos ramos `else`.

**Prova:** `envelope.js` (antes contra a build publicada, depois contra esta);
`voo2.js` — pousa de verdade na pista com flape 2 e trem e para, sai do estol,
plana sem motor, vira pela inclinação, táxi, e mede o salto de aceleração na
saída do chão; mais `fumaca.js`, `acesa.js`, `tv3d.js` (o celular decola o
avião de ponta a ponta) e os scripts dos revisores, todos com `FALHAS: 0`.

**Um erro meu, registrado:** a primeira régua de subida saía de 20.000 e em
vinte segundos estava a 50.000, no ar rarefeito — e eu li "nariz a 60° fica
pendurado sem subir" como se fosse o avião. Era o motor sem fôlego lá em cima.
Em densidade constante o modelo antigo subia na vertical sem problema. A régua
agora prende a altitude quando o que se mede é regime.

**O que esta fase NÃO fez** (a "fase B" do revisor): o vetor velocidade
continua colado no nariz, então não há ângulo de ataque de verdade nem
derrapagem. O estol ainda é por velocidade, com as regras que o dono pediu
(histerese, asa que larga, nariz que cai para a terra, mais manso perto do
chão).

---

## A grande revisão — lote 3: toque, teclado, rede e robustez

Os três revisores que o limite de uso tinha cortado voltaram e entregaram
(painel, entrada, robustez). Com os dois primeiros são **63 achados**, todos
com reprodução. Este lote fecha os de entrada e de robustez que não são visuais
(os do painel e da capa ficam com os construtores da cabine e da capa).

| defeito | onde mora o conserto |
|---|---|
| no modo DEDO o manche lia sempre o primeiro dedo: arrastar a **manete** era profundor cheio, deslizar a **arma** virava o avião, apertar **FOGO** recentrava o manche e, apertado antes, impedia de pilotar | os ouvintes de `touchstart/move/end`: o manche tem dono (`identifier`) e ignora toque que começa em botão |
| digitar o **código da sala** baixava flape, trocava vista, pedia câmera e ligava munição infinita; Enter no campo começava o voo | `digitando(e)` nos ouvintes de teclado |
| um **nome de jogador** que não é texto congelava o anfitrião e todos os convidados | `nomeDeRede()` (texto, sem marcação, 12 letras) |
| mensagem `apx` com pista inexistente congelava jogo e estado | faixa no `case 'apx'` e cinto em `aproxDados()` |
| posição/eixos de outro jogador entravam crus (NaN na malha; todo tiro "acertava") | validação no topo de `Batalha.poe` |
| dano que não é número deixava o avião **imortal**; negativo curava | `numeroDeRede` em `levaTiro` |
| celular varrido por silêncio continuava pilotando **por fora** da tripulação | readmissão em `Tripulacao.recebe` |
| `Batalha.entra` não desfazia nada ao falhar nem ao trocar de batalha | `entra()`/`hospeda()` e os ouvintes que conferem o dono |
| "SEM SINAL DO CELULAR" **sem saída** | no aparelho de toque o comando volta para a tela; na TV, Enter devolve ao teclado |
| o fim de jogo durante uma pausa era desfeito na retomada | `fim()` limpa as três pausas; `tFim` cancelado em `reinicia()` |
| a **nuclear** sobre a cidade congelava o jogo (238 reconstruções dos telhados: 387 ms; agora 1: 11 ms) | `derrubaPredio(p, emLote)` e `nuclear()` |
| cada **míssil** deixava 9 geometrias na placa para sempre | `liberaNo` ao tirar bomba e cogumelo da cena |
| uma exceção em qualquer ponto do quadro **congelava o jogo** para sempre | `quadro()` embrulha `quadroCorpo()` |
| dois `C` seguidos abriam duas câmeras | trava `_ligando` em `Cabeca.liga` |
| sem servidor de encontro o PeerJS religava a cada segundo, para sempre | espera que dobra até 30 s, nos quatro modelos |

Prova: `scratchpad/lote3.js` (16 verificações que falhavam antes), os scripts
dos revisores `revisao/entrada/a.js` e `b.js` antes e depois, e a regressão
(`voo2.js`, `fumaca.js`, `acesa.js`, `tv3d.js`) com `FALHAS: 0`.

**Para desfazer:** `git revert` do commit deste lote.

**Do revisor de robustez, ainda aberto:** um terço das ordens de desenho vem de
geometria parada (a pista gasta 50 ordens para 124 triângulos; os alvos, 30) —
cabe em 5; a queda automática de qualidade lê tela travada em 30 Hz como
máquina fraca; e uns 72 kB de lixo de memória por passo de física.

---

## A grande revisão — lote 4: a cabine pintada no celular

O revisor de painel achou catorze defeitos; estes seis são os que o dono mais
sente, porque acontecem no celular deitado, dentro da cabine:

| defeito | onde mora o conserto |
|---|---|
| dentro da cabine **não havia comando de trem nem de flape** — na final não dava para baixar o trem sem trocar de vista | CSS: `#dedos.semCara #dTrem, #dFlap` voltam para a faixa de cima |
| a alavanca pintada do acelerador estava **debaixo do seletor de arma** invisível: arrastar a manete trocava de arma (43% da zona no celular de 844) | `aceleradorNaManete()` encolhe o `#dArma` até a borda da zona |
| **metade do HUD ficava atrás da pintura**: G, variômetro, número da altitude e meia fita | `calculaVidroHUD()` sobe a caixa até o topo do para-sol (`CAB_PINT_TOPO`) |
| a **tarja do alarme** era desenhada atrás da chapa: ouvia-se "pull up" sem ler nada | `tarjaDoAlarme()`, chamada depois da pintura, em cima do para-sol |
| a cruz da aproximação e a fita de chamas caíam atrás da chapa | a cruz vai para o centro do vidro; a fita não é desenhada na cabine pintada |
| o **tremor** passava muito da folga (até 869 px) e descobria o mundo na borda | folga de 6% e `tremorDaCabine(c)` saturando nela |
| as janelas 2D, invisíveis na cabine, **continuavam pegando toque** | `mfdPega()`: na cabine respondem as telas PINTADAS, e só ao arrasto de lado (rola a página) |

Prova: `scratchpad/cab4.js` nas duas telas (844x390 com toque e 1280x720), com
captura olhada: `cab4-cel.png` e `cab4-tv.png`.

**Para desfazer:** `git revert` do commit deste lote.

**Do revisor de painel, ainda aberto:** rumo espelhado entre a bússola do HUD e
as páginas VOO e APROX (só norte e sul coincidem), e a VEL da APROX em outra
unidade; a escada de arfagem herda a cor de quem desenhou antes; a fita de
altura passa por baixo de outras coisas; o HUD salta na vertical com o olhar de
cabeça; a página MOTOR diz SEM ALERTAS com alarme tocando; distâncias
sobrepostas na bússola; e, no celular, o texto da página MAPA se sobrepõe nas
telas pintadas (visto na captura).

---

## A cabine do caça ganhou a arte dele

O caça voava sentado na cabine azul e amarela do dragão. A arte própria veio
do ChatGPT do dono, em forma de kit: a cabine vazia sobre magenta, cinco peças
já recortadas (manche, duas manetes, alavanca de flape, alavanca do trem) e
uma máscara para cada tela e cada luz. Duas montagens anteriores, feitas aqui
com peças desenhadas em outro ângulo, foram recusadas ("as peças coladas").
Desta vez as peças são recortes da própria cabine montada: cada uma foi
procurada na imagem montada e bateu com erro zero.

**Antes de entrar no jogo, foi mostrada.** A arte foi injetada na página do
jogo aberta num navegador de teste, sem gravar nada, e o dono escolheu por
foto: cabine inteira na TV, aproximada no celular, só no caça.

### O que entrou

- **Só o caça usa.** O dragão continua na cabine do Lucas, sem mudança
  (o teste mede o enquadramento dele antes e depois).
- **Enquadramento por tela.** A arte é 16:9 e o painel ocupa dois terços dela.
  Em TV e monitor entra inteira. Em tela deitada com proporção de 1,95 para
  cima (celular), é aproximada e presa pelo alto: o topo do painel fica a 46%
  da altura e manche, manetes e flape aparecem pela ponta.
- **As telas são furos.** As laterais são tortas, em perspectiva. O
  instrumento é desenhado por baixo, inclinado junto, e a moldura vem por cima.
- **As peças mexem.** O manche inclina e encurta; as manetes correm pelo
  trilho; o flape vem para trás um dente por posição; a alavanca do trem tomba
  para a esquerda quando ele desce.
- **As três luzes do para-sol são o trem.** Apagadas recolhido, âmbar piscando
  em trânsito, verdes baixado e travado.
- **O acelerador de dedo** mora em cima das duas manetes, como já morava na
  outra cabine.

### Onde mora

- `aviao3d.modelo.html`: o bloco `A CABINE DO CAÇA` (`CAB_CACA`, `cabineCaca`,
  `arteDaCabine`, `topoDaCabine`, `telasDaCabine`, `desenhaCabineCaca`) e o
  ramo do caça em `caixaCabinePintada`. HUD, tarja de alarme e toque nas telas
  agora perguntam a `arteDaCabine()` em vez de assumir a arte do Lucas.
- `montar.py`: seis marcadores `__CABINE_CACA…__`.
- Arte: `cabine-caca.webp` e `cabine-caca-{manche,manete-a,manete-b,flape,trem}.webp`
  (128 KB somados).

### Para desfazer

Em `arteDaCabine()`, devolver sempre `lucas`, e rodar `montar.py`. O caça volta
para a cabine do dragão e nada mais muda.

### O que ficou em aberto nela

- A alavanca do trem é só desenho: tocar nela não baixa o trem (o botão
  invisível do trem continua onde estava).
- No celular, com flape todo baixado, a alavanca de flape quase sai da tela.
- A tarja de alarme é desenhada em cima das três luzes; enquanto ela aparece,
  as luzes do trem ficam tapadas.
- O kit original (PNG sobre magenta e máscaras) não está no repositório; as
  medidas tiradas dele estão em `CAB_CACA`.

---

## O terceiro avião: o "Caça novo" (nome provisório)

O dono adorou o caça azul e amarelo de uma ilustração do ChatGPT (o caça
parado no hangar) e mandou a ficha técnica dele. Primeiro o AD-02 foi
redesenhado por ela; depois veio a decisão: **o AD-02 não muda**, o desenho
novo vira um **terceiro avião** na garagem, ao lado do AD-02 e do dragão.

### O que ele é

- **Cotas da ficha** (20 unidades = 1 m): 16,0 m de comprimento (320),
  12,2 m de envergadura aberta (244), 4,8 m de altura do chão à ponta das
  derivas (96). Medido no modelo montado: 320 x 247 (com as luzes) x 96.
- **Nariz** raso e largo, de dorso chato, com *chines* (aresta viva lateral)
  correndo do bico às tomadas; cone amarelo longo (72 no desenho) e fino na
  ponta, e uma faixa amarela pelo vinco.
- **Cabine**: por dentro é a do AD-02, copiada. A **bolha de fora é dele**
  (`TERCEIRO.BOLHA`): baixa e comprida, assentada no dorso chato, com arco e
  moldura escuros. Ela foi medida em volta do olho do piloto, da câmera do
  capacete, do combinador do HUD, do painel e do apoio de cabeça — tudo fica
  dentro dela (as contas estão no comentário da tabela).
- **Duas tomadas** laterais grandes, quase retangulares, inclinadas, com a
  borda amarela; duas naceles até dois bocais grandes (os mesmos bocais
  variáveis e vetorados do AD-02).
- **Duas derivas** altas, inclinadas 22° para fora e enflechadas 50°, azuis
  com faixa diagonal e ponta amarelas, **cada uma com o seu leme**; os dois
  giram juntos. A altura de 4,8 m foi fechada baixando o corpo e o trem, não
  encurtando a deriva.
- **Motores**: as naceles engordam para trás e os bocais (raio 19 no
  desenho) saem de trás delas e do estabilizador, à mostra entre as derivas.
- **Asa variável de 18°, 38° e 58°**, como na ficha: desenhada aberta a 18°,
  com curso de 0,8 do curso do jogo (`asaVarre`), nasce de um LERX amarelo;
  faixa amarela atrás do bordo de ataque, banda amarela transversal no meio
  do painel e ponta amarela. Estabilizadores com ponta amarela.
- **Trem** com bequilha de rodas gêmeas e duas pernas principais saindo das
  naceles, mais curto que o do AD-02 (o avião é baixo).
- **Os inimigos não mudam**: com o terceiro na garagem, eles continuam sendo
  o AD-02. Os outros jogadores na rede aparecem com o avião escolhido.
- **Cabine pintada**: ele usa a arte de cabine do AD-02 (`arteDaCabine`
  agora pergunta `tipoDeAviao !== 'dragao'`).

### A escala

A cabine do AD-02 tem centenas de números próprios (banco, painel, pernas,
HUD). Em vez de redesenhá-la para um avião de 320, o terceiro é **desenhado
na escala da cabine (514 de comprimento) e encolhido por 320/514 ≈ 0,62** no
fim de `montaTerceiro` — a escala vai para cada filho (o
`poeMalha` reescreve a matriz do avião e jogaria fora uma escala no grupo).
Tudo o que o jogo lê sai em `MEDIDAS_TERCEIRO` já na escala do jogo: roda,
olho do piloto, fogo, pivô e ponta da asa, marca das derivas. O vidro do HUD
(`combinador`) é encolhido em número. Duas coisas do jogo passaram a ler a
escala, e valem 1 para os outros dois aviões: o recuo da câmera do capacete
e o corte de perto das vistas de dentro. E a câmera de perseguição chega
mais perto dele (`MEDIDAS.camera` = 0,78).

### Onde mora

Tudo em `jogos/aviao3d.modelo.html` (rodar `montar.py` depois):

- `MEDIDAS_TERCEIRO` (logo depois de `MEDIDAS_CACA`);
- o bloco `O TERCEIRO AVIÃO` antes de `fazForma`: `anelDeSecao3`,
  `pontoNoCasco3`, `secaoEm3`, `fuselagem3`, `faixaNoCasco3`,
  `convesDaCabine3` (cópias das do AD-02 com a quina dos chines), a tabela
  `TERCEIRO` e `montaTerceiro`;
- `montaDragao(..., tipo)` despacha `'terceiro'`; a capa tem o botão
  `btTerceiro` ("✈ Caça novo"); o `localStorage` aceita `'terceiro'`;
- `giroDaAsa` (curso da asa por avião), o laço dos lemes em `arruma`
  (`comandos.lemes`), `montaDragao` soltando os dois lemes, a marca das
  derivas na rede (`marcaDeriva`), `MEDIDAS.camera` e `MEDIDAS.escala`.

O AD-02 ficou **idêntico** ao commit `b12704b`: `montaAD02`, a tabela `AD02`,
`MEDIDAS_CACA` e todas as funções que ele usa batem byte a byte, e as fotos
do modelo montado saem pixel a pixel iguais.

### Para desfazer

Tirar o botão `btTerceiro` da capa e o `'terceiro'` da validação do
`localStorage` basta para ninguém chegar nele. Para apagar de vez: o bloco
`O TERCEIRO AVIÃO`, `MEDIDAS_TERCEIRO` e o ramo `'terceiro'` de `montaDragao`
e de `montaGaragem`; o resto (`giroDaAsa`, `lemes`, `camera`, `escala`) é
neutro para os outros aviões e pode ficar.

### O pouso que não contava (era o teste)

O `pousos` só sobe quando o avião ficou pelo menos 3 s no ar (`tNoAr >= 3`,
para encostar a roda duas vezes não valer dois pousos). `tNoAr` conta o
tempo do JOGO, e o laço do quadro limita o passo a 0,1 s: numa máquina lenta
(o navegador de teste desenha por software, a uns 3 quadros por segundo) o
jogo anda bem mais devagar que o relógio, e o teste antigo esperava pelo
relógio e ainda teletransportava o avião. O teste novo (`mexe.js` no
rascunho) decola, segura a altura com um piloto automático até `tNoAr`
passar de 3,5 s e desce na própria pista: o pouso conta (`pousos` 0 → 1,
1000 pontos), nos dois caças. O jogo não tinha defeito.

### O que ficou diferente da ficha

- O interior da cabine é o do AD-02 encolhido; a bolha de fora já é a dele,
  mas ainda é uma bolha só (a ficha mostra a capota com mais armação).
- Sem armamento, sem as inscrições e sem o logotipo da ficha.
- Ao fechar a asa a 58°, a raiz do painel mostra um dentinho na quina da
  luva, visível só de cima e de perto.

---

## A capa virou um hangar

A entrada do jogo era uma coluna de caixas sobre um degradê azul. Agora é um
hangar aberto ao pôr do sol (arte do ChatGPT do dono, `capa-hangar-caca.webp`,
165 KB), com o caça parado à direita e o cartão em vidro escuro sobre a parede
vazia da esquerda. Foi mostrado em foto, em cima da capa de verdade, antes de
entrar.

- **Saiu da frente:** o parágrafo de apresentação, o "esta é a tela do jogo",
  a caixa de batalha aérea (continua no botão "Sala · QR e batalha aérea") e o
  aviso de onde se escolhe a missão.
- **Ficou:** QR e código na TV, pista/ar, caça/dragão, os dois botões de jogar,
  o teste do tremor e a ajuda do teclado (rolando dentro do cartão).
- **Cada avião tem o seu hangar:** o mesmo cenário com o avião escolhido
  parado nele (`capa-hangar-caca.webp`, `capa-hangar-terceiro.webp`,
  `capa-hangar-dragao.webp`, todas do ChatGPT do dono, ~170 KB cada). A escolha
  do avião põe a classe `terceiro` ou `dragao` na capa; o `montar.py`
  (`regras_da_capa()`) escreve a regra que troca `--hangar` só quando a arte
  existe. Sem a arte, o avião fica no hangar do AD-02.
- **A vitória tem foto própria:** o hangar fechado da Lotus
  (`capa-vitoria.webp`). O nariz ali está à esquerda, então na vitória o
  cartão vai para a direita (`#capa.vitoria`). Derrota volta ao hangar do avião.
- **No celular deitado** a foto encosta na direita em vez de ser cortada, para
  o focinho do dragão e o nariz do Caça novo não ficarem atrás do cartão. Na
  TV o cartão ficou mais estreito (390 px, 34% da largura) pelo mesmo motivo.
- **Teste:** `capa-tres-teste.js` (três botões, três hangares diferentes;
  vitória; volta na derrota).
- **Onde mora:** o bloco `A CAPA NO HANGAR` no fim do `<style>` de
  `aviao3d.modelo.html`, a linha do `$('capa').classList.toggle('dragao', …)`
  na escolha do avião, e `regra_hangar_dragao()` no `montar.py`.
- **Para desfazer:** apagar o bloco de CSS e rodar `montar.py`.

---

## As missões novas

A leva das missões (commit `6b4cfd1` e os acertos seguintes) juntou cinco
sortidas às quatro antigas, o relatório de fim com estrelas, os anéis do rio,
a página OBJET paginada e os caças inimigos recalibrados. Esta seção diz o que
cada uma pede, onde mora e como sai — e o que a verificação mediu.

### O que cada sortida pede

Todas se escolhem na página **OBJET** com o avião **parado na pista** (a
linha toca `escolheSortida(id)`; com nove sortidas a lista tem páginas de 5,
ou de 3 no celular deitado, e o botão `MAIS MISSÕES ▸` roda as páginas). A
escolha fica em `localStorage` `aviao3d.sortida`.

| id | nome | objetivos | quem chama os caças | perde quando | 3ª estrela | par |
|---|---|---|---|---|---|---|
| `patrulha` | PATRULHA | decolar, 6 alvos, rasar PORTO ALTO, 12 s de rasante, pousar numa avenida, pousar no VALE | ninguém | cai | nenhum pouso duro | 9:00 |
| `defesa` | DEFESA AÉREA | abater 4 caças, voltar e pousar | subir acima de 350 m (depois de 30 s de voo) | cai / abatido | perder < 30 de vida | 5:30 |
| `bombardeio` | BOMBARDEIO | 8 alvos, voltar e pousar | o 3º alvo no chão | cai / abatido | perder < 30 de vida | 5:30 |
| `infiltra` | INFILTRAÇÃO | 18 s abaixo de 200 m sobre PORTO ALTO, voltar | passar 4 s acima de 320 m | cai / abatido | não ser visto | 4:00 |
| `trem` | CAÇA AO TREM | parar a locomotiva, 4 vagões, voltar (4 mísseis, sem nuclear) | o 2º vagão | **o trem some no norte** (~2:35 depois da decolagem) | os 8 vagões | 4:00 |
| `rio` | CORRIDA DO RIO | 8 anéis em ordem, voltar | ninguém | **5:00 de voo** | nenhum anel perdido | 2:50 |
| `exclusao` | ZONA PROIBIDA | 4 helicópteros, voltar (sem nuclear) | o 2º helicóptero | **derrubar um avião de rota** | perder < 30 de vida | 5:00 |
| `alerta` | ALERTA NA PISTA | abater 6 (levas de 1, 2 e 3), voltar | o relógio: 30 s **contando na pista** | cai / abatido | perder < 30 de vida | 7:00 |
| `correio` | CORREIO AÉREO | **parar** no VALE, **parar** numa avenida de NOVA ORLA, voltar | ninguém | **9:00 de voo** | nenhum pouso duro | 5:30 |

"Voltar e pousar" só conta parado em pista (não em avenida), e é sempre o
último: com outro objetivo faltando, a parada só avisa `AINDA FALTA`.

### Onde mora (em `aviao3d.modelo.html`)

- `const SORTIDAS = [...]` — a tabela das nove; os campos opcionais (`par`,
  `limpo`, `armas`, `limite`/`atraso`, `falha()`, `relogio()`, `prepara()`,
  `decola()`, `passo()`, `guia()`) estão descritos no comentário logo acima.
- `OBJ_DEF` — o texto e a meta de cada objetivo; `Missoes` (logo abaixo de
  `Sortida`) marca cada um, e `Missoes.parado()` confere o que depende de
  estar PARADO (as entregas, o "voltar", o conserto na pista).
- `const Sortida` — as fases (solo → trânsito → alerta → quente →
  cumprida/fracassou), o gatilho dos caças e as levas.
- `const Relatorio` — o relógio da sortida, as três estrelas
  (`criterios()`), a melhor marca em `localStorage` `aviao3d.melhor.<id>`
  (`{ e, t }`; só sobe — mais estrelas, ou as mesmas em menos tempo), a
  faixa `MISSÃO CUMPRIDA` e o relatório que entra em `#placar` no fim do voo.
- `const Portoes` — os anéis da CORRIDA DO RIO.
- `mfdPaginaEscolha` / `sorPorPag` / `sorViraPagina` — a página OBJET.
- `CACA_*` e `const Inimigos` — os caças. Não abalroam (o `rompe` é pelo
  tempo até a passagem mais próxima), não descem entre as torres
  (`pisoDeCaca`) e a bala deles não atravessa prédio (`predioNaReta`).

### Como desfazer

- **Uma sortida:** apagar a entrada dela em `SORTIDAS` e rodar `montar.py`.
  Os objetivos de `OBJ_DEF` que sobrarem não fazem mal; quem tinha a sortida
  guardada em `aviao3d.sortida` cai na PATRULHA (a leitura confere o id), e
  a melhor marca `aviao3d.melhor.<id>` fica esquecida no aparelho.
- **A leva inteira:** reverter `6b4cfd1` e os commits de acerto que vieram
  depois dele (o celular-controle também mudou: `controle.modelo.html`) e
  rodar `montar.py`.
- **O conserto das avenidas desta verificação:** tirar as duas linhas
  `if (invadeAvenida(...)) continue;` de `montaMapa` (a função pode ficar).

### A verificação (testes novos, no rascunho `missoes2/`)

Os testes antigos se perderam; estes voam de verdade. `piloto.js` é um piloto
automático que só mexe em `eixos()`, `motor`, `trem`, `flap` e no gatilho —
quem move o avião é `atualiza(1/60)`, chamado em laço (o laço do jogo é
parado: no navegador de teste o tempo de jogo não anda com o relógio).
Pousos, paradas, anéis e decolagens contam pelas regras do jogo, sem
teletransporte.

| script | prova |
|---|---|
| `missoes.js [ids]` | para cada sortida: escolhida **clicando** na OBJET (virando a página da lista quando precisa), objetivos zerados, voada até cumprir, estrelas iguais aos critérios, melhor marca gravada e não sobrescrita por uma pior, relatório com as estrelas acesas, 30 quadros inteiros sem exceção; e um segundo voo que fracassa (pelo motivo da própria sortida quando ela tem um) com o relatório de fracasso e sem gravar marca |
| `cacas.js` | caças: nenhuma batida e a menor distância (reto e em curva), nenhum passo dentro de prédio com o jogador rente sobre PORTO ALTO, e o tiro: 5 balas forçadas a acertar atrás de uma torre não tiram nada; com a reta livre tiram 20 |
| `persegue.js`, `choque.js` | o jogador colado num caça (sem e com tiro): conta batidas |
| `garagem.js` | caça, dragão e terceiro avião numa CORRIDA DO RIO (1º anel) e numa DEFESA AÉREA (caças no céu), com quadros desenhados e o laço de verdade rodando depois |
| `avenida-livre.js` | nenhum prédio sobre o eixo de nenhuma avenida, em 8 mapas sorteados |

O piloto de teste é fraco de combate: nas sortidas com caça ele pode ser
derrubado antes de cumprir, e `missoes.js` tenta de novo (até 5 vezes nas de
combate) e diz em qual tentativa venceu.

**Medido:**

- As nove sortidas foram cumpridas de ponta a ponta pelo piloto de teste,
  com relatório e marca gravada (na última rodada: PATRULHA 3★ 5:39,
  DEFESA 3★ 4:40 na 4ª tentativa, BOMBARDEIO 2★ 4:02, INFILTRAÇÃO 3★ 1:42,
  TREM 2★ 3:03, RIO 3★ 2:05, ZONA PROIBIDA 2★ 2:52 na 3ª, CORREIO 3★ 3:41;
  o ALERTA só numa rodada anterior, ver abaixo); cada uma também fracassou do jeito dela
  (chão, abatido, TREM ESCAPOU aos 2:35, TEMPO ESGOTADO aos 5:00, CIVIL
  ABATIDO, O CORREIO ATRASOU aos 9:00).
- Caças: 6 voos de 2 min com caças em cima, reto e em curva: **0 batidas**,
  menor distância 2195 (o choque é a 731), 49 quebras. 8 voos de 2 min com o
  jogador perseguindo sem atirar: 0 batidas, menor distância 1000. 3 voos de
  150 s rente sobre PORTO ALTO: **0** passos de caça dentro de prédio em
  27 000 (32 000 passos-caça abaixo de 200 m).

### Um defeito achado e consertado: prédio em cima da avenida de NOVA ORLA

`naRua` olhava só o meio da célula onde o prédio nasce; o prédio anda até 160
para o lado e tem até 280 de meia largura, e a caixa dele (desenho e colisão)
é sempre alinhada aos eixos do mundo. Em NOVA ORLA, de grade torta a 35°, a
quina atravessa a avenida. **Medido em 8 mapas: de 4 a 10 prédios sobre o
eixo de cada avenida de NOVA ORLA, em todos; em PORTO ALTO, 0 ou 1.** O piloto
de teste, alinhado no eixo, batia num prédio ao tocar — e o CORREIO pede
PARAR lá. Agora `invadeAvenida()` recusa o prédio cuja caixa (mais a folga de
260 da colisão) entra no asfalto: 0 prédios nas 8 partidas, e as duas
sortidas que pousam em avenida foram cumpridas.

### O que ficou em aberto (das missões)

- **O conserto entre as levas do ALERTA quase não existe.** O respiro entre
  uma leva e a próxima é de 15 s, e o conserto pede o céu vazio e 4 s parado
  na pista. O piloto de teste abateu a 1ª leva e foi direto pousar: levou
  53 e 55 s até parar, a 2ª leva já estava no ar (2 caças) e não houve
  conserto. Só rearma quem já está na final quando o último cai.
  **Mudado depois da verificação:** o respiro virou campo da sortida
  (`caca.respiro`, 15 s por padrão) e o ALERTA usa 70 s — dá para pousar,
  parar 4 s e decolar antes da leva seguinte. Para desfazer, tirar
  `respiro:70` da linha `caca:` do ALERTA.
- **O caça ainda pode ser abalroado por quem o persegue.** Sem o jogador
  atacando, nenhuma batida; mas no combate de verdade o piloto de teste bateu
  3 vezes em umas 25 tentativas. A caixa-preta de uma delas: o caça estava em
  `rompe` (quebrando para o lado, faltando 1,6 s) e o piloto de teste virou
  para dentro da quebra — de 1054 a 780 em 0,1 s. O lado da quebra é escolhido
  uma vez, no começo; quem persegue na direção dela ainda encontra o caça.
- **O ALERTA é a mais difícil:** 6 caças com 8 mísseis; o resto é na
  metralhadora, e o conserto entre as levas não acontece (acima). O piloto
  de teste venceu **uma vez em umas 22 tentativas** (2★, 6:42, 32 de dano);
  nas outras caiu com 1 a 5 dos 6 abatidos, quase sempre no chão, brigando de
  metralhadora. É o piloto de teste que é fraco; um jogador bom deve vencer,
  mas a sortida merece ser jogada por gente antes de ir ao ar.
- **Um estado estranho perto do chão (não é das missões, não foi mexido):**
  nas quedas do piloto de teste na metralhadora (ALERTA), a fita dos últimos
  1,5 s mostra o avião a 80 do chão, **de dorso** (banco de 140° a 160°),
  estolado, com `voo = 0` e o nariz a +0,8, até o nariz passar de -0,30 e
  vir a queda. Parece a regra "quem só raspou ainda pode arremeter" (fora do
  asfalto, só mata com o nariz abaixo de -0,30) segurando no chão um avião
  que tocou de dorso. Não consegui reproduzir de propósito, nem medi quanto
  tempo ele fica ali.
- A página OBJET mostra `LEVA 2 EM 0 s` por um quadro, no instante em que o
  céu esvazia (o `tLeva` só é posto no passo seguinte).

---

## O painel 3D com a cara da cabine nova

"Na visão do capacete ainda tá o painel velho feio." A vista de CABINE cola a
pintura nova por cima e esconde o modelo; a do CAPACETE mostra o modelo, e o
modelo ainda era o da prancha antiga: azul-marinho quase preto, contraluz
azul e uma faixa bege no alto (o degradê quente da lona do painel). Agora o
interior 3D do caça e do terceiro segue a arte aprovada
(`scratchpad/arte-caca2/14.png`), com as cores medidas nela:

- **chapa cinza-azulada**: `mCab` passou de `0x232c3a` para `0x6c6a76`. A
  arte mede `#4f5360` nos consoles; a luz da cena escurece a chapa a uns 70%,
  e com esta base o console sai `#5a5e6e` na foto. A aba do coaming deixou de
  ser preta (multiplicador 0,26 → 0,70).
- **a lona do painel** (`lonaPainelArte`): face `#232737` com chapas,
  costuras e rebites, três molduras GROSSAS (`#35373c`, a do meio maior) com
  um parafuso em cada canto, grades embaixo. Sem luz própria — o fio quente e
  a contraluz azul saíram.
- **o tampo dos consoles** (`lonaConsoleArte`): o cinza claro da arte, com
  rebites e o trilho da manete / do flape; a borda de fora é um vinco escuro.
- **a placa do para-sol com as três luzes do trem**, pregada na cara da aba
  que olha para o piloto: apagadas (`#381613`) com o trem recolhido, âmbar
  piscando em trânsito, verdes com ele baixado — a mesma regra de
  `desenhaCabineCaca`, lida de `tremAnim` em `acendeLuzesTrem`.
- **as laterais**: uma luz laranja e uma grade de cada lado, junto da parede
  logo atrás do painel, e a face de dentro dos consoles em verde-água
  (`#30454c`, por cor de vértice, sem tinta nova).

**Onde mora.** Tudo no `aviao3d.modelo.html`, na seção "O PAINEL DA ARTE
NOVA" (logo antes de `lonaConsole`): `PAINEL_ARTE`, `ARTE_CAB`,
`lonaPainelArte`, `vestePainelArte` (as peças, uma função só chamada pelo
`montaAD02` e pelo `montaTerceiro`), `escureceFora`, `tinge`,
`acendeLuzesTrem` e `lonaConsoleArte`. As luzes acendem no laço, logo depois
da linha do `tremAnim`. O dragão tem cabine própria e não mudou.

**O que não mudou.** O combinador, o olho, as telas vivas, o manche, a
manete e o corte de perto das câmeras ficaram onde estavam: as peças novas
são acréscimo. O inimigo usa o AD-02 `simples`, sem cabine: continua com 130
malhas, 16 materiais e 16.418 triângulos.

**Custo.** Duas tintas novas (as luzes do trem e a laranja); todo o resto é
`mCab` e se emenda no `fundePorCor`. Medido na vista do capacete, só o avião:
caça 27 → 29 chamadas, terceiro 24 → 26 (76 → 80 e 74 → 78 contando a
passada de sombra). A cena inteira fica em torno de 200 e varia mais que isso
de uma carga para a outra.

**Ficou diferente da arte.** As telas laterais não são inclinadas (as telas
vivas não podiam mudar de lugar); o para-sol não sobe em corcova acima do
painel (subiria na frente do vidro do combinador) — a placa das luzes fica na
cara da aba; o verde-água quase não aparece, porque as pernas do piloto tapam
a face de dentro dos consoles; e o trilho da capota continua escuro, porque
aparece por fora do avião.

**Para desfazer:** `const PAINEL_ARTE = false;` — volta a lona antiga, a cor
antiga de `mCab`, a aba e o trilho escuros, e as peças novas não nascem.

---

## A vista do capacete ganhou a pintura dela

**O que mudou.** No caça e no terceiro, a vista do CAPACETE (a terceira do
botão de vista) deixou de mostrar o avião 3D e passou a mostrar a arte 2D
feita para ela: o arco inteiro da canópia, o painel com três telas e três
luzes, as manetes, o manche, o flape, a alavanca do trem e o encosto do
banco. Ela faz o que a pintura da CABINE já fazia:

- as três telas são **furo** e o instrumento vivo é desenhado por baixo,
  inclinado junto com a moldura;
- as três luzes do topo são o **trem**: apagadas recolhido, âmbar piscando em
  trânsito, verdes baixado;
- as **peças mexem**: o manche inclina ±0,40 rad e encurta 20% puxado (em
  volta do colarinho, para não sair de cima da coifa); as manetes correm pelo
  trilho com a potência (a arte as mostra no meio, que é a potência 0,5); o
  flape anda um dente por posição; o trem tomba e desce quando baixa;
- o **HUD** termina acima da chapa, a **tarja de alarme** vai por cima da
  caixa das luzes (nunca atrás da pintura), tocar numa tela pintada **pega a
  tela**, o **acelerador de dedo** mora em cima das manetes, a pintura
  **treme** com o avião e **esmaece** quando se vira a cabeça;
- **enquadramento**: na TV a arte entra inteira, com o arco da canópia
  cabendo; no celular deitado ela é aproximada — painel a 44% da altura e as
  placas das alavancas no rodapé — e o arco e o banco saem pelas bordas.

O dragão não mudou: o capacete dele continua em 3D. Se a arte não carregar,
volta o painel 3D da seção anterior (`PAINEL_ARTE`), que ficou como estava.

**Como a arte foi montada (e por que assim).** Peças geradas em separado e
coladas por cima "parecem coladas" — já foi recusado. Então a **base é a
própria arte montada**, e cada peça que mexe é um **recorte dela** (só a
parte que anda: a alavanca, nunca a placa do trilho), por polígono medido
numa grade por cima da arte. Parada, base + peça é a arte original. O buraco
que a peça deixa ao andar foi tapado, só ali dentro, com a versão **vazia**
da mesma arte, deslocada de 0 a 3 px para casar com a montada em volta de
cada peça (as duas não são iguais pixel a pixel). As peças soltas grandes não
foram usadas. Tudo isso está no scratchpad (`capacete2/gera.js` e
`capacete2/pecas.js`, com os polígonos).

**Onde mora.** `jogos/capacete-caca.webp` (a base: magenta transparente e as
telas furadas, 98 KB) e `jogos/capacete-caca-{trem,manetes,flape,manche}.webp`
(as peças, 13 KB juntas), embutidas pelo `montar.py`. No
`aviao3d.modelo.html`, a seção "O CAPACETE PINTADO" (logo depois de
`telasDaCabine`): `CAPACETE_PINTADO`, `CAP_CACA` (telas, luzes, peças, caixa
das manetes, lugar da tarja), `capaceteCaca`, `vistaDoCapacete` e
`kitDaArte`, que diz qual kit é a arte e deixa `topoDaCabine`,
`telasDaCabine`, `desenhaCabineCaca` e `aceleradorNaManete` servirem às duas
pinturas. As peças mexem em `pecasDoCapacete`; o enquadramento está no
começo de `caixaCabinePintada`. `usaCabinePintada` e `arteDaCabine`
passaram a responder também na vista do capacete — é por isso que o HUD, a
tarja, o toque, o acelerador, o tremor e o esmaecer vieram de graça.

**Ficou diferente da arte.** Movida, cada peça deixa à mostra o desenho da
arte vazia, que não é o mesmo da montada: atrás da alavanca do trem aparece
uma placa de ponta (a da arte vazia), e as fendas das manetes têm um degrau
miúdo onde as duas artes se encontram. A tarja de alarme tapa as luzes do
trem enquanto apita. No celular o arco da canópia não aparece inteiro.

**Para desfazer:** `const CAPACETE_PINTADO = false;` — a vista do capacete
volta a ser 3D em todos os aviões, e a cabine não muda nada.

---

## As três luzes do painel: uma por função

As três luzes do para-sol (na cabine pintada, na vista do capacete e no
painel 3D) eram as três do trem. A pedido do dono, cada uma ganhou uma função
e o nome escrito dentro dela:

- **TREM:** apagada recolhido, âmbar piscando em trânsito, verde baixado.
- **FLAPE:** apagada recolhido, âmbar piscando enquanto anda, verde baixado.
- **PÓS:** verde com a pós-combustão acesa, âmbar piscando com o nitro abaixo
  de 20%, apagada no resto.

Onde mora: `estadoDasLuzes()` e `LUZES_NOMES`, logo antes de
`desenhaCabineCaca`, usados pela pintura e por `acendeLuzesTrem` (o painel 3D
ganhou uma tinta por luz). Teste: `luzes3.js`. Para desfazer: devolver o
estado do trem nas três posições de `estadoDasLuzes()`.

---

## O HUD sem a caixa das réguas, e dentro do vidro

Pedido do dono: "essa barrinha tipo régua não tá legal" e, logo depois, "as
informações da régua ficam, tira só o sombreado que faz a forma da régua". E:
"o HUD tem que encaixar no vidro, o HUD da cabine tá passando".

- **As réguas sem caixa.** A bússola (fita do rumo) e a fita da altitude
  perderam só a tarja escura e o contorno verde. Riscos, NO/N/NE, o número do
  rumo, os números da altitude, o variômetro, o ponteiro e as setas de alvos e
  pistas com a distância continuam. Para ler contra nuvem, o texto ganhou um
  contorno escuro fino (`textoNoCeu`) e os riscos uma sombra de 2 px.
- **As três vistas iguais.** Mira, escada de arfagem e G passaram a existir
  também na vista de fora e no capacete (eram só da cabine). A cruz do míssil e
  da nuclear agora sai da projeção do cano, como a da metralhadora: no meio da
  tela ela ficava atrás do painel desde que a câmera da cabine olha 7° para
  baixo.
- **O HUD cabe no vidro** (CABINE e CAPACETE do caça e do terceiro). Cada
  kit de pintura ganhou `vidro` (o polígono do vidro em pixel da arte, entre as
  colunas do arco e acima do painel, medido no magenta e encolhido 10 px) e
  `hud` (a caixa dos números dentro dele). `calculaAreaVidro()` leva os dois
  para a tela com a mesma conta da pintura (caixa, tremor do quadro,
  `hudDX/hudDY`), e todo o HUD é desenhado com recorte nesse polígono
  (`abreVidro`/`fechaVidro`). A escada fica mais estreita, os números se
  arrumam na caixa, e a mira, quando o nariz cai atrás do painel, encosta na
  borda de dentro com o anel tracejado (batente). Alarmes, tarja, avisos e as
  janelas das telas ficam de fora do recorte. Com a cabeça virada (pintura
  abaixo da metade) e no dragão, o HUD segue o vidro 3D de antes.

Onde mora: `REGUA_COM_FUNDO`, `textoNoCeu`, `bussola`, `fitaAltura`;
`CAB_CACA.vidro/hud`, `CAP_CACA.vidro/hud`; o bloco "O HUD CABE NO VIDRO"
(`HUD_NO_VIDRO`, `calculaAreaVidro`, `abreVidro`, `cabeNoVidro`) logo depois de
`calculaVidroHUD`; e `desenhaHUD`. Medida do vidro: `scratchpad/hud2/mede-vidro.js`.
Teste: `scratchpad/hud2/teste.js` (pixels do HUD fora do vidro: 74.369 antes,
0 depois).

Para desfazer: `REGUA_COM_FUNDO = true` traz as caixas de volta;
`HUD_NO_VIDRO = false` desliga o recorte e a caixa volta a ser a do
combinador. A mira, a escada e o G nas três vistas voltam a ser só da cabine
trocando `if (cockpit || (jogando && !caindo))` por `if (cockpit)` em
`desenhaHUD`.

---

## Os lados do celular e mais céu na cabine

Três pedidos do dono, juntos.

**1. "O controle do celular e do cockpit têm que ter a mesma ordem."** Na
cabine pintada as manetes ficam à esquerda; no celular o acelerador estava na
borda direita. Mudou o celular:

- **Celular como controle da TV** (`controle.modelo.html`): o acelerador foi
  para a borda ESQUERDA e o nitro para a DIREITA, ao lado do FOGO. As duas
  colunas têm a mesma largura, então só trocaram de borda em
  `Painel.regioes()`; o seletor de arma ficou à esquerda (com o polegar da
  manete, que arrasta) e o FOGO e a DEFESA à direita (com o nitro: tudo que se
  aperta). De quebra, o painel **em pé** (página girada por CSS, "preso
  deitado") saía com a forma trocada — lona de 390x844 dentro de uma página
  de 844x390, alavancas viradas em faixas e os botões de cima empilhados.
  Agora a lona mede pelo leiaute (`clientWidth`), o painel é 100% do pai
  girado, a fila de botões anda pelo `left` que ela mesma escreveu, e o toque
  nas janelas converte a coordenada da tela para a da página (`local()` em
  `gestoDoPainel`). O aviso "preso deitado" sai voando (volta na engrenagem).
- **Celular jogando direto** (`aviao3d.modelo.html`, modo de dedo): fora da
  cabine, a barra do acelerador (`#dAcel`) foi para a borda esquerda e o nitro
  (`#dNitro`) para a direita. Na cabine e no capacete o acelerador continua
  sendo a zona invisível em cima das manetes pintadas (`aceleradorNaManete`).

Para desfazer: trocar `pot` e `nitro` de borda em `Painel.regioes()`
(controle) e o `left`/`right` de `#dAcel` e `#dNitro` (jogo).

**2 e 3. "A visão do capacete muito embaixo" e "o cockpit ocupa muito a
tela".** O topo do painel pintado estava a 35% da altura (cabine, TV), 46%
(cabine, celular), 40% (capacete, TV) e 44% (capacete, celular), e a mira caía
atrás do painel nas quatro, sempre no batente. Testadas as duas hipóteses:
subir a câmera do capacete (`VISTAS`, `cima` 9 -> 24) não muda nada que se
veja, porque a pintura é um quadro colado na tela e o horizonte e a mira estão
no infinito; descer o quadro da pintura resolve. O quadro agora é escolhido
pela fração da altura onde cai o topo do painel, com a menor escala que cobre
a largura (4% de folga para o tremor), ancorado nesse topo:

| variante | cabine TV | cabine celular | capacete TV | capacete celular |
|---|---|---|---|---|
| hoje (antes) | 0,35 | 0,46 | 0,40 | 0,44 |
| **A (no ar)** | 0,48 | 0,50 | 0,54 | 0,56 |
| B (mais céu) | 0,56 | 0,54 | 0,62 | 0,62 |

Com A e com B a mira sai do batente nas quatro telas. Na cabine as colunas da
canópia saem pela borda de cima da arte; com o quadro mais baixo elas são
prolongadas até o alto da tela (`prolongaArco`, inclinação `CAB_CACA.arco`) e
o vidro do HUD sobe junto (`calculaAreaVidro`). No capacete o arco fecha
dentro da folha e acima dele é céu. Em B, no celular, a cabine fica com as
manetes quase fora da tela (a zona do acelerador continua lá). O capacete 3D
do dragão não mudou.

Onde mora: bloco "MAIS CÉU NA CABINE E NO CAPACETE PINTADOS", logo antes de
`caixaCabinePintada` (`ENQUADRA_PADRAO`, `ENQUADRAMENTOS`, `caixaPeloTopo`,
`prolongaArco`; o quadro antigo inteiro em `caixaAntiga`). O tremor passou a
não sacudir além da sobra de baixo. Para comparar sem mexer no código:
`aviao3d.html?enquadra=B` (ou `=HOJE`). Para escolher B:
`ENQUADRA_PADRAO = 'B'`. Para desfazer: `ENQUADRA_PADRAO = 'HOJE'`.

Testes: `scratchpad/lados/teste.js` (lados, sobreposição, arrasto do
acelerador, topo do painel em cada vista, tela e variante, cobertura, mira,
colunas, telas tocáveis). Fotos: `scratchpad/lados/`.

---

## O que está em aberto

- **A ou B?** O enquadramento da cabine e do capacete pintados tem duas
  variantes (ver "Os lados do celular e mais céu na cabine"); está no ar a A.
  O dono escolhe olhando `aviao3d.html?enquadra=B`.
- **O jogo não tem nome.** A capa de compartilhamento ainda diz "Avião 3D".
- **A página APROX não baixa o trem.** Na final você está nela e precisa rolar
  até a SINÓT. O checklist TREM/FLAPE/VEL já está lá; falta deixar tocar.
- **O limiar de 350 m da DEFESA AÉREA** pode ser apertado demais para um avião
  de teto 585. Só voando para saber.
- **As duas janelas da TV andam grudadas** ao carrossel: não dá para escolher o
  formato de cada uma, como já dá no celular.
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
