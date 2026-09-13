# Como o celular vira controle

Resposta curta para a pergunta "isso é possível?": **sim, e sem instalar nada.**
Todo navegador de celular avisa a inclinação do aparelho. Você escuta esse aviso
e usa o número como se fosse um analógico de videogame. É isso — o resto é jogo
comum, desenhado no `<canvas>`.

## O evento

```js
window.addEventListener('deviceorientation', (e) => {
  e.beta    // inclinação da frente para trás, em graus
  e.gamma   // inclinação de um lado para o outro, em graus
  e.alpha   // giro tipo bússola
});
```

Três regras que economizam muita dor de cabeça:

1. **Não use `alpha`.** É o giro em torno do eixo que sai da tela — parece o
   movimento natural de um volante, mas depende de bússola, deriva sozinho e
   varia de aparelho para aparelho. Volante de verdade se faz com `beta`/`gamma`.
2. **Só funciona em `https`** (ou em `localhost`, ou em arquivo aberto
   localmente). No GitHub Pages funciona, porque o Pages é https.
3. **No iPhone e iPad são DUAS permissões**, e as duas só são aceitas se o
   pedido sair de um toque do usuário — por isso o pedido fica dentro do clique do
   botão "Jogar", nunca no carregamento da página:

```js
if (typeof DeviceOrientationEvent.requestPermission === 'function') {
  const r = await DeviceOrientationEvent.requestPermission();
  if (r !== 'granted') { /* cai para o controle por toque */ }
}
// A SEGUNDA, fácil de esquecer: sem ela o evento devicemotion nunca dispara,
// e é dele que sai a gravidade que descobre se o celular está deitado.
if (typeof DeviceMotionEvent !== 'undefined' &&
    typeof DeviceMotionEvent.requestPermission === 'function') {
  await DeviceMotionEvent.requestPermission();
}
```

No Android as duas vêm liberadas juntas, então o esquecimento não aparece —
só no iPhone, e só quando a rotação da tela está travada.

## A pegadinha principal: beta e gamma trocam de lugar

`beta` e `gamma` são medidos em relação ao **aparelho**, não à tela. Quando a
pessoa deita o celular para jogar, a tela gira mas os eixos do aparelho não.
Resultado: o controle inverte, ou o "volante" passa a levantar o nariz.

A correção é olhar para `screen.orientation.angle` e converter. É o que a função
`eixos()` faz nos dois jogos:

| tela | volante (virar para os lados) | manche (nariz sobe/desce) |
|---|---|---|
| retrato (0°) | `gamma` | `beta` |
| paisagem (90°) | `beta` | `-gamma` |
| paisagem (270°) | `-beta` | `gamma` |
| retrato invertido (180°) | `-gamma` | `-beta` |

Depois dessa conversão, **volante** é sempre "girar em torno do eixo vertical da
tela" e **manche** é sempre "girar em torno do eixo horizontal da tela", não
importa como a pessoa esteja segurando o aparelho.

Para conferir isso no seu celular, abra `testar-sensor.html`: ele mostra os
números crus, os convertidos e o ângulo da tela, ao vivo.

## Os três ajustes que fazem o controle parecer bom

Sensor cru não é controle. Sem estes três tratamentos, o jogo parece quebrado
mesmo estando certo:

**1. Calibragem (zerar na mão de quem joga).** Ninguém segura o celular
perfeitamente na horizontal. Na hora de começar, guarde a leitura atual e
subtraia dela para sempre:

```js
zero = leituraAtual;          // uma vez, ao começar
valor = leituraAtual - zero;  // todo quadro
```

**2. Zona morta.** Abaixo de uns 2 a 3 graus, ignore: é o tremor da mão.

**3. Teto.** Escolha o quanto a pessoa precisa inclinar para ir ao máximo — uns
20 a 25 graus é confortável — e transforme graus em um número de −1 a 1:

```js
function grausParaEixo(graus, maximo, zonaMorta){
  const s = Math.sign(graus), g = Math.abs(graus);
  if (g <= zonaMorta) return 0;
  return s * Math.min(1, (g - zonaMorta) / (maximo - zonaMorta));
}
```

Esse −1 a 1 é o que o jogo consome. A partir daí o sensor desaparece do
problema: é igual a uma seta do teclado, só que analógica.

## Exemplo mínimo que funciona

Uma bolinha que corre atrás da inclinação. Salve como `.html`, publique e abra
no celular:

```html
<canvas id="c" style="width:100%;height:100vh;display:block"></canvas>
<button id="b" style="position:fixed;top:10px;left:10px">ligar</button>
<script>
const c = document.getElementById('c'), x = c.getContext('2d');
let g = 0, bx = 0;
c.width = innerWidth; c.height = innerHeight;

document.getElementById('b').onclick = async () => {
  if (typeof DeviceOrientationEvent.requestPermission === 'function')
    await DeviceOrientationEvent.requestPermission();
  addEventListener('deviceorientation', e => { g = e.gamma || 0; });
  document.getElementById('b').remove();
};

(function laco(){
  bx += (g / 45) * 8;                                   // inclinação -> velocidade
  bx = Math.max(-c.width/2, Math.min(c.width/2, bx));
  x.fillStyle = '#111'; x.fillRect(0, 0, c.width, c.height);
  x.fillStyle = '#5cc8ff';
  x.beginPath(); x.arc(c.width/2 + bx, c.height/2, 26, 0, 7); x.fill();
  requestAnimationFrame(laco);
})();
</script>
```

## Sempre deixe uma saída

Tem celular sem giroscópio, tem permissão negada, e tem gente que vai abrir no
computador. Os dois jogos aqui esperam 1,2 segundo pela primeira leitura; se não
vier nada, avisam e oferecem o controle por toque. Teclado funciona no
computador. Sem isso, o jogo simplesmente não abre para parte das pessoas e
você não descobre por quê.

## Onde está cada coisa nos jogos

| arquivo | o que tem dentro |
|---|---|
| `corrida.html` | Parte 1: controle &middot; Parte 2: a pista (lista de segmentos com curva e altura) &middot; Parte 3: desenho em falsa perspectiva |
| `aviao.html` | Parte 1: controle (idêntica) &middot; Parte 2: o mundo e a projeção &middot; Parte 3: desenho &middot; Parte 4: regras |
| `testar-sensor.html` | só o sensor, com os números na tela — para depurar no aparelho |

A "Parte 1" é igual nos dois arquivos de propósito: é o pedaço para copiar no
próximo jogo.

## As regras do avião

O jogo é sobre **combustível**, não sobre pontos:

| coisa | o que faz |
|---|---|
| tanque | começa em 100% e cai **3,3% por segundo** — dá uns 30 s de voo |
| tambor **amarelo** | devolve **20%** |
| tambor **azul** | devolve **32%** e liga o **turbo por 5 s**: o avião vai de 1700 para 3000 de velocidade, com clarão, partículas, riscos na tela e um selo TURBO no painel |
| turbo | enquanto dura, gasta 5%/s em vez de 3,3% — anda muito mais, mas custa caro |
| **pombo** e **avião** | bater em qualquer um derruba: explosão, o avião roda e cai até o chão |
| tanque vazio | o motor morre, o nariz cai e o avião despenca — explode ao bater no chão |
| placar | **distância em metros**; o recorde também |

O **teto** fica em 5200 (uns 1475 m no altímetro) e é macio: perto dele o ar
rarefaz e o avião para de subir aos poucos, com aviso na tela. Os tambores, em
compensação, só nascem até 2600 — subir muito é uma escolha que deixa o
combustível para trás, não um limite do jogo.

O **som do motor** é feito na hora, sem arquivo nenhum: duas ondas graves (o
ronco), **uma terceira voz aguda** e ruído filtrado (o ar). A terceira voz não é
enfeite: alto-falante de celular e de TV quase não reproduz abaixo de 400 Hz, e
sem ela o motor fica inaudível fora de um fone. Medindo a energia acima de
400 Hz, ela dobra o que se escuta (0,032 para 0,071). A altura do ronco acompanha a velocidade, o
motor engasga quando o tanque está no fim e morre escorregando para o grave na
queda. O botão 🔊 no canto liga e desliga, e a escolha fica guardada.

A dificuldade cresce sozinha: quanto mais longe você chega, mais obstáculos
aparecem, e mais deles são aviões (que são bem maiores que os pombos).

Os números todos ficam juntos no começo do núcleo, com nome: `GASTO`,
`DA_NORMAL`, `DA_AZUL`, `TURBO_SEG`, `VOO_BASE`, `VOO_TURBO`, `RAIO_PEGA`.
Mexer no equilíbrio do jogo é mexer nessas linhas.

## Ideias de próximo passo

- **Trocar o desenho do carro pelo personagem da sua filha.** No `corrida.html`,
  a função `desenhaCarro()` desenha tudo à mão; troque por uma imagem
  (`ctx.drawImage`) e o jogo inteiro continua funcionando.
- **Dois jogadores no mesmo celular** não dá com inclinação, mas dá com um
  celular controlando o jogo que aparece na TV — aí já entra rede, e é um
  projeto bem maior.
- **Vibração** nas batidas: `navigator.vibrate(120)` funciona no Android.

## O celular como controle, o jogo na TV

É o modelo Jackbox / AirConsole, e são dois arquivos:

| arquivo | onde abrir | o que faz |
|---|---|---|
| `aviao-tv.html` | **nos dois** | um arquivo só: descobre sozinho se é a tela, o controle, ou os dois |
| `tv.html` | monitor, TV, notebook | a versão separada: só a tela |
| `controle.html` | celular | a versão separada: só o controle |

**O `aviao-tv.html` decide o papel assim**, na ordem:

1. foi a TV que abriu a página (Chromecast) → é a **tela**, e já nasce conectada;
2. endereço com `?papel=tela` → é a **tela**;
3. endereço com `?sala=ABCD` → é o **controle**, com o código preenchido;
4. tela grande e sem toque (um computador) → é a **tela**, sem perguntar;
5. resto (um celular) → **pergunta**, e o botão de enviar para a TV vem primeiro.

### O botão "Enviar o jogo para a TV"

Usa a **Presentation API** — a mesma coisa que o ícone de transmitir do YouTube.
O celular manda a TV abrir esta página com `?papel=tela`, e o canal de conversa
entre os dois é criado pelo próprio navegador: **sem código de sala, sem digitar
nada**. Duas exigências, e nenhuma delas está no meu código:

- a TV precisa ser **Chromecast, Google TV, Android TV** ou equivalente
  (**Samsung não é** — usa sistema próprio e o botão não a enxerga);
- a página precisa estar num endereço **https** de verdade, porque quem vai
  buscá-la é a TV. Arquivo no celular não serve para esse botão.

Quando não dá, o botão some sozinho e sobram os outros caminhos.

**Como os dois se acham.** Cada um abre uma conexão **WebRTC** — os aparelhos
falam direto entre si pela WiFi, com uns 5 a 20 ms de atraso. Só para se
encontrarem pelo código eles passam por um *servidor de sinalização*: por
padrão, o servidor público do PeerJS (precisa de internet nos dois aparelhos,
mas só naquele instante). Depois disso, o tráfego é local.

Para usar um servidor próprio — numa rede sem internet, por exemplo — abra os
dois com `?servidor=ip:porta` e rode `npx peerjs --host 0.0.0.0 --port 9000 --path /sinal`.

**O que viaja pela rede.** O celular manda `{t:'eixo', v: volante, m: manche}`
em graus, já calibrados. A TV manda de volta o placar a cada 250 ms, e o celular
vibra quando o número de argolas sobe. Se o sinal cair por 2 segundos, a TV
pausa; quando o celular volta, continua de onde parou.

**A regra de ouro continua valendo:** a página do celular precisa estar num
endereço `https` de verdade (ou aberta como arquivo local pelo `file://`),
porque é ela que lê o sensor. A página da TV não lê sensor nenhum — pode ser
aberta até com dois cliques num arquivo.

**Como o jogo entrou lá dentro.** `tv.html` é o `aviao.html` com uma troca: o
objeto `Controle` não lê o sensor, recebe os ângulos pela rede. O núcleo do jogo
(mundo, desenho, regras) é copiado sem alteração pelo `montar.py`. Para mudar o
jogo, mude `aviao.html` e rode o script — `tv.html` acompanha. As bibliotecas
(PeerJS e o gerador de QR) ficam embutidas, para cada página ser um arquivo só.

**Mais controles** é o próximo passo natural: a sala já aceita conexões; o que
falta é a TV manter um avião por conexão e o jogo desenhar todos.

### Qualquer TV: os três caminhos, do melhor para o pior

Não existe **um** mecanismo que alcance toda TV — cada fabricante escolheu o seu.
Então o `aviao-tv.html` cobre os três, e o que estiver disponível aparece:

**1. Chromecast embutido** (Google TV, Android TV, Chromecast na HDMI, a maioria
das TCL, Sony, Philips). O botão *Enviar o jogo para a TV* aparece sozinho no
celular, a TV abre o jogo e o celular vira controle. Sem código, sem digitar.
É o caminho bom.

**2. Navegador da própria TV** (Samsung, LG e qualquer TV com browser). A TV
abre a página como tela; o celular entra pelo código. Digitar endereço no
controle remoto é ruim, e por isso existe a pasta `jogos/tv/`: o endereço fica
`…/jogos/tv/` em vez de `…/jogos/aviao-tv.html?papel=tela`. A sala mostra esse
endereço curto na própria tela, para ler de longe.

**3. Espelhamento** (Smart View, Miracast, AirPlay). Funciona em quase tudo, mas
a TV vira um espelho do celular: o jogo e o controle ficam na mesma imagem, e
sobra o atraso do espelhamento. É o plano C.

Os três dependem de a página estar num endereço que a TV alcance — só o
espelhamento dispensa isso.

### Testar sem publicar: `servir.py`

O sensor exige `https`. Para testar na sua rede sem publicar nada, rode no
computador, dentro desta pasta:

```
python3 servir.py          (no Windows costuma ser:  py servir.py)
```

Ele serve esta pasta por https com um certificado caseiro e imprime o endereço,
tipo `https://192.168.0.15:8443/aviao-tv.html`. Abra no computador (vira a tela)
e o mesmo endereço no celular (vira o controle). O celular vai avisar que "a
conexão não é particular" — é esperado, o certificado não tem quem o assine;
toque em *Avançado* → *Continuar*. Nada sai da sua rede.

O que **não** funciona por esse caminho é o botão de enviar para a TV: o
Chromecast não aceita certificado caseiro. Para ele, a página precisa estar num
endereço https de verdade.

## Versão missão: cidade, alvos e armas

O mapa deixou de ser infinito. Todo cenário guarda o seu **x e z absolutos**, e
quem anda é o avião. Antes o mundo vinha vindo e cada objeto tinha o z alterado
a cada quadro — não dá para fazer isso com uma cidade inteira, e não permitia
ter começo e fim.

| coisa | como funciona |
|---|---|
| cidade | bairros com quarteirões e ruas, gerados uma vez no começo. Cada prédio é uma caixa: das quatro paredes, desenham-se as que a câmera está vendo de fora, com janelas quando está perto |
| alvos | depósitos de combustível, marcados com um círculo piscando. Valem 500 pontos |
| bomba | cai em queda livre e leva o avanço do avião junto. A **mira no chão** mostra onde vai cair, e fica verde quando está em cima de um alvo |
| míssil | vai reto e rápido, bom contra avião inimigo |
| metralhadora | tiro contínuo de curto alcance, bom contra pombo |
| prédio | bater num derruba o avião, igual a bater num pombo |

No computador: **1 2 3** trocam de arma, **espaço** atira, **V** alterna entre
ver de fora e ver de dentro da cabine. No celular, o controle ganhou os três
botões de arma e um botão **FOGO** grande.

## Versão 360°: o avião vira

O jogo era um trilho: inclinar empurrava o avião para o lado, mas ele sempre ia
para a frente, na mesma direção. Agora o avião tem **rumo**. Inclinar faz
**curva** — com a asa toda inclinada, a volta completa sai em uns 7 segundos —
e dá para ir para qualquer canto do mapa e voltar por onde veio.

O mapa é um **quadrado de 6 km de lado**, com um rio de norte a sul e duas
estradas que se cruzam. A missão não é mais chegar ao fim: é **derrubar os 14
depósitos** espalhados pelos bairros.

Como isso funciona no desenho: uma função só, `paraCamera(x, z)`, gira o mapa
inteiro em volta do avião antes de projetar, de modo que "para a frente" é
sempre o nariz. O resto do desenho continua igual. O que mudou de verdade foi
o que **não dava mais para supor**:

| antes (trilho) | agora (360°) |
|---|---|
| a lista de prédios estava ordenada por z, e bastava varrer uma fatia | a ordem muda a cada quadro: tudo é convertido para o eixo do nariz e ordenado do fundo para a frente |
| pegar combustível era "passou do meu z?" | é distância de verdade nos três eixos, porque dá para chegar no tambor por qualquer lado |
| o chão era uma escada de faixas em z | é uma grade do mapa, recortada pelo campo de visão e ordenada por distância |
| o prédio tinha "a frente e uma lateral" | é uma caixa: para cada parede, vejo se a câmera está do lado de fora dela |
| o sol ficava preso num canto da tela | tem um rumo no mapa, e anda pela tela quando se vira |
| a serra do horizonte rolava com o deslocamento | é desenhada pelo **rumo** de cada ponto da tela, com ondas de período inteiro — girando 360° as mesmas montanhas voltam ao mesmo lugar |

E entrou uma peça nova que num corredor não fazia falta: a **bússola**. Mostra
o rumo, e dois marcadores dizem onde está o tambor de combustível mais próximo
e o alvo mais próximo, com a distância em metros. Quando a coisa fica para
trás, o marcador encosta na ponta da fita e vira seta. Sem isso, voar em
círculo desorienta em dez segundos.

### Visão de cabine

É a mesma projeção, com duas diferenças: a câmera vai para dentro do avião
(`d = z + 60` em vez de `z + 750`), e o avião do jogador deixa de ser desenhado.

A cabine foi desenhada a partir de fotos de cockpit de verdade. O que as fotos
ensinaram, e que eu tinha errado:

- **quem rola é o mundo, não a cabine.** O piloto e o painel ficam parados e o
  horizonte é que se inclina. Eu tinha feito ao contrário, e o painel saía de
  quadro quando o avião virava;
- o **painel de teto** lá em cima, cheio de disjuntores, é o que mais entrega
  "isto é um avião" — sem ele o alto da tela era só um vazio preto;
- o painel é **escuro**, e quem brilha são os mostradores;
- os instrumentos seguem o **T básico**: velocidade à esquerda, horizonte
  artificial no meio, altímetro à direita;
- o **HUD é uma projeção no vidro**: tem que ser recortado pelo para-brisa. Se
  escorre para cima da armação, não parece vidro nenhum.

### Duas armadilhas de CSS que custaram caro aqui

**Especificidade.** `#controle.ver{display:flex}` tem especificidade maior que
`#controle{display:grid}`, mesmo o segundo estando dentro de uma media query —
media query não soma especificidade. O layout de duas colunas simplesmente não
acontecia.

**Estilo em linha.** `elemento.style.display = 'flex'` no JavaScript vence
qualquer regra de CSS. Trocar por `classList.add('ver')` devolve o controle
para a folha de estilo.

### A cabine, refeita com a disposição real

A primeira versão eu desenhei de cabeça, e saiu parecendo para-brisa de caminhão.
Refeita a partir de como é de verdade:

**Painel: arranjo "T básico".** É padrão em avião: horizonte artificial em cima
no centro, **velocidade à esquerda dele**, **altímetro à direita**, **rumo logo
abaixo**. Combustível e missão ficam nas pontas, fora do T.

**HUD: símbolos de caça.** Fita de velocidade à esquerda, fita de altitude à
direita, escada de arfagem no centro (linha cheia para subida, tracejada para
descida, numerada de 5 em 5 graus, a do horizonte sem número), **cruz do canhão**
fixa marcando para onde o nariz aponta, e o **vetor de velocidade** — o círculo
com asinhas que mostra para onde o avião vai de verdade. Pôr o vetor em cima de
um ponto do chão é ir naquele ponto.

**O que rola e o que fica parado.** Este foi o erro que mais custou: eu rodava a
cabine. É o contrário — o piloto e o painel ficam parados, e **o mundo é que
rola**. A escada de arfagem acompanha o horizonte (rola junto), mas as fitas e a
cruz do canhão ficam presas ao avião, e não rodam.

Fontes que usei: o arranjo do painel em
[Engineering LibreTexts](https://eng.libretexts.org/Bookshelves/Aerospace_Engineering/Fundamentals_of_Aerospace_Engineering_(Arnedo)/05:_Aircraft_instruments_and_systems/5.01:_Aircraft_instruments/5.1.04:_Instruments_layout)
e a simbologia do HUD em [Falconpedia](http://falcon4.wikidot.com/avionics:hud)
e na [documentação do DCS](https://dcs.man-sim.org/en/fa18c/05.hud/).

## Versão caça: cambalhota, e o controle que não inverte mais

O Brunno achou o defeito: *"quanto mais eu giro, após um certo ângulo ele volta
para o outro lado"*. Era **trava de cardan**. Eu lia `beta` e `gamma` do sensor
e usava direto, mas `gamma` só vai de -90° a +90° — passando disso a leitura
**dobra para trás**.

A correção é montar o vetor "para cima do mundo" visto de dentro do aparelho:

```
u = ( -cos(beta)·sin(gamma) ,  sin(beta) ,  cos(beta)·cos(gamma) )

rolagem = atan2(u.x, u.y)   -> volta inteira, -180° a 180°, sem trava
arfagem = asin(u.z)         -> o quanto a tela está virada para o céu
```

Isso resolve três coisas de uma vez: a rolagem **dá a volta completa**, os dois
eixos **param de se misturar** (girar na mão não mexe no manche), e o jogo
**deixa de precisar adivinhar** se o celular está em pé ou deitado — a
calibragem absorve a pegada. O botão "girar" virou **"zerar aqui"**: segure
como quiser, toque, e aquela posição passa a ser "asas niveladas".

### E o avião ganhou atitude de verdade

Com o controle dando a volta inteira, o modelo de voo antigo não servia mais:
ele tinha um ângulo de inclinação achatado e um "nariz" que empurrava a linha do
horizonte na tela. Não havia como representar o avião de ponta-cabeça, nem
apontando para o zênite.

Agora o avião carrega **três vetores** — para onde aponta o nariz, o teto da
cabine e a asa direita. Rolar gira um par em volta do nariz; cachimbar gira
outro par em volta das asas. Como a manobra é sempre em volta dos eixos **do
avião**, duas coisas saem de graça:

- inclinar e puxar faz **curva**, como num avião de verdade;
- puxar com as asas niveladas faz **looping**.

A projeção virou uma câmera de furo de verdade (`x/z`, `y/z`), sem o truque de
empurrar o horizonte. E o céu deixou de ser "a parte de cima da tela": o
horizonte é uma **reta**, e de que lado dela está o céu sai do vetor "para cima
do mundo" visto pela câmera. É isso que deixa voar de cabeça para baixo sem a
imagem se desmanchar.

A escada de arfagem do HUD também foi refeita: cada degrau é uma **direção do
mundo** projetada pela mesma câmera, em vez de linhas empilhadas a partir de
uma linha do horizonte inventada. Por isso ela sobrevive ao looping.

### Controle: deslizar em vez de apertar

*"Tem que ser rolando, passando o dedo para o lado, e não apertando, pois força
olhar o controle."* O seletor de arma virou uma faixa: o dedo arrasta para o
lado e a arma muda. E cada arma **vibra diferente** — um, dois ou três toques —
para dar para trocar de arma com os olhos na tela grande.

### O QR fica aberto

O código e o QR continuam num canto durante a partida inteira, encolhidos para
não atrapalhar. Quem chegar depois aponta a câmera e entra sem ninguém parar o
jogo.

## Dois jogadores: piloto e artilheiro

Quando o segundo celular entra, ele **não toma o avião** — ganha um posto.

Antes a tela guardava **uma** conexão e o mais novo derrubava o antigo: quem
entrasse no meio da partida roubava o avião, e o primeiro via *"a TV
desconectou"*. Agora existe uma **tripulação**:

| posto | quem é | o que faz |
|---|---|---|
| **piloto** | o 1º que entra | a inclinação dele vira a do avião |
| **artilheiro** | o 2º | a inclinação dele move a **torre**, e é ele quem escolhe a arma e aperta o gatilho |
| reserva | do 3º em diante | entram como artilheiros e assumem se alguém sair |

A torre é um desvio em relação ao nariz, dentro de um cone de uns 24°. Míssil e
metralhadora saem **por onde a torre aponta**; a bomba continua saindo do
ventre, porque bomba quem manda é a gravidade. Na tela grande aparece um
retículo vermelho separado da cruz do canhão, e ele **fecha e fica verde**
quando há alvo na linha de tiro — dá para acertar sem ninguém falar nada.

O controle do artilheiro muda de cara: em vez do horizonte artificial, ele vê a
mira andando dentro do cone.

Detalhe que custou um teste: **fechar a aba do celular não avisa a tela** — o
PeerJS simplesmente não manda nada. Quem sumiu é descoberto pelo **silêncio**
(3,5 s sem mensagem). Sem isso o artilheiro nunca assumia o manche quando o
piloto largava o jogo.

## O manche estava invertido

`asin(uz)` mede "a tela está virada para o céu", e é **empurrar** a borda de
cima para longe que vira a tela para cima. Sem o sinal negativo, empurrar subia
e puxar descia. Agora vale o manche de verdade: **puxar a borda de cima levanta
o nariz**, que é o que o aviso na tela sempre prometeu.

## Leme, bomba nuclear e o celular preso deitado

### O leme, pelo movimento lateral

Os outros dois eixos vêm da **inclinação**, que o sensor mede direto. O leme
vem de **deslocar** o celular para o lado — e aí tem um limite físico que vale
dizer em voz alta: **acelerômetro não sente posição, só mudança de movimento**.
Deslocar e segurar parado na esquerda é, para ele, idêntico a estar parado no
meio. O que dá para medir é o **deslizar**. Então o leme dá chute e volta ao
centro, como pedal de leme de verdade.

Separar o empurrão da freada deu duas tentativas erradas antes da certa:

| tentativa | por que não serve |
|---|---|
| integrar a velocidade lateral | a freada no fim do gesto invertia o leme |
| trava de tempo depois de cada gesto | deslizando várias vezes seguidas, a freada caía fora da trava e virava gesto novo, para o lado contrário |
| **silêncio antes do empurrão** | é o que distingue os dois: empurrão começa com a mão parada, freada vem colada |

O leme aparece na **bolinha de derrapagem** do horizonte artificial e numa
marca embaixo da cruz do HUD. No computador é **A** e **D**.

### A bomba nuclear

Três coisas separadas, que juntas fazem o efeito: o **clarão** (é o que se vê
primeiro, de longe), o **cogumelo** e o **anel** correndo pelo chão, que é o
que dá a escala. O som é um estrondo grave e longo com a cauda descendo de tom.

Um erro que custou uma rodada: passei o cogumelo pela névoa cheia, e como a
névoa puxa tudo para a cor do céu, ele **sumia dentro do próprio céu**. Uma
explosão dessas tem luz própria — agora a névoa entra com um terço da força.

A marca preta no chão é desenhada como **polígono projetado**, não como elipse
na tela: assim ela deita no terreno e acompanha a inclinação do avião, em vez
de ficar como adesivo colado no vidro.

Ela derruba tudo num raio de 450 m — inclusive **você**, se largar voando
baixo demais. Por isso são só 6, com recarga longa.

### Preso deitado

Girando o celular a página se remontava "em pé" e o controle mudava de lugar na
mão. Agora tenta-se a trava de verdade (tela cheia + `orientation.lock`) e,
quando o navegador não deixa — é o caso do Safari do iPhone —, a página é
**girada por CSS** para continuar deitada.

Para isso a `@media (max-height:520px)` do controle virou **classe**: com o giro
por CSS o navegador continua achando que a tela é alta, a media query não casava
e o controle saía montado em coluna, transbordando para fora da área visível.

## A câmera solta e o avião em 3D de verdade

São duas coisas que só funcionam juntas.

**A câmera** era parafusada no avião: a base dela *era* a base do avião. Por
isso o avião ficava cravado no meio da tela, sempre na mesma pose, e quem
girava era o mundo inteiro. Agora ela **persegue** o avião com atraso — e é o
avião que se mexe dentro do quadro: inclina, sobe, escorrega para o lado e
volta para o meio. O teto da câmera persegue o do avião **só em parte** (metade
puxa para o céu), senão ela rolaria junto até o fim e a inclinação das asas
não apareceria em lugar nenhum. Na cabine não há atraso: lá a câmera é o
piloto.

**O avião** era um desenho chapado — um recorte de papel que girava na tela.
Com a câmera solta isso não se sustenta: de qualquer ângulo que não fosse
exatamente por trás, a mentira aparecia.

Agora ele é uma **malha**: uma lista de vértices no sistema do próprio avião e
uma lista de faces. A cada quadro cada vértice vai para o mundo pela base do
avião (asa direita, teto, nariz), de lá para a câmera, e daí para a tela. As
faces que dão as costas para a câmera são descartadas, o resto é ordenado do
fundo para a frente, e cada uma recebe a luz do sol pela sua **normal**. São
114 faces e 142 vértices — fuselagem de seção hexagonal, asa em flecha de ponta
cortada, empenas, derivas duplas, dois motores e canopy.

Sobre modelar num programa de modelagem: seria o caminho natural, mas um
modelo exportado vira **arquivo externo**, e o jogo deixaria de ser um HTML só
— que é justamente o que faz ele abrir no navegador da TV e funcionar sem
servidor. A malha mora dentro do arquivo, escrita como código.

Dois detalhes que fizeram diferença: um **fio escuro** no contorno de cada
face (sem ele, com o avião pequeno na tela, a malha vira uma mancha só) e a
**sombra no chão**, que é o que diz a altura de verdade. O avião inimigo usa a
mesma malha, pintada de vermelho e virada para o rumo dele.

## A versão com engine: aviao3d.html

O desenho em canvas chegou no teto. Passar para uma engine 3D resolve o que
não dava para fazer à mão: luz especular, sombra projetada, névoa de verdade e
milhares de polígonos sem custar quadro.

**Por que three.js e não Godot/Unity.** Uma engine de verdade exporta uma pasta
com `.wasm` e dados, precisa de servidor e pesa dezenas de megabytes — e o jogo
deixaria de abrir no navegador da TV. O three.js é uma biblioteca: vai
**embutida no HTML** (725 KB, ~190 KB comprimidos pela rede) e o arquivo
continua sendo um só. `montar.py` faz esse embutimento, igual já fazia com o
PeerJS.

**O que muda no código.** Na versão em canvas eu calculava à mão cada polígono,
a ordem de desenho, a névoa e a luz. Aqui eu só **descrevo a cena** — o que
existe, de que cor, onde está a luz — e a placa de vídeo desenha.

| coisa | como ficou |
|---|---|
| terreno | uma malha só, cor por célula. **Desindexada**: pintando por vértice, a placa interpola entre um campo e o vizinho e o mosaico vira um borrão |
| cidade | `InstancedMesh`: uma caixa e uma lista de posições, 700+ prédios numa passada só |
| avião | fuselagem de revolução com normais suaves, asa extrudada, material com brilho especular |
| luz | hemisférica (céu/chão) + sol direcional com sombra, e uma luz fraca presa na câmera para nada ficar preto |
| névoa | `THREE.Fog`, que some com a cidade no horizonte de graça |
| HUD | continua em canvas 2D, numa camada por cima: texto e linha fina é o que o 2D faz melhor |

Três erros que custaram tempo, anotados para não repetir:

1. **A câmera montada na mão ficava espelhada.** Montar a matriz com
   (direita, cima, −frente) dá uma base inválida, e o resultado é o avião
   aparecer *atrás* da câmera. `lookAt` monta a base certa.
2. **Cor por vértice borra o terreno** — o mosaico precisa de malha desindexada.
3. **O tamanho da célula não era o que eu supunha:** a malha divide o mapa em
   partes iguais, então a célula mede `mapa/segmentos`, não o passo que eu
   tinha em mente. Arredondar pelo número errado pinta a célula vizinha.

O que **ainda não está** na versão 3D: o controle pelo celular em rede (sala,
QR, copiloto). Isso continua só em `aviao.html` / `aviao-tv.html` até a versão
3D provar que roda bem na TV.

### O celular controlando a versão 3D

Não foi preciso escrever controle nenhum: o `controle.html` que já existia
**conecta na página 3D sem uma linha de mudança**, porque as duas falam o mesmo
protocolo e usam o mesmo prefixo de sala. O que a versão 3D ganhou foi só o
lado que escuta — abrir a sala, desenhar o QR e repartir os postos.

Um defeito que só apareceu com dois celulares, e que estava **também** nas
versões 2D sem ninguém ter notado:

> O aviso de estado sai a cada 250 ms para todo mundo. Quando um celular novo
> entrava, esse aviso o alcançava **antes de a conexão terminar de abrir** — o
> PeerJS soltava um erro `not-open-yet`, e como o meu tratador de erro
> expulsava o membro, o recém-chegado era posto para fora no mesmo segundo em
> que entrava.

O sintoma enganava: o celular mostrava "ARTILHEIRO" e a torre até respondia
(porque o tratador de dados continuava preso na conexão), mas a tela dizia que
só havia um jogador. A correção são duas linhas: só mandar para quem já abriu,
e **erro solto não é despedida** — quem sai, sai pelo `close` ou pelo silêncio.

---

## Esquerda e direita trocadas na versão 3D

O Brunno testou e explicou o problema melhor do que qualquer medição:

> *"cada mão segurando o celular (deitado) é como se controlasse uma asa. Ao
> inclinar para a esquerda — mão esquerda para baixo — o avião rotacionava a
> asa esquerda para cima."*

A causa é a **mão do sistema de eixos**. O avião guarda três vetores, e um
deles o código chama de "asa direita" (`eixoD`). Ele era calculado como
`teto × nariz`, e num sistema destro isso dá o vetor que aparece à
**esquerda** de quem olha para a frente. Medido, numa tela de 1280 (o centro
é 640):

```
o vetor que o código chama de eixoD aparece em x=221 -> ESQUERDA da tela
```

Na versão em canvas o erro não aparecia: aquele desenho é espelhado do mesmo
jeito e os dois enganos se cancelavam. Com o three.js, que usa a convenção
certa, o espelho sumiu.

### A primeira tentativa quebrou a câmera — e por quê

O conserto "certo no papel" seria trocar o `eixoD` por dentro. Foi o que eu
fiz, e o Brunno respondeu: *"o controle piorou, a câmera ficou fora de
controle; no primeiro teste a câmera estava perfeita"*.

O motivo: a **inclinação** é medida a partir do próprio eixoD
(`atan2(-eixoD.y, eixoC.y)`), e a rolagem pelo celular é um comando
**absoluto** — o jogo não aplica uma velocidade de rolagem, ele *persegue* o
ângulo que a mão pediu:

```js
const erro = (lat*180 - inclinacao);    // o quanto falta
rol = clamp(erro*3.2);                  // corrige na direção do erro
```

Trocando o sinal do `eixoD` sem trocar o da medida, `inclinacao` passou a ter
o sinal contrário e a correção deixou de puxar **contra** o erro para empurrar
**a favor** dele. Realimentação positiva: o avião rodopiando sem parar e a
câmera atrás, tentando acompanhar. O sintoma parecia "a câmera enlouqueceu",
mas a câmera estava certa — quem enlouqueceu foi a malha de controle.

### A correção que ficou

O espelho se desfaz na **entrada**, num sinal só:

```js
const MAO = -1;      // o eixoD do jogo é, visualmente, a asa esquerda
lat  = MAO * (volante/180)
leme = MAO * leme
```

O mundo continua coerente consigo mesmo, a realimentação continua negativa
(mede e persegue o mesmo eixoD de sempre, com o mesmo sinal), e só o lado para
onde o comando pede é que muda. A câmera nem fica sabendo.

A bússola tinha o mesmo espelho, e foi desfeito só na **hora de desenhar**
(`rumoVisto() = -rumo`), sem tocar no `rumo` que as nuvens e a escada de
arfagem usam.

### O que foi medido depois

```
celular 35° para a DIREITA : desceu a asa DIREITA     ✔
celular 35° para a ESQUERDA: desceu a asa ESQUERDA    ✔
curva para a DIREITA : o mundo correu para a ESQUERDA ✔   bússola 000° -> 015°  ✔
curva para a ESQUERDA: o mundo correu para a DIREITA  ✔   bússola 000° -> 345°  ✔
leme para a DIREITA  : o nariz foi para a DIREITA     ✔
leme para a ESQUERDA : o nariz foi para a ESQUERDA    ✔
puxar -> nariz +78°  |  empurrar -> -78°              ✔
setas do teclado                                      ✔
câmera após 5 s de manobra forte: 748 de distância, avião bem à frente  ✔
```

**Duas armadilhas na hora de medir**, que me custaram duas rodadas:

1. **Projetar um ponto que está fora do quadro não serve de prova.** Um ponto
   a 85° do eixo da câmera devolve um x absurdo (5357 numa tela de 1280) e o
   sinal pode até virar. A medida confiável é com vetores do mundo:
   `direita da tela = frente × cima` — regra tirada de um teste mínimo de
   convenção, não de memória.
2. **"Inclinar e puxar" com puxada forte não é curva, é cambalhota.** Numa das
   rodadas o nariz terminou a 0,96 de vertical, e aí `atan2(x, z)` do rumo é
   só ruído: a bússola parecia errada e estava certa. O teste passou a
   imprimir a arfagem junto, para não cair nisso de novo.

## O acelerador e o nitro

Pedido: *"um acelerador no controle no lado direito, e no lado esquerdo o
botão do nitro"*.

Até aqui o avião voava sempre à mesma velocidade (`VOO_BASE`, 1700) e só
acelerava quando pegava um tambor azul. Agora a velocidade de cruzeiro é
escolhida pelo dedo:

```
potência 0     -> VOO_MIN  700     (marcha lenta)
potência 0,67  -> VOO_BASE 1700    (exatamente o de antes)
potência 1     -> VOO_MAX  2200    (potência militar)
nitro          -> VOO_TURBO 3000
```

O acelerador começa em **0,67** de propósito: quem joga no teclado e nunca
encostar nele voa igual ao de sempre. E o combustível passou a acompanhar o
acelerador (`GASTO * (0,55 + 0,7 × potência)`) — voar devagar rende mais
quilômetro.

O **nitro** é de segurar e tem carga própria: gasta 26 por segundo, enche 8,5
por segundo sozinho, e o tambor azul enche até em cima. Sem carga, o botão
apaga e o avião volta à potência do acelerador.

### Três decisões que valem explicar

**1. O acelerador é uma alavanca, não um par de botões.** O dedo pousa na
altura que quer e a potência salta para lá. É a mesma ideia do seletor de
armas: nada que obrigue a olhar para o celular. E, como reforço, ele **vibra a
cada 10%** — um toque curto nos degraus, dois no cheio, um longo no vazio.
Dá para ajustar a potência com os olhos na tela grande.

**2. Os dois viajam dentro do pacote de eixos, não em mensagem própria.** O
canal do controle é o **não confiável** (rápido, mas perde pacote). Uma
mensagem `{t:'motor', v:0.8}` solta que se perdesse deixaria o avião na
potência errada até o dedo se mexer de novo. Indo junto com os eixos, 30 vezes
por segundo, um pacote perdido não custa nada: o próximo já corrige. Custa
dois números a mais por pacote.

**3. O nitro solta sozinho quando o celular some.** Se o piloto sai da sala
com o dedo no botão, o `nitroBotao` fica ligado para sempre e o avião não
desacelera nunca. Quem sai, solta — e o mesmo vale para a janela que perde o
foco com o Shift apertado.

### O erro do caminho: a tira ficava larga e baixa deitada

O CSS do controle deitado estava escrito como `body.paisagem .motor { width: ... }`,
e não pegava. O motivo é **especificidade**: `#acel { width:100%; max-width:340px }`
é uma regra de **id**, e uma regra de id ganha de uma regra de classe por mais
classes que ela tenha. A tira continuava com 340×74 no meio da tela, por cima
do botão de fogo. A correção foi trocar por `body.paisagem #acel, body.paisagem #nitro`.

Medido depois, em quatro telas (844×390, 667×375, 915×412 e 390×844 girada
por CSS): nenhuma sobreposição com o gatilho, com o seletor de armas ou com o
horizonte, nada fora da tela, e o dedo a 2%, 50% e 98% da tira dando 2%, 50% e
98% de potência.

### Teclado

`W` e `S` mexem o acelerador, `Shift` é o nitro. Vale nas quatro versões,
porque a conta mora no núcleo compartilhado.

## A escada de arfagem do HUD estava deitada

> *"o HUD (cabine) está errando: inclinando para a esquerda ele se comporta
> como se estivesse indo para a direita"*

Desta vez não era sinal trocado — e foi por isso que demorei a achar. O
**lugar** de cada degrau estava certo: inclinando para a esquerda a escada
sobe para a direita, que é exatamente o que se vê de dentro de um avião
inclinado (inclinando a cabeça para a esquerda, o mundo parece girar para a
direita). O errado era o **desenho**: cada degrau saía DEITADO na tela,
sempre, enquanto o horizonte estava torto. Medido, com 40° de banco:

```
horizonte de verdade ......... 39°
degrau desenhado ............... 0°   ✘
```

Uma escada de degraus retos marchando para cima e para a direita lê-se, para
qualquer olho, como um avião inclinado para a DIREITA. O HUD contava uma
história e o mundo contava outra.

O conserto evita de propósito a conta de rolagem, que é justamente a de sinal
duvidoso neste jogo: em vez de calcular o ângulo, o desenho projeta **um
segundo ponto do mesmo degrau**, um pouco de lado. A direção entre os dois já
é a do horizonte — com perspectiva e tudo, e sem trigonometria nenhuma para
errar o sinal.

```js
const c  = naTela(rumo, a);           // o meio do degrau
const d2 = naTela(rumo - 0.16, a);    // um palmo para a direita, no mesmo degrau
// (c -> d2) é a direção do horizonte
```

Medido depois, nos dois bancos e em três alturas: diferença de 0° a 2° entre o
degrau e o horizonte (os 2° são perspectiva de verdade — degraus acima e
abaixo do horizonte convergem, como devem). Os números da escada passaram a
girar junto, e cada degrau ganhou uma farpa apontando para o horizonte, que é
o jeito padrão de um HUD dizer onde fica o chão.

**A lição que ficou:** quando o mundo e o HUD discordam, o suspeito não é só o
sinal. Foi preciso medir as três coisas separadamente — onde está o horizonte,
para onde anda a espinha da escada, e com que ângulo cada degrau é desenhado —
para ver que duas estavam certas e só a terceira estava errada.

---

## Fazer 180 e 360: o aileron virou VELOCIDADE

> *"uma situação que tô sentindo dificuldade é de fazer 180 graus ou 360
> graus. Tem que ter bem definido o que mexe no profundor e o que mexe no
> aileron."*

O aileron era um comando **absoluto**: 30° de mão eram 30° de asa. Preciso
para voar reto — e, sem querer, uma prisão: para dar 360° na asa a pessoa
teria de girar o pulso 360°. Não dava, e nunca ia dar.

Pior, os dois eixos tinham gramáticas DIFERENTES. O profundor sempre foi
velocidade (puxou, o nariz sobe enquanto estiver puxado), o aileron era
ângulo. Uma mão pedia posição e a outra pedia taxa. É exatamente o "não está
bem definido o que mexe no quê".

Agora os dois pedem **velocidade**:

| gesto | comando | o que faz |
|---|---|---|
| girar o celular de lado | **aileron** | roda as asas enquanto estiver inclinado |
| puxar/empurrar a borda de cima | **profundor** | levanta/baixa o nariz enquanto estiver puxado |
| deslizar o celular para o lado | **leme** | chuta o nariz para o lado |

### Três detalhes que fazem a diferença

**1. A resposta é curva, não reta.** `taxa = (curso)^1,6`. Perto do meio o
avião rola devagar e dá para corrigir fino; a rolagem cheia (195°/s, um tonô
em menos de dois segundos) só vem no fim do curso. Com a resposta reta um
tranquinho de mão já jogava o avião de lado.

**2. Soltar endireita — mas só até 32° de banco.** Esse limite não é enfeite,
e eu só descobri que precisava dele porque o teste cobrou: sem ele, o comando
por velocidade **tira a curva do jogo**. A pessoa inclina para entrar na
curva, endireita a mão para parar de rolar, e o nivelador desfaz a curva
inteira. Com o limite, inclinar e soltar deixa o avião pousado numa curva
firme — que é como se voa de verdade — e perto do nivelado ele continua se
endireitando sozinho, que é o que salva quem está começando.

**3. Passando de 32°, o avião segura o que tem.** É o que permite voar de
cabeça para baixo depois de meio tonô.

Medido: 45° de celular segurados por 4 s giram **779°** nas asas (duas voltas
e pouco); manche puxado por 5 s leva o nariz por **430°** (a cambalhota
inteira e sobra); banco de 24° com a mão solta volta a **0°**; banco de 136°
com a mão solta fica em **136°**.

## Pista, trem de pouso, flapes, decolagem e pouso

> *"também quero poder pousar. Quero flaps, trem de pouso, quero poder decolar
> e aterrissar."*

Tem uma pista de 22.000 unidades correndo de sul para norte a partir da
origem, com asfalto, tracejado do meio, cabeceiras e as faixas do ponto de
toque. Nenhum prédio, alvo ou tambor nasce perto dela, e o campo em volta
ficou com a grama aparada de aeroporto. O jogo **começa parado nela** (dá para
escolher "começar já no ar" na capa, e a escolha fica guardada).

### Os números, e por que são esses

```
marcha lenta ................. 520      \  a marcha lenta tem de ficar ABAIXO
estol sem flape .............. 640      /  do estol, senão nunca se estola
estol com flape 1 ............ 540
estol com flape 2 ............ 450
teto com o trem embaixo ..... 1400
teto com flape 2 ............ 1150
velocidade máxima no toque .. 1250
```

Duas dessas linhas nasceram de erro meu, apanhado pelo teste:

**A marcha lenta era 700 e o estol 640.** Ou seja: era impossível estolar, o
código do estol era letra morta e os flapes não serviam para nada. Baixando a
marcha lenta para 520, fechar a manete sem flape faz o nariz cair — e com
flape não faz. É exatamente para isso que os flapes existem, e agora eles
existem.

**O limite de velocidade no toque era 1500, e o teto do trem é 1400.** O
avião com o trem fora nunca chegava a 1500, então a checagem nunca disparava.
Com 1250 dá para estourar o pouso chegando com a manete aberta e sem flape —
e reduzir ou baixar flape passa a ser uma decisão.

### O pouso

Tocar na pista é pouso se o trem estiver embaixo, o banco abaixo de 22°, a
velocidade abaixo de 1250 e a descida abaixo de 620 por segundo. Qualquer
outra coisa é batida, e o aviso diz qual das quatro foi. Pouso macio vale 400
pontos, pouso duro 150.

### Três erros do caminho

**A corrida de decolagem durava meio segundo.** Eu reaproveitei a fórmula da
velocidade do ar (`voo += (alvo - voo) * dt*2,5`), que existe para a
velocidade "assentar" depois de mexer na manete. Como corrida de decolagem ela
é absurda: o avião saltava para a velocidade de rotação antes de a pista
começar a passar. No chão a velocidade passou a ganhar e perder POR SEGUNDO
(86 de aceleração, 330 de freio), e a corrida ficou em 6 s e 1.940 de pista.

**O avião parado nunca saía do lugar.** Havia um `if (voo < 8) voo = 0` para
o avião encostar em zero ao frear. Só que ele valia sempre — e zerava, a cada
quadro, o empurrãozinho de 1,8 que a aceleração acabara de dar. Agora o corte
só vale para quem está freando.

**Bater com o avião no chão deixava `noChao` ligado.** O `derruba()` não
mexia nessa marca, e o avião "caía" achando que estava rolando na pista. Uma
linha, mas contaminou uma rodada inteira de teste antes de eu ver.

### O que dá para medir

```
começa parado na pista, trem embaixo, flape 1                    ✔
corrida até a rotação: 6,0 s e 1.940 de pista (a pista tem 22.000) ✔
puxou -> decolou usando 2.386                                     ✔
aproximação com trem e flape 2, pilotada só pelo manche -> POUSOU ✔
freando com a manete fechada: parou em 2,5 s e 1.018 de pista     ✔
sem trem de pouso ............ bateu  ✔      asa a 40° ......... bateu  ✔
manete aberta e sem flape .... bateu  ✔      descendo como pedra  bateu  ✔
manete fechada sem flape: nariz caiu a -52°  ✔ (estolou)
a mesma manete com flape 2:   nariz em 0°    ✔ (é para isso que servem)
```

No celular apareceram dois botões, **TREM** e **FLAPE**, na fileira de cima —
que é onde mora o que se usa duas vezes por voo. Eles só aparecem se o jogo do
outro lado souber pousar: o pacote de estado traz `pousa:true`, e assim o
mesmo `controle.html` continua servindo os jogos em 2D sem dois botões mortos
na tela. E mandam o valor que querem (`v`), não "troque" — num canal que perde
pacote, um "troque" perdido deixaria os dois lados discordando para sempre.

---

## O leme: de deslizar para APONTAR

> *"temos que pensar como controlar o leme do avião agora, pois faz falta kkkk"*

O leme era o deslize do aparelho para o lado, e eu já sabia por que ele era
ruim — está escrito lá em cima: **acelerômetro não sente posição, só mudança
de movimento**. Deslocar e segurar parado à esquerda é, para ele, igual a
estar parado no meio. O que dava para medir era o chute, e chute morre
sozinho.

Enquanto o jogo era só voar e bombardear, dava para levar. Depois que passou
a ter pista, não dá: manter o avião no eixo na corrida de decolagem e na
corrida de pouso é justamente segurar um leme **firme**, por segundos.

### O terceiro movimento

Os outros dois comandos usam dois giros do aparelho:

- **rolar** (em torno do eixo que sai da tela) = aileron
- **puxar/empurrar a borda de cima** (em torno do eixo comprido) = profundor

Sobra exatamente um giro: **apontar o conjunto para o lado**, girando com o
corpo, como quem mira. Não mexe em nenhum dos dois outros, e é uma posição —
dá para segurar. Virou o leme.

### Como se mede

Das três leituras do sensor sai a orientação inteira do aparelho, e dela eu
tiro **o eixo que sai pelas costas da tela**. Esse eixo tem duas propriedades
que são exatamente o que o leme precisa:

1. **rolar o celular não o move** — rolagem é giro em torno dele mesmo. Isso
   não é aproximação, é identidade: girar em torno de um eixo deixa o eixo
   onde estava. Medido: apontado 20°, rolando de 0° a 270°, o leme leu
   `0,481` nas seis medidas. O mesmo número, sem uma casa de diferença.
2. **puxar e empurrar só o levantam ou abaixam**, sem mudar o rumo dele.
   Medido: ±25° de profundor, leme sempre `0,481`.

O rumo desse eixo no plano horizontal mede o apontar, e só o apontar.

Não dá para usar o `alpha` cru, que seria o caminho óbvio: ele trava quando o
aparelho aponta para cima ou para baixo — a velha trava de cardan, a mesma que
estragou o aileron lá no começo. O vetor não trava.

### A fuga lenta do zero

No Android o `alpha` não tem norte de verdade: é giroscópio integrado, e
escorrega alguns graus por minuto. Sem tratar, o avião ia derivando sozinho
com a mão parada.

A saída: enquanto o pedido de leme estiver **pequeno**, o zero persegue a
leitura bem devagar — constante de uns 20 segundos. Rápido o bastante para
comer a escorregada (a 4°/min ela se estabiliza em menos de 1° de erro, muito
dentro da folga de 7°), lento o bastante para não roubar um leme que a pessoa
esteja segurando de propósito. Perto do talo não vaza nada.

Medido: 13 s de escorregada a 4°/min terminam com leme `0,000`; um leme de
28° segurado pelo mesmo tempo continua em `0,78`.

### E no chão, o aileron também esterça

Rolando na pista, inclinar o celular para o lado não tinha para que servir — e
"deitar para o lado que quero ir" é o gesto que sai sozinho. Então o aileron
esterça junto com o leme, com meia força. Duas consequências boas: o gesto
natural funciona, e dá para se manter na pista mesmo se o apontar não estiver
indo bem no aparelho de alguém.

### O que dá para medir

```
apontei 25° para a direita  -> leme +0,67 (direita)   ✔
apontei 25° para a esquerda -> leme -0,67 (esquerda)  ✔
apontei 4° (a folga é 7°)   -> leme 0,00              ✔
apontei 40° (curso de 34°)  -> leme 1,00, no talo     ✔
rolando 0→270°  : 0,481 0,481 0,481 0,481 0,481 0,481 ✔ nem um pouco
arfando ±25°    : 0,481 0,481 0,481 0,481 0,481       ✔ nem um pouco
apontando ±30°, o aileron e o profundor leram 0,0     ✔ nos dois sentidos
na pista, leme e aileron esterçam para o lado certo   ✔
corrida torta corrigida com o leme: x=101 -> x=0      ✔ (a pista tem ±620)
```

### Dois erros meus, os dois no TESTE

O código saiu certo na primeira; o teste é que mentiu duas vezes, e vale
anotar porque é o mesmo tipo de engano das outras vezes.

**O sinal.** Eu supus que apontar para a direita fazia o `alpha` crescer. É o
contrário: o `alpha` do padrão cresce girando para a **esquerda**. Só que a
conta que eu escrevi produz um rumo de bússola, que cresce para a direita — e
aí o menos que eu tinha posto "para corrigir" era justamente o erro. Medir
resolveu em uma rodada.

**O eixo da arfagem.** O primeiro teste acusou "o profundor vaza no leme", com
o leme indo de 0,00 a 1,00 ao arfar. Não vazava nada: eu tinha modelado a
arfagem como giro em torno do eixo **curto** do aparelho, que deitado aponta
para **baixo** — ou seja, o meu "arfar" era mais apontar. Trocando para o eixo
certo, o vazamento sumiu inteiro.

Duas vezes seguidas o modelo do teste estava errado e o código, certo. A
lição é a mesma da escada de arfagem: quando o número não bate, o suspeito não
é só o código — o instrumento de medida também erra, e ele é escrito com a
mesma cabeça que escreveu o código.

---

## Batalha aérea: gente de verdade no mesmo céu

> *"quando tiver alguém jogando e outra pessoa for no jogo, poder mostrar
> quantas pessoas on-line, e poder entrar também. E poderá me derrubar."*

Cada tela do jogo já abria uma sala, para o celular entrar como controle. A
batalha reaproveita exatamente isso: **quem já está voando tem um código, e
outra pessoa digita esse código para cair no mesmo céu**.

### A forma é uma estrela

Quem abriu a sala é o anfitrião e serve de central: cada um manda o seu estado
para ele, e ele reparte para todo mundo. Com meia dúzia de aviões é de longe o
mais simples que funciona — malha completa exigiria cada um encontrar cada um,
e o encontro pelo PeerJS já é trabalho suficiente para uma ligação só.

### Quem decide o tiro é quem atira

Essa é a decisão que faz a coisa ser jogável. O acerto é testado **na tela de
quem apertou o gatilho**, contra a posição que ela recebeu, e o resultado vai
como recado: *"te acertei, tanto de dano"*. A vítima acredita e desconta.

Se fosse a vítima a julgar, com 80 ms de atraso de rede o avião que ela vê na
tela de quem atirou já não está mais lá quando a bala chega, e ninguém
acertaria nada. Entre amigos, confiar em quem atira é a escolha certa — e é o
que quase todo jogo de tiro faz, pelo mesmo motivo.

Cada avião tem 100 de fuselagem. Metralhadora tira 7, míssil tira 45, e a
nuclear leva todo mundo no raio.

### Uma conexão que chega pode ser um CELULAR ou um AVIÃO

Não dá para saber pelo evento de conexão — dá para saber pela primeira
mensagem. Então a ligação fica em observação: quem diz `{t:'entra'}` é
jogador, qualquer outra coisa é celular, e quem não disser nada em 4 segundos
é celular (que é o caso comum). Sem isso, o avião de outra pessoa entrava como
**artilheiro** e tomava a torre.

### Dois erros que só apareceram com dois navegadores abertos

**Quem estava caindo sumia do mundo.** O `atualiza` desvia para a queda logo no
começo e volta — e ali dentro ninguém mandava estado. Resultado: o abatido
congelava no céu dos outros até a varredura de silêncio apagá-lo cinco
segundos depois. Ninguém via a queda. Uma linha dentro de `atualizaQueda`.

**A contagem piscava.** Eu contava os aviões desenhados no céu. Só que quem
está na tela de capa, ou caindo, não manda posição — e a conta caía para 1
sozinha. Agora a contagem vem do anfitrião, que é quem sabe quantas ligações
tem, e viaja junto com o estado dele.

### E um bug antigo que a batalha revelou

O CSS tinha `canvas{ position:fixed; inset:0 }`, escrito para as duas telas
grandes do jogo. Só que ele pegava **todos** os canvas — inclusive os QR
pequenos dentro de caixinhas. O código do convite ia parar grudado no canto de
cima da tela, longe da sua própria legenda. Estava assim desde que o convite
existe; eu só reparei olhando uma foto de teste da batalha.

### O que dá para medir

O servidor de encontro público está bloqueado aqui, mas o `peer` roda local —
então o teste é com **dois navegadores de verdade**, cada um com a sua sala,
conversando por WebRTC:

```
A e B abrem salas próprias, B entra na de A
1) A anfitrião, B convidado, cada um vê o outro        ✔
2) contagem: A diz 2, B diz 2                          ✔
3) A vai para (5000,3000,-2000): B vê (5000,3000,-1997) ✔
4) A metralha B: fuselagem de B 100 -> 44, e A concorda ✔
5) dano até o fim: B cai, e A vê B cair                ✔
6) um celular entra na sala de A: vira PILOTO, e o
   avião do B continua contando como jogador           ✔
```

---

## O míssil voava de lado

> *"a perspectiva de ver ele tá estranha… eu vejo ele indo de lado, quando na
> verdade tenho que ver ele de trás."*

Uma linha, e dessas que só existem porque o código mudou por baixo:

```js
b.no.lookAt(b.x + b.vx, b.y + b.vy, b.z + b.vz);
b.no.rotateX(Math.PI/2);
```

O `lookAt` já aponta o **+Z** do objeto para onde ele vai. O quarto de volta a
mais existia por causa da **bomba**, que é uma cápsula deitada no eixo Y — é
ele que leva o eixo da cápsula para a frente.

Só que o míssil novo já nasce montado apontando para +Z. Ele estava levando
esse quarto de volta em cima do que já estava certo, e saía voando de
través. Agora o giro extra vale só para a bomba. Medido: o nariz do míssil
está a **0,0°** da direção em que ele voa, e o eixo da bomba continua a 0,0°
da direção em que ela cai.

## O estol precisava de um tom de desespero

> *"o som do travamento tá PERFEITO, é esse o nível de estresse que temos que
> ter na cabine. O ESTOL, que é algo desastroso, não tá com esse tom de
> desespero."*

Estava um `bip` de 180 Hz a cada 1,1 s. Soava como um forninho avisando que o
pão ficou pronto.

Buzina de estol de verdade é **contínua**, áspera, e não deixa pensar em outra
coisa — é essa a função dela. Como esta é feita:

- **duas dentes-de-serra desafinadas** (392 e 407 Hz): o batimento entre as
  duas é o urro. Uma só sairia limpa demais;
- uma terceira duas oitavas abaixo, para ter peso;
- **passa-banda com Q alto** por cima, que é o que dá cara de corneta barata
  em vez de sintetizador;
- **tremor de 9 Hz na amplitude** — e é esse o detalhe que importa. Sem ele
  era só um som feio; com ele, é um som *aflito*. A diferença entre barulho e
  urgência está no ritmo, não no timbre.

E não para até o avião voltar a voar. A tela acompanha: uma borda vermelha
pulsando no mesmo compasso, porque um aviso de texto se perde no meio de uma
manobra.

## O controle treme junto

> *"quando eu solto o míssil, ou o atiro, ou metralho, tem que tremer o meu
> controle."*

O recado de tremer vai **na hora**, fora do pacote de estado — que só sai de
250 em 250 ms, tarde demais para casar com o estalo de um tiro.

O motorzinho do celular só sabe ligar e desligar, então quem dá caráter a cada
arma é o **ritmo**:

| o que aconteceu | como treme |
|---|---|
| metralhadora | contínuo enquanto o gatilho estiver apertado |
| míssil | um tranco curto e um longo — o sopro da saída |
| bomba | um baque só, grave e comprido |
| travou o alvo | três toques secos, no ritmo do som de travamento |
| levou tiro | dois trancos fortes |
| estol | batida lenta e insistente, que não para |

**Duas decisões que valem explicar.**

A metralhadora **não manda um recado por tiro**. A 14 tiros por segundo seriam
14 mensagens e 14 tremidinhas que o motorzinho nem consegue separar. Vai
"começou" e "parou", e quem faz o padrão contínuo é o celular.

E o contínuo **se reprograma sozinho**, um pouco antes de o padrão acabar:
`navigator.vibrate` não tem laço, o padrão toca uma vez e morre. Sem
reprogramar antes do fim, fica um buraco audível entre uma volta e outra.

Medido, com um celular de verdade ligado numa sala de verdade e o vibrador
espionado: míssil chega `[45,35,130]`, bomba `[180]`, metralhadora manda 4
padrões contínuos em 1,6 s e **manda `0` ao soltar o gatilho** (que é o que
cala o motorzinho). No estol, a buzina liga junto com o tremor e os dois
calam quando a potência volta.

---

## O estol jogava para cima quando se estava de cabeça para baixo

> *"eu estava de cabeça para baixo e o ESTOL me chocou para cima e não para o
> chão."*

O código era:

```js
giraPar(eixoF, eixoC, -falta*1.1*dt)     // baixa o nariz na direção do
                                          // CHÃO DA CABINE
```

Voando normal dá no mesmo, porque o chão da cabine aponta para a Terra. De
cabeça para baixo ele aponta para o céu — e o estol atirava o avião para cima.

**Asa que para de sustentar não sabe onde fica a barriga do avião.** Ela
simplesmente larga, e quem manda dali em diante é a gravidade. Então o giro
passou a ser em torno de um eixo **horizontal** perpendicular ao nariz, no
sentido que abaixa o bico, seja qual for a posição do avião:

```js
let h = vcruz(eixoF, {x:0,y:1,z:0});      // eixo horizontal, perpendicular ao nariz
// com h = nariz × cima, o ângulo NEGATIVO sempre abaixa o nariz
eixoF = giraEmTorno(eixoF, h, -falta*1.1*dt);
eixoC = giraEmTorno(eixoC, h, -falta*1.1*dt);
eixoD = giraEmTorno(eixoD, h, -falta*1.1*dt);
```

Os três eixos giram juntos: é o corpo inteiro caindo de bico, sem torcer as
asas. Precisou de uma função nova — `giraEmTorno`, a fórmula de Rodrigues —
porque o `giraPar` só sabe girar dentro do plano de dois vetores do próprio
avião, e aqui o eixo é do **mundo**.

Medido em seis atitudes: nivelado, de cabeça para baixo, de faca para os dois
lados, inclinado 45° e subindo 30°. Em todas o nariz cai e o avião perde
altura, e a inclinação das asas não muda (45° antes, 45° depois).

## O tremor aerodinâmico — o aviso ANTES do estol

> *"quero mais desespero na cabine. O controle tem que tremer nos tiros, tem
> que tremer quando estiver perto do estresse aerodinâmico."*

Avião de verdade avisa antes de largar: a asa começa a descolar o ar perto da
ponta e a cabine inteira **treme**. É o aviso mais honesto que existe, porque
você sente antes de ler qualquer instrumento.

De 1,22× a velocidade mínima até ela, um número `estresse` sobe de 0 a 1 e
aciona quatro coisas ao mesmo tempo:

| | |
|---|---|
| **som** | ronco grave e sujo — ruído por um passa-baixa que abre conforme aperta |
| **câmera** | sacolejo que cresce com o quadrado do estresse (leve some, forte sacode) |
| **celular** | tremor rápido e miúdo, diferente do estol (lento e pesado), para dar para saber qual é qual na mão |
| **tela** | faixa amarela nas bordas que aperta, e "VELOCIDADE BAIXA" piscando |

Quando o ronco vira buzina e a faixa vira vermelha, já é tarde: isso é o
estol.

O sacolejo da câmera virou coisa geral, e agora a cabine também sacode ao
disparar (leve na metralhadora, forte no míssil), ao levar chumbo e ao bater.

### O erro que o teste não pegaria

`Controles.treme()` é chamado **a cada quadro**. A trava que evita mandar
recado repetido existia só para a metralhadora — o tremor aerodinâmico e o
estol estavam mandando **60 mensagens por segundo**, entupindo o canal e
reiniciando o padrão do vibrador antes de ele chegar a tocar. Agora a trava
vale para todos: uma mensagem por *mudança*.

Medido com um celular de verdade ligado: 3 segundos dentro do tremor
aerodinâmico geram **2 pedidos** ao vibrador. Mandando por quadro seriam 180
mensagens e mais de cem pedidos.

---

## Jogando DIRETO no celular

O Brunno foi testar o 3D abrindo o jogo no próprio celular, em vez de usar o
celular como controle de uma tela grande. Aí apareceram duas faltas que eu não
tinha visto, porque nunca tinha exercitado esse caminho.

### O leme velho ainda estava lá

O leme por **apontar** eu tinha escrito só no `controle.html`. Jogando direto
no aparelho, quem lê o sensor é a página do jogo — e ela continuava com o leme
antigo, o de deslizar, que nunca funcionou. A mesma conta foi para o
`aviao3d`, com o deslize de novo como plano B para aparelho que não dê `alpha`.

É o preço de ter dois lugares lendo o mesmo sensor. Ficou anotado: **toda
mudança no sensor tem de ir nos dois**.

### Não havia manete, nem nitro, nem trem, nem flapes

Esses comandos moram no `controle.html`. Sem um segundo aparelho, o avião voava
sempre na mesma potência — não decolava e não pousava, que são justamente as
duas coisas novas.

Então a tela do jogo ganhou os mesmos comandos, **nos mesmos lugares**, porque
a mão já aprendeu onde eles ficam: nitro na borda esquerda, manete na direita,
gatilho no canto direito de baixo, armas por deslize no canto esquerdo, e
trem/flapes/zerar numa fileira em cima.

Eles só aparecem quando **não** há um celular separado fazendo de controle —
com controle seriam dois donos do mesmo avião. E se um controle entrar no meio
do voo, os botões sumem sozinhos.

### Toque e mouse contavam o mesmo gesto duas vezes

Num aparelho de toque o navegador ainda dispara eventos de mouse **depois** do
toque, por compatibilidade com páginas antigas. Sem tratar, cada gesto valia
duas vezes — um toque no seletor pulava duas armas. A trava é simples: gesto de
mouse é ignorado se houve toque nos últimos 700 ms.

Também apareceu uma fragilidade de verdade: `e.touches[0]` estava sendo lido
sem conferir, em três lugares. Num celular sempre vem um dedo, mas um evento
sem ponto derrubava o laço do jogo inteiro. Agora todos conferem.

### O rearranjo da tela

Com os comandos ocupando as duas bordas, os painéis de canto ficavam por
baixo deles. O que mudou no modo de dedo:

- os painéis das quatro quinas recuam a largura da tira lateral;
- a caixa do combustível desce para a coluna da esquerda, liberando o meio de
  cima para os três botões;
- o painel do pouso vira uma **tira deitada** no rodapé, entre o seletor de
  armas e o gatilho, com os rótulos escondidos — e sem repetir trem e flapes,
  que já estão escritos nos próprios botões;
- o olho e a qualidade recuam para dentro da tira do acelerador.

Medido em três telas (844×390, 915×412 e 667×375), com treze elementos
conferidos dois a dois: **nenhuma sobreposição e nada fora da tela**. Foram
três rodadas até chegar lá — a cada arrumação aparecia uma colisão nova, e num
celular pequeno três de uma vez.

### O teste que se enganou sozinho

Numa das rodadas o seletor de armas "não respondia". O comando estava certo: o
teste tinha aberto a manete a 95% com o avião **parado na pista**, ele correu,
saiu da pista, bateu — e a tela de capa voltou e cobriu os botões. O
`elementFromPoint` no ponto do toque devolvia `codigo`, que é um elemento da
capa. Foi o que entregou.

---

## Seis coisas depois de jogar sozinho no celular

### O celular não tremia com nada

E o motivo era bobo: o recado de tremer ia **só para os celulares ligados como
controle**. Jogando sozinho no próprio aparelho não existe controle nenhum —
o recado saía e não chegava a lugar algum.

Agora cada recado vai para os dois lados: pela rede, para quem estiver de
controle, **e** para o vibrador deste aparelho. No computador o
`navigator.vibrate` não existe ou não faz nada, e sai de graça.

E treme em mais coisa, que era o pedido ("ele tem que tremer no caos"): pegar
tambor, derrubar alvo, abater avião, tocar na pista, sair do chão, o estouro
do míssil, a nuclear (conforme a distância) e a batida — essa com um padrão
longo e feio, de cinco trancos.

### A nuclear na pista

Dava para soltar a bomba parado no chão. Ela caía a dois palmos do avião e o
cogumelo abria em cima de quem soltou: suicídio de graça, e na **primeira
coisa que se aperta no jogo**, porque a arma inicial era justamente a nuclear.

Duas correções: a bomba é recusada com as rodas no chão, e o avião passou a
nascer na **metralhadora**.

### A decolagem: agora o avião ROTACIONA

Era o pulo mais feio do jogo. Na pista o manche não fazia **nada** até a
velocidade de decolagem — e aí o avião saltava para 15° de uma vez
(`giraPar(eixoF, eixoC, 0.26)` no instante da saída).

Dois problemas de uma vez: sem velocidade, puxar não fazia nada e parecia que
o comando tinha morrido; com velocidade, sair do chão era um salto.

Avião de verdade **rotaciona**: puxando, a roda do nariz sai primeiro e ele
corre um pedaço apoiado só nas rodas de trás, de bico para cima. Se não tiver
velocidade para voar, é só isso que acontece — que é exatamente o que o
Brunno pediu. Quanto o nariz sobe depende do ar que passa pela cauda, então
começa a valer lá pelos 40% da velocidade mínima e cresce daí.

E sair do chão deixou de mudar a posição: a atitude já é a que o avião ganhou
rotacionando, então largar o apoio não muda nada. Medido: **0,00° de mudança
de arfagem no quadro da decolagem** (antes, 15°).

### O míssil ganhou uma porção nuclear

O estouro dele era uma bolinha de faíscas. Virou uma nuclear em miniatura:
clarão, bola de fogo, anel, um cogumelo pequeno e o mesmo baixo grave da
grande, só que curto. A diferença para a bomba não é de tipo, é de
**tamanho** — 22% do raio e um terço do tempo. É o que dá para sentir que é
da mesma família sem virar o fim do mundo a cada tiro.

Para isso o `somNuclear` ganhou uma escala: o mesmo desenho de som, encolhido.

### O som do avião

Eram três osciladores tocando juntos (62, 124 e 372 Hz). Dava um **zumbido de
abelha grande**, não um avião.

Turbina tem três partes bem distintas, e é a mistura delas que o ouvido
reconhece:

1. **o sopro** — de longe o mais importante, e o que não existia. É RUÍDO por
   um passa-banda: o ar sendo rasgado. Sem ele, nenhuma quantidade de
   oscilador soa como avião;
2. **o ronco** grave da combustão, uma dente-de-serra lá embaixo;
3. **o assobio** agudo do compressor, um seno fino por cima.

As três andam com a velocidade, mas **em proporções diferentes**: o assobio
quase dobra de frequência da marcha lenta ao turbo (992 → 1854 Hz medidos), o
ronco sobe pouco, e o sopro abre o filtro em vez de mudar de tom. É essa
diferença que faz acelerar *soar* como acelerar, em vez de só ficar mais alto.
No chão o conjunto é mais abafado: o avião ainda não está cortando o ar.

### O teste que estava velho

O botão do trem "falhou" — e estava certo: recolher o trem com as rodas
apoiadas é recusado de propósito. O teste é que ainda esperava o
comportamento antigo. E, ao corrigi-lo, aprendi outra coisa: pôr
`noChao = false` não basta para "estar no ar", porque a 150 do chão o jogo
pousa de novo no quadro seguinte. Que é a prova, de graça, de que o pouso
funciona.

---

## Fazer funcionar no iPhone

Três buracos, e o primeiro é grande.

### O iPhone não tem vibração

O Safari do iPhone **não tem `navigator.vibrate`**. A API de vibração nunca
existiu lá. Todo o tremor que eu escrevi — míssil, metralhadora, estol, tremor
aerodinâmico, batida — não fazia absolutamente nada num iPhone.

O que ele tem, do iOS 17.4 em diante, é o **retorno háptico do interruptor**:
um `<input type="checkbox" switch>` dá um toque no motorzinho ao mudar de
estado, e clicar no rótulo dele por código provoca esse toque. Fica escondido
fora da tela e serve de tique.

É bem menos do que a vibração do Android: dá para bater **um tique**, não uma
duração. Um padrão como `[45, 35, 130]` — no Android "vibra 45, pausa 35,
vibra 130" — vira aqui "dois tiques, com 80 ms entre eles".

**O ritmo sobrevive; a força, não.** E aqui uma decisão antiga pagou sozinha:
os padrões foram escritos com **ritmos diferentes entre si**, não com
intensidades diferentes — a metralhadora é miúda e rápida, o estol é lento e
pesado, o míssil é curto-e-longo. Isso atravessa os dois mundos. Se eu tivesse
diferenciado por força, no iPhone tudo soaria igual.

Num iPhone mais antigo nem o interruptor existe, e o jogo segue sem tremor,
sem reclamar. E o Android continua no caminho de sempre, com o padrão inteiro
— conferido.

### O contexto de áudio era novo a cada clique

`ligaAudio()` criava um `AudioContext` **novo** toda vez que era chamado — e
ele é chamado no botão de jogar, no de dedo e no de entrar na batalha.

No computador isso passava batido. No iPhone, onde o contexto só acorda dentro
de um toque, o segundo clique trocava o contexto **por baixo do motor**, que
continuava tocando no antigo — mudo. Agora cria uma vez e nas seguintes só
manda acordar, que é exatamente o que o iPhone precisa.

### O iPhone não deixa travar a tela

Nem `screen.orientation.lock` nem tela cheia existem no Safari do iPhone. O
`controle.html` já contornava isso girando a página por CSS, mas o **jogo**
não tinha tratamento nenhum: em pé, o horizonte sumia e os comandos
empilhavam.

Girar por CSS uma tela de WebGL é outra conversa — muda o tamanho do quadro e
as coordenadas do toque. Então o jogo faz o honesto: em pé, **pede para virar
e segura o jogo**; ao virar, volta de onde parou. No computador, onde não há
toque, o aviso não aparece nunca, por mais alta que seja a janela.

### Medido num iPhone de mentira

Um navegador com `navigator.vibrate` apagado, sem `requestFullscreen` e sem
`orientation.lock`:

```
caminho de tremor escolhido ............ interruptor háptico  ✔
o jogo começa sem tela cheia ........... jogando               ✔
ligaAudio() de novo -> MESMO contexto .. sim                   ✔
soltar o míssil ........................ 2 tiques              ✔
metralhar .............................. 11 tiques, e para ao soltar ✔
girar para retrato ..................... pede para virar e segura ✔
girar de volta ......................... volta de onde parou   ✔
o controle.html ........................ mesmo caminho, 2 tiques ✔
Android (com vibrate) .................. padrão inteiro, como antes ✔
computador em janela alta .............. sem aviso de girar    ✔
```

**O que eu não consigo garantir daqui:** se o iOS exige que o clique no
interruptor esteja dentro de um gesto do dedo para soltar o háptico. Se
exigir, o tremor vai sair nos toques e não nos eventos do jogo. Isso só um
iPhone de verdade responde.

---

## O avião-dragão

> *"O avião é o objeto que vemos praticamente no jogo todo. Ele tem que ser o
> objeto mais bem trabalhado."*

Era verdade e era uma crítica justa. O que estava lá era um caça branco: certo
de forma — fuselagem de revolução, asa em flecha, derivas duplas — e sem
personalidade nenhuma. Dava para trocar por qualquer outro avião branco e
ninguém notava.

O que entrou no lugar é um **brinquedo**: azul com amarelo, redondo, com cara
de dragão amigável no bico, asas de morcego, hélice na frente e duas
turbininhas atrás. Peças grandes, poucas, todas reconhecíveis de longe.

Três regras mandaram no desenho:

1. **Tudo é redondo.** O corpo é um torno, o focinho é uma esfera achatada, as
   pontas são cones de poucos lados. Brinquedo bom não tem quina.
2. **O amarelo é estrutura, não enfeite.** Membrana da asa, chifres, focinho,
   aros das turbinas e cubos das rodas — o olho junta tudo isso e lê "é a mesma
   peça". É o que dá unidade.
3. **O tamanho não mudou.** Mesmo comprimento e mesma envergadura do caça, para
   a câmera, o trem de pouso, as colisões e a altura de pouso continuarem
   valendo sem nenhum outro ajuste.

### As quatro vezes em que ele ficou errado

Modelar sem ver é impossível, então cada rodada foi: montar, **fotografar de
seis ângulos** com o navegador de teste, olhar e consertar.

| o que saiu | por quê | o conserto |
|---|---|---|
| um **balão** | o perfil tinha diâmetro quase igual de ponta a ponta | cauda que afina de verdade: raio 58 no meio, 6 na ponta |
| as faixas laterais foram parar **na barriga e no lombo** | depois de deitar o torno, `phi=0` é a barriga e `phi=π` é o lombo — as laterais são ±π/2 | fatia do mesmo torno em ±π/2 |
| uma **cruz preta em cima da cara** | quatro pás pretas de 150, plantadas na frente do rosto | duas pás azuis de 104, mais à frente, e um disco quando gira |
| o rosto **só existia de frente** | de lado, uma bola azul e um borrão branco | focinho que adianta e desce, boca que corre pela mandíbula, presa por fora, chifres deitados |

### O olho, que deu três voltas

Onde pôr a íris foi um cabo de guerra perdido duas vezes. Bolinha grudada para
a frente: some de perfil. Bolinha para fora: some de frente. O meio-termo
perdeu dos dois lados ao mesmo tempo.

O erro estava em pensar a íris como uma **peça**. Olho de verdade não tem
bolinha pendurada — tem uma **mancha pintada no globo**. Então a íris virou um
pedaço de casca esférica de mesmo centro e um fio de raio a mais, cobrindo 60°
de olhar: como acompanha a curva, aparece inteira de frente e inteira de lado.

A pupila tentou ser casca também e saiu **retangular** — recorte de esfera é
retângulo em (phi, theta), e o bicho ficou com dois olhos de televisão. Ela
voltou a ser bola, mas **afundada na medida**: a 18,5 do centro de um globo de
21, põe para fora uma calota larga, redonda de todo ângulo. (Antes estava a 16
com raio 8,5 e mal vazava — daí ter sumido.)

### O preço, e como ele foi pago

O dragão ficou bonito e ficou caro:

```
                     peças   triângulos     cena inteira
caça branco             33        3.244    2.796 ordens / 226k
dragão, peça a peça     83       10.852    6.047 ordens / 770k
```

Para a placa de vídeo, malha não custa pelo tamanho: custa por ser mais uma
**ordem de desenho**. Com o céu cheio de inimigos, 6.000 ordens num celular é
o fim.

A saída não custou desenho nenhum. Depois de montado, o avião não mexe mais nas
suas peças — só o grupo inteiro gira. Então dá para **cozinhar tudo**: cada peça
é passada para o lugar onde está e todas as que dividem a mesma cor viram uma
malha só. Mesmo triângulo por triângulo, mesma cara, mesma sombra — mas saem
sete ordens em vez de oitenta e três. (A hélice fica de fora: essa gira
sozinha.) Junto com uma poda de segmentos onde ninguém vê — o olho gastava
sozinho 3.000 triângulos —, o resultado:

```
dragão, cozinhado        32        6.052    2.288 ordens / 343k
```

Menos ordens que o caça branco tinha, com o dobro de desenho.

`BufferGeometryUtils` faria a fusão pronta, mas ele mora nos *examples* do
three.js e aqui só está o núcleo. O serviço é curto: tirar o índice, aplicar a
matriz, emendar os vetores.

### O bug que o avião novo revelou

Enquanto isso o teste de **dois navegadores** começou a falhar: o avião de B
entrava na sala de A e A não via ninguém. Nada a ver com rádio — com o laço de
desenho parado a conexão fechava na hora.

A causa estava num **chute de 4 segundos**. Quem abre uma ligação com a tela do
jogo pode ser um avião entrando na batalha (`{t:'entra'}`) ou um celular
virando artilheiro (`{t:'oi'}`) — e havia um relógio que, se ninguém falasse em
4 s, decidia "é celular". Isso é uma corrida: se o `entra` demorasse mais que
isso — rede ruim, celular fraco, a tela do anfitrião engasgada —, o **jogador
entrava como artilheiro**. Ele via a batalha; a batalha não via ele.

O avião mais pesado derrubou o teste de 6,6 para 5,7 quadros por segundo, e
isso bastou para o chute passar na frente do aperto de mão. Mas o bug já estava
lá, esperando um celular ruim.

Corrida nenhuma se ganha andando mais depressa: o que resolve é **tirar o
segundo corredor**. Os dois lados já se anunciam sozinhos, então o relógio foi
para 15 s — tempo de sobra para o primeiro pacote de qualquer um. Quem chega
depois disso é mesmo alguém que abriu a ligação e não falou.

---

## Duas portas no mesmo QR

> *"Quando alguém ler o QR code, a pessoa tem que poder escolher entre ser
> copiloto ou enfrentar a batalha aérea também."*

Até aqui o QR só tinha um destino: `controle.html`, e quem lia virava
**tripulante da mesma cabine** — copiloto, artilheiro, torre. Era o desenho
antigo, de quando o jogo era uma TV com celulares em volta. Com a batalha
aérea existindo, a mesma etiqueta passou a servir duas vontades diferentes:

- o irmão que quer **sentar do lado** e dividir este avião;
- o outro que quer **o avião dele** no céu, para brigar.

### Por que a escolha mora no controle, e não no QR

A tentação era fazer dois QR. Mas duas etiquetas na tela é uma decisão a mais
para quem está *olhando de longe*, e nessa hora ninguém lê legenda — aponta a
câmera e pronto.

Então o QR continua um só, e a escolha acontece **depois de ler**, no celular,
onde a pessoa já está com o aparelho na mão e o código já veio preenchido:

```
Código da tela de quem chamou
          ┌──────┐
          │ 73YB │
          └──────┘
   [ Ser copiloto desta tela ]     ← comanda o avião que já está na tela
   [ Levar o meu avião · batalha ] ← abre o jogo aqui, avião só seu
```

O mesmo código serve aos dois caminhos sem mudar nada: para o copiloto é a
**sala** onde ele entra; para o avião é o **código da batalha**.

O segundo botão não conecta nada — `controle.html` é o controle, ele não voa.
Ele **troca de página**: vai para `aviao3d.html?batalha=73YB`, que abre a sala
própria do celular e entra sozinho no céu de quem chamou, sem ninguém digitar
código de novo.

### E a sala própria continua aberta

Quem chegou com avião próprio também tem um código e um QR — então um terceiro
celular pode sentar de copiloto **no avião dele**. Uma coisa não atrapalha a
outra: tripulação e batalha são duas listas separadas, e a mesma ligação de
rede serve às duas.

### Dois monitores, um celular em cada

A pergunta que veio junto: *o outro jogador também tem monitor — como ele
controla pelo celular dele?* Não tem truque: **cada tela tem a sua sala**. O B
liga o celular dele na sala dele e digita o código do A na caixa da batalha.
Medido com quatro páginas de navegador ao mesmo tempo:

```
tela A = sala 5NAU | tela B = sala 6J2F
cada tela com o seu piloto de celular ................. ✔
na batalha: A anfitriã vê 2 | B convidado vê 2 ........ ✔
nenhum celular foi derrubado pela batalha ............. ✔
girei o CELULAR de B a 45°: a asa de B girou .......... ✔
o avião de A não se mexeu junto ....................... ✔
```

E o caminho novo, ponta a ponta:

```
o QR aponta para .................. controle.html?sala=73YB
o celular abriu com o código já digitado e duas portas . ✔
escolheu COPILOTO: senta na mesma cabine ............... ✔
escolheu MEU AVIÃO: foi para aviao3d.html?batalha=73YB . ✔
   abriu sala própria 3CVK e entrou sem digitar nada ... ✔
o copiloto continuou, e o segundo virou adversário ..... ✔
a tela vê o avião dele no céu, na posição certa ........ ✔
```

### Um bug velho que a segunda porta destampou

Com mais um botão, o título da tela de entrada **sumiu** num celular de 375 de
altura — e não dava para rolar até ele.

É uma armadilha antiga do flexbox: `justify-content:center` junto com
`overflow:auto` faz o conteúdo que não cabe sobrar para os **dois** lados, e o
que sobra para cima fica *acima do zero da rolagem* — cortado e inalcançável.
A palavra `safe` desliga a centralização exatamente nesse caso e encosta o
conteúdo no topo, que é de onde a rolagem começa. Uma palavra:

```css
justify-content: center;        /* para quem não conhece `safe` */
justify-content: safe center;   /* para quem conhece */
```

**O que eu não consigo garantir daqui:** se ler o QR num iPhone abre o
`controle.html` no Safari ou dentro do app da câmera — se abrir numa janelinha
embutida, o pulo para o `aviao3d.html` pode perder a tela cheia. Isso só um
iPhone de verdade responde.

---

## A entrada, refeita: duas perguntas, dois passos

> *"Quando outra pessoa acessar a página, tem que dar a opção de entrar na sala
> ou escolher outra sala. Ao fazer isso, tem que selecionar se é a tela do jogo
> ou do controle. Ao escolher a tela do jogo, tem que dar a opção de usar o QR
> code para conectar o controle do outro jogador. Tá muito confuso."*

Estava mesmo, e o defeito era meu. Eu tinha resolvido o **mecanismo** — o
celular já podia virar controle ou trazer o próprio avião — e deixado a porta
de entrada do jeito que estava: um campo de código e dois botões lado a lado.
A pessoa digitava quatro letras sem saber o que cada botão ia fazer com elas.

### Duas perguntas não cabem numa tela só

Existem duas perguntas de verdade, e elas são independentes:

1. **Em qual sala?**
2. **Este aparelho vai ser o quê?** — a tela do jogo, ou o controle

Empilhar as duas numa tela só foi o erro. Agora é uma de cada vez, e o passo 2
mostra a resposta do passo 1 escrita em cima, com um *trocar de sala* embaixo:

```
PASSO 1                        PASSO 2
  Em qual sala?                  SALA PTC9
    ┌──────┐                   Este aparelho vai ser…
    │ ABCD │                     [ O CONTROLE            ]
    └──────┘                     [ A TELA DO JOGO        ]
    [ Continuar ]                       trocar de sala
```

Quem chegou pelo QR **já respondeu a primeira pergunta sem saber** — o código
veio no endereço. Então o passo 1 seria uma tela a mais só para confirmar o que
já está escrito: ele é pulado, e o *trocar de sala* fica ali para quem leu o QR
errado.

### E o QR do outro jogador

Quem escolhe **A TELA DO JOGO** já entra na batalha de quem chamou — e cai numa
capa que, até ontem, tinha duas caixas de código com a mesma cara. Voltava à
estaca zero.

Agora a capa **diz em que ponta da corda a pessoa está**, e as duas caixas
deixaram de parecer a mesma coisa:

```
  Esta é a TELA DO JOGO — o avião voa aqui.

  ┌ 1 · Ligar um celular nesta tela ────────┐   ← QR e código DESTA tela
  │  para comandar ESTE avião               │
  └─────────────────────────────────────────┘
  ┌ 2 · Voar no céu de outra tela ──────────┐   ← o código DA OUTRA
  │  opcional; vocês se veem e se derrubam  │
  └─────────────────────────────────────────┘
```

E para quem chegou pela escolha, a caixa 1 vem **acesa**, dizendo exatamente o
que falta: *"você já está na batalha PTC9. Falta ligar o seu controle, aqui
embaixo."*

Medido com quatro páginas, o caminho inteiro:

```
leu o QR -> caiu no passo "papel", sala PTC9 ...... ✔ não repetiu a pergunta
"trocar de sala" -> volta ao passo 1 .............. ✔
escolheu O CONTROLE -> a tela ganhou 1 piloto ..... ✔
escolheu A TELA DO JOGO -> sala própria RUL8,
   já na batalha, caixa do QR acesa ............... ✔
o controle DELE entrou pelo QR DELE ............... ✔
placar: duas telas, um controle em cada, mesma batalha ✔
```

---

## O monitor mudo

> *"No outro terminal, com o iPhone, o monitor ficou sem som."*

A causa é uma regra do navegador que aqui pegou de lado. **Som só sai depois de
um gesto naquela página** — e quando se joga pelo celular, a página da tela pode
não receber gesto nenhum: quem apertou "Começar" foi o telefone, e o `comeca()`
chegou pela rede. Para o navegador aquilo é uma aba querendo tocar som sozinha,
e ele segura. O jogo rodava perfeito e mudo.

Duas correções, porque uma só não cobre:

1. **Qualquer toque na tela serve de chave.** Antes só os botões da capa
   chamavam `ligaAudio()`. Agora um clique em qualquer lugar, uma tecla, um
   toque — tudo destrava. Quem esbarrar no monitor resolve sem saber.
2. **Se ainda assim continuar mudo, dizer.** Um botão 🔇 *ligar o som* aparece
   no rodapé enquanto o som está preso e some no instante em que ele sai. Sem
   isso a pessoa fica achando que o jogo não tem som — foi o que aconteceu.

**Confirmado num iPhone de verdade:** *"o som deu certo no iPhone"*. Aqui o
navegador do contêiner solta o som sem gesto nenhum, então a trava de verdade
não dava para reproduzir — só a lógica, com o áudio preso na mão. O aparelho
respondeu a pergunta que o teste não conseguia responder.

Isto vale anotar porque é o padrão que se repete neste projeto: **o teste prova
que o código faz o que eu escrevi; só o aparelho prova que era isso que
precisava ser escrito.** Foi assim com o sentido da rolagem, com o estol de
cabeça para baixo, com o tremor no celular — e agora com o som. O laço é o
mesmo: eu meço o que dá para medir daqui, digo em voz alta o que ficou de fora,
e alguém liga o aparelho.

O que o teste daqui provou:

```
começou pelo celular, sem tocar no monitor:
  áudio=suspended, botão "ligar o som" aparece ... ✔
tocou no botão: áudio=running, motor ligado,
  e o aviso sumiu ................................ ✔
clique em lugar nenhum da tela: áudio -> running   ✔
```

---

## Munição infinita para teste

No mesmo molde do combustível infinito que já existia: ligada por padrão, tecla
**M** liga e desliga, `?municao=0` no endereço devolve as balas contadas. O
contador, na tela e no celular, mostra **∞**.

Sem isso não dava para ficar meia hora provando o míssil perseguidor — acabavam
as oito e o teste acabava junto.

---

## O estouro do míssil, sem cogumelo

> *"Tira esse cogumelo do míssil. Tenta melhorar ela."*

Ali morava um cogumelo em miniatura, de quando o pedido foi *"os mísseis têm que
ter uma porção nuclear"*. A ideia estava certa e a **peça** estava errada:
cogumelo é uma coluna que sobe do chão por dez segundos, e o que acontece num
tiro ar-ar é o contrário — estoura em meio segundo, no ar, e some. Encaixar a
peça grande encolhida deixava uma torrinha cinza pendurada no céu depois de cada
míssil, entulhando a vista bem na hora da briga.

O que faz um estouro no ar ser lido como estouro são três coisas, nessa ordem:

1. **O anel de choque** — é ele que diz "isto explodiu". Um aro fino que abre
   depressa e some. Sem ele, fogo é só fogo.
2. **A bola de fogo**, que cresce rápido e apaga em meio segundo. Fogo que dura
   parece cenário.
3. **A fumaça**, que fica um pouco depois de tudo apagar. É ela que deixa a
   marca no céu — e agora é uma bolinha, não uma torre.

### Três erros no caminho

**O anel virou um pneu.** Espessura 0,82–1 e abertura até 3× o raio: na tela era
uma argola de fumaça do tamanho da cidade, em volta do avião. Anel de choque é
um risco de luz — 0,94–1, e abre 2,4×.

**Somar luz em tudo deixou o fogo branco.** `AdditiveBlending` é o que separa
fogo de tinta, mas somar sobre um **céu claro** satura: claro + laranja =
branco. O estouro virou uma bola de leite e o laranja sumiu. A divisão que
funciona é a de uma chama de verdade:

| peça | mistura | por quê |
|---|---|---|
| corpo da bola | normal, laranja | garante a cor contra qualquer fundo |
| miolo | aditiva | só o centro é quente demais para ter cor |
| anel | normal | aditivo, sobre o céu, ele sumia |

**As faíscas eram pedregulhos.** Raios de 90 a 150 num avião de 500 de ponta a
ponta: no primeiro quadro, antes de se espalharem, dez bolas escuras empilhadas
tapavam o próprio fogo. Viraram 26 a 40.

```
estouro do míssil: cogumelos 0, peças de fogo 3, clarão 0,43, vibrou  ✔
0,8 s depois: 0 peça(s) de fogo                                      ✔ não deixa entulho
```
