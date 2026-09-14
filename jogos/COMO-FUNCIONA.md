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

---

## O tremor que não chegava

> *"Eu acho que não senti também a vibração no Android. E também não sentiram
> no iPhone."*

Dos dois lados. No Android o `navigator.vibrate` é caminho direto, sem truque
nenhum — se lá também não vibra, o defeito é meu. E era: **dois**, somados.

### 1. Metade dos tremores nunca saía do jogo

A tabela de padrões existia **duas vezes**: uma no jogo e outra no
`controle.html`. O recado que atravessava a rede levava só o **nome** do
tremor, e o outro lado procurava o padrão na cópia dele:

```js
if (PADROES[a]) vibra(PADROES[a]);      // no controle.html
```

O jogo cresceu e passou a mandar nove nomes. O controle continuou conhecendo
quatro. Então `explode`, `bateu`, `tocou`, `pegou` e `alvo` chegavam, não
achavam o nome na tabela e **caíam no chão calados** — sem erro, sem aviso,
sem nada. Explodir um avião, bater no chão, pousar, pegar um tambor, acertar
um alvo: nada disso chegava a nenhum controle, e não havia como desconfiar.

Duas tabelas que precisam ser iguais um dia ficam diferentes. A correção não é
copiar a tabela de novo — é **mandar o padrão junto com o recado**. Quem sabe o
que aconteceu é quem manda; o controle só toca o que chegou. A tabela de lá
continua existindo como reserva para um recado de versão antiga, mas parou de
ser necessária, e é isso que a impede de desandar outra vez.

### 2. E os que chegavam eram curtos demais para sentir

Vibrador de celular moderno não é o motorzinho desbalanceado de antigamente: é
um solenoide (LRA), e ele leva uns **20 ms só para pegar o embalo**. Olhando os
tempos com isso em mente:

| tremor | ligado, antes | depois |
|---|---|---|
| tremor aerodinâmico | **16 ms** | 32 ms |
| metralhadora | **26 ms** | 42 ms |
| travamento | 22 ms | 40 ms |
| míssil | 45+130 ms | 70+180 ms |

Um pulso de 16 ms não chega a acontecer. Um de 26 ms é cócega. E quem está
jogando **não está com o aparelho parado na mesa** — está inclinando o celular
para virar o avião, com o braço em movimento. O que mal se sente parado some
inteiro no meio do gesto.

Todos os tempos *ligado* dobraram; as pausas ficaram quase iguais, porque quem
manda no que se sente é o tempo ligado, não a pausa. O ritmo de cada um
continua o mesmo — é ele que deixa reconhecer na mão qual é qual sem olhar.

### 3. Um botão para a próxima vez

Daqui eu não sinto o aparelho de ninguém, e *"não senti"* pode ser três coisas
diferentes: o recado não chegou, o padrão é fraco, ou o aparelho não vibra.
Então entrou um **testar o tremor** nos dois lados — na entrada do controle e
na capa do jogo — junto de uma linha dizendo qual caminho está em uso:

```
tremor: pelo vibrador (Android)      [ testar o tremor ]
tremor: pelo háptico do iPhone
tremor: este aparelho não tem
```

O padrão do teste é longo de propósito (220–120–220–120–420): não precisa caber
em ritmo nenhum, precisa ser **sentido**. Se esse não passa, nenhum passa — e
aí o relato deixa de ser "não senti" e vira "apertei e não senti", que é outro
defeito, com outro conserto.

```
o controle diz "tremor: pelo vibrador (Android)"
  e o botão de prova soltou [220,120,220,120,420] ...... ✔
os 9 tremores do jogo: chegaram 9/9 .................... ✔ nenhum cai no chão
metralhadora contínua: liga e desliga .................. ✔
tempo LIGADO: míssil 250 ms, travamento 150 ms,
  pulso da metralhadora 42 ms, do buffet 32 ms ......... ✔ acima dos ~20 ms do LRA
```

---

## O iPhone mudo, parte 2: a chavinha de silencioso

> *"O jogo sendo visto e controlado pelo iPhone não tem som."*

Duas semanas depois do monitor mudo, o mesmo sintoma noutro lugar — e a
diferença entre os dois casos é que dá a resposta.

No monitor, com o iPhone só de controle, **o som saiu**. No iPhone rodando o
jogo, não sai. O contexto de áudio acorda (o aviso que eu pus no rodapé nem
aparece), o motor monta, o `running` está lá. O que o monitor não tem e o
iPhone tem é a **chavinha de silencioso na lateral**.

### Categoria de áudio

O Safari classifica o som de uma página em **categorias**. A padrão é
`ambient` — som de enfeite, do tipo que ninguém quer ouvir tocar sozinho no
meio de uma reunião — e som `ambient` **obedece a chavinha**. Vídeo e música
ficam em `playback`, que a ignora: é por isso que um vídeo toca com o telefone
no mudo e o nosso motor não tocava.

Faltava o jogo **dizer em que categoria ele está**. Uma linha:

```js
navigator.audioSession.type = 'playback';
```

E tem de ser dita antes de o contexto começar a tocar, dentro do mesmo toque —
por isso mora no `ligaAudio()`, o único lugar por onde todo mundo passa.

### O mesmo defeito estava nos quatro jogos

No `aviao.html` (e portanto no `tv.html` e no `aviao-tv.html`, que herdam o
núcleo dele) o áudio é **preguiçoso**: só nasce quando alguma coisa toca. E a
primeira coisa a tocar pode acontecer longe do dedo da pessoa — aí o navegador
segura o contexto **e** a categoria chega tarde. Ganharam o mesmo destravar por
gesto que o 3D já tinha, e a mesma declaração de categoria.

```
aviao3d.html  declarou ["playback","CONTEXTO","playback"]  ✔ antes do contexto tocar
aviao.html    declarou ["playback","CONTEXTO","playback"]  ✔
tv.html       declarou ["playback","CONTEXTO","playback"]  ✔
```

### O que o jogo não tem como saber

A chavinha **não dá para ler pelo navegador**: com ela ligada o contexto fica
`running` do mesmo jeito e o som some no caminho, sem deixar rastro. Então o
`🔇 ligar o som` do rodapé, que resolve o caso do contexto preso, é cego para
este — e ficar mudo sem explicação nenhuma é o pior que pode acontecer.

O jogo não pode avisar sozinho, mas pode **dizer onde olhar**, e só no aparelho
onde essa chavinha existe:

> iPhone: se ficar mudo, confira a **chavinha de silencioso** na lateral.

**O que eu não consigo garantir daqui:** não há chavinha de silencioso neste
contêiner. O que ficou provado é que os quatro jogos declaram `playback`, e
declaram antes do contexto tocar. Se a `navigator.audioSession` não existir no
iOS desse aparelho, a linha sai de graça e sobra a dica — que aí passa a ser a
correção inteira.

---

## "Os celulares não conseguem entrar na mesma sala"

> *"Ao entrar numa sala, tem que ficar o código disponível na tela, ou então o
> QR, para entrar no jogo como copiloto ou fazer a batalha aérea."*

Primeiro medi, porque "não consegue entrar" pode ser rede ou pode ser tela.
**Dois celulares de verdade**, os dois rodando o jogo, num teste novo:

```
celular A: sala MGKR | celular B: sala RQEW
os dois abriram sala ....................................... ✔
B entrou na sala de A: A vê 2, B vê 2 ...................... ✔
a caixa "entrar na batalha": topo em y=647, tela de 390 ..... ✘ o dedo NÃO alcança
```

A rede estava boa. O que não dava era **chegar ao botão**. Todos os meus testes
anteriores usaram janelas de computador, de 560 a 620 de altura; um celular
deitado tem 390, e nessa altura a capa vira uma coluna comprida com a caixa da
batalha **257 pixels abaixo da borda de baixo**. Dava para rolar até lá, mas
quem rola procurando o botão de jogar passa direto — e depois, voando, não
havia lugar nenhum onde reler o código.

### Um painel, e o código sempre na tela

A resposta é a que veio no pedido. Um painel só, que abre da capa **e de dentro
do voo**, com tudo o que diz respeito a estar acompanhado:

- o **código desta tela** e o **QR** dela — quem entrar por aí comanda este avião;
- o **campo para entrar no céu de outra pessoa**.

E o botão que abre esse painel tem **o código escrito nele** — `SALA CUNN`, no
alto da tela, o voo inteiro. A pergunta *"qual é o código?"* passa a ter resposta
sem ninguém tocar em nada.

Na capa de um celular deitado, as duas caixas compridas somem e no lugar entra
um botão que abre o mesmo painel. A capa volta ao que ela precisa mostrar: como
**começar a voar**. Num monitor nada muda — lá o QR grande à vista é justamente
como se traz um celular para dentro.

```
na capa do celular: botão "Sala EWYR · QR e batalha aérea" em y=207 de 390  ✔
o painel: código, QR desenhado, campo e botão ao alcance do dedo ......... ✔
B entrou na sala de A pelo painel: os dois veem 2 ........................ ✔
voando: o botão do alto diz "SALA EWYR", dentro da tela .................. ✔
e abre o painel de dentro do voo ......................................... ✔
```

### Três defeitos que apareceram no caminho

**A regra que não fazia nada.** A media query que esconde as caixas compridas
começou lá em cima da folha de estilo — e `#sala, #batalha{display:flex}` vem
depois, com a mesma especificidade. Entre iguais ganha a última, então a regra
nova era letra morta. Foi para o fim da folha.

**O QR gigante no canto, de novo.** A tela do jogo é um `canvas` preso na janela
inteira, e a regra que faz isso pega **qualquer** canvas da página. O QR novo
saltou para o canto do tamanho de um cartaz. Já é a segunda vez: cada QR precisa
ser desamarrado à mão, e agora a lista está comentada no lugar.

**O `.op` que só existia dentro de uma caixa.** `Entrar na batalha` é `.op`, mas
o estilo estava escrito como `#ondeComeca .op` — então aquele botão sempre foi
um botão branco de navegador, na capa e no painel. Estilo é do botão, não do
lugar onde ele está: `.op` virou geral, e o `#ondeComeca` só ajusta o que é dele.

### Ainda em aberto

Este teste roda os dois celulares **dentro da mesma máquina**. Dois aparelhos de
verdade em redes diferentes — um no wi-fi, outro no 4G — precisam de um servidor
TURN para atravessar o NAT, e o PeerJS público não dá isso. Se continuar sem
entrar com os dois longe um do outro, é esse o próximo lugar para olhar, e não
a tela.

---

## O mapinha redondo

> *"Tem que ter um mapinha redondo no canto."*

O jogo tinha bússola (para onde o nariz aponta) e seta de alvo (onde está o
próximo), e nenhuma resposta para a pergunta que vem antes das duas: **onde eu
estou**. Voando sobre uma cidade que se repete, sem isso a pessoa fica girando
à toa procurando a pista.

Três decisões mandaram no desenho:

1. **Nariz para cima, não norte para cima.** Mapa de papel aponta o norte; mapa
   de avião aponta para onde se está indo, senão é preciso girar a cabeça para
   traduzir. O norte virou um risquinho que passeia pela borda — é ele que
   gira, não o mundo.
2. **Só o que se procura:** a pista, os adversários e os alvos que faltam. Os
   tambores e os pombos ficaram de fora; são dezenas, e um radar cheio de
   pontinhos não responde pergunta nenhuma.
3. **Quem está fora do alcance fica na borda**, menorzinho. Sumir com o
   adversário porque ele está a 30 km é esconder justamente a informação de que
   ele existe e de que lado ele vem.

### A geometria, lida dos pixels

Sinal trocado é o erro que mais me pegou neste projeto, então o teste não
confere a conta: ele **põe um avião no mundo, manda desenhar e procura o ponto
vermelho** dentro do disco.

```
o outro avião à frente (+z)  aparece EM CIMA   ✔
o outro avião atrás  (-z)    aparece EMBAIXO   ✔
o outro avião à direita      aparece DIREITA   ✔
o outro avião à esquerda     aparece ESQUERDA  ✔
virei o nariz 90° para a DIREITA:
   quem estava à frente foi para a ESQUERDA    ✔ o mundo gira, o avião não
a 50.000 (o alcance é 26.000): fica na borda   ✔
alvo destruído: some do mapa                   ✔
```

O último saiu de uma leitura do código, não do teste: eu tinha escrito
`if (a.destruido) continue` e o campo chama-se `vivo`. `destruido` é sempre
`undefined`, então o radar mostrava alvo já derrubado como se ainda faltasse.

### Onde o disco cabe: três palpites e uma busca

O pedido dizia "no canto". O canto é o único lugar onde ele **não** cabe.

| tentativa | o que aconteceu |
|---|---|
| "14 do canto, 62 do rodapé" | caiu dentro da caixa da velocidade |
| "olhe os painéis colados na borda esquerda" | a caixa da velocidade começa em 135, não é colada — atropelado de novo |
| "olhe quem cruza a faixa da esquerda" | certo no computador; no celular o disco foi parar **debaixo** do seletor de armas — desenhado e invisível |
| encolher no canto até caber | o canto é onde os painéis moram: encolhia até 40 sem nunca sair de dentro deles |
| deslizar pela borda, de baixo para cima | certo no computador; no celular as tiras do acelerador e do nitro ocupam os dois lados **de cima a baixo** |

O erro foi sempre o mesmo: **eu decidindo de antemão onde há espaço**, numa
tela cujo conteúdo muda com o modo (dedo ou sensor), com o tamanho e com o que
o avião está fazendo. A tela sabe melhor do que eu.

Então o disco procura. Do maior raio para o menor, de fora para dentro, de
baixo para cima, ele para no primeiro lugar em que não encosta em nada. Painel
nenhum precisa ser nomeado, e o que aparecer amanhã já entra na conta. A busca
não roda a cada quadro — a arrumação só muda quando a janela muda ou quando um
botão aparece, então meio segundo de memória basta.

```
iPhone deitado  844×390 -> disco de 46 em (235, 244)  ✔ sem encostar em nada
Android         915×412 -> 47 em (138, 265)           ✔
iPhone pequeno  667×375 -> 46 em (235, 229)           ✔
computador     1280×800 -> 92 em (104, 568)           ✔ canto de baixo, como se espera
quadros por segundo: 6,6 -> 5,6 (o mesmo de antes do radar)
```

### E um encontrão que já estava lá

O botão `SALA` nasceu em `top:14; left:50%` — exatamente onde mora a caixa do
combustível. As duas se sobrepunham, com "SALA CUNN" escrito por cima do 100%.
Desceu para baixo dela.

---

## Altímetro na cabine, e nascer espalhado

### O número que faltava

> *"O HUD do modo cabine também tem que ter altitude, em verde."*

Faltava mesmo — e não só na cabine: **o jogo inteiro não tinha altímetro**. Dava
para saber a velocidade, o combustível, a fuselagem, a distância voada e a
potência, e não dava para saber a que altura se está, que é o número que decide
se dá para puxar ou não.

Na cabine ele foi para a **direita**, do outro lado da mira: é ali que o olho de
quem voa procura altitude, e a esquerda já é do motor. Mesma tinta verde e mesmo
vidro escuro atrás — o verde do HUD some em cima da cidade branca, e as réguas
do motor já tinham aprendido isso.

Duas linhas, porque uma só não conta a história: os **metros** grandes, e embaixo
a **subida ou descida em metros por segundo**, com sinal. Altitude parada não diz
se o chão está chegando. Abaixo de 120 m o número fica vermelho.

A razão de subida sai direto de `eixoF.y * voo` — o quanto do vetor de voo aponta
para cima — e não de comparar alturas entre quadros, que com quadro irregular
pula de +300 para −900 e volta. Alisada, senão ninguém lê um algarismo que troca
sessenta vezes por segundo.

### A fila indiana

> *"O nascimento da batalha aérea tem que ser aleatório no mapa. Sempre nasce um
> atrás do outro no mesmo ponto."*

Era literal. O `reinicia()` punha todo mundo em `(0, 1500, 0)`, olhando para
`+z`. Dois aviões que entram na mesma batalha nascem colados, e quem morre e
volta reaparece exatamente onde o outro está esperando. Não é batalha, é fila.

Sozinho o ponto fixo não incomoda — e os testes contam com ele —, então o
sorteio vale **só quando há batalha**.

Sortear um ponto qualquer também não basta: o sorteio pode cair em cima de outro
avião, e aí o problema volta pior, porque agora é surpresa. Ele tenta até vinte
pontos e fica no primeiro que estiver a mais de 8.000 de todo mundo; se os vinte
falharem (céu cheio), fica com o mais longe que achou, que é sempre melhor que o
ponto fixo.

O raio do sorteio é o do mapinha: nascer **dentro do alcance do radar** é o que
faz a pessoa se achar, em vez de procurar a pista no vazio. O rumo também é
sorteado — nascer todo mundo olhando para o mesmo lado é meia fila.

E quem escolheu **começar na pista** não dá para espalhar pelo mapa. Aí o sorteio
é outro: ao longo da pista, cada um no seu pedaço, e um pouco ao lado do eixo —
ela tem 620 de meia-largura, cabem os dois.

```
sozinho, 5 vezes: sempre 0,0 ................................ ✔ como antes
em batalha, 40 vezes: 40 pontos diferentes, 5.427 a 25.807 ... ✔ nunca repete
   alturas de 1.572 a 4.213 ................................. ✔
   rumos de -179° a 168°, eixos normalizados ................ ✔ cada um para um lado
com alguém no céu, 30 vezes: nasceu colado nele 0 vezes ...... ✔
na pista, em batalha: z de -7.630 a -3.258, todos no asfalto . ✔
cabine a 2.000 m: o altímetro verde aparece .................. ✔
a 60 m do chão: fica vermelho ................................ ✔
```

---

## A altura virou fita, e a sala saiu do meio

> *"O HUD de altura pode ser no mesmo estilo do HUD de lateralidade, só que
> vertical. O nome da sala pode ficar num canto e não no meio da tela."*

### Caixa não é HUD

O que eu tinha feito era uma **caixa com o número dentro**, e caixa de número
diz onde se está e não diz para onde se vai. A fita diz as duas coisas com o
mesmo traço: os riscos correm para baixo quando se sobe, e a **velocidade com
que correm é a razão de subida** — dá para ler sem ler o número.

É a bússola virada em pé, de propósito: mesma caixa escura de cantos redondos,
mesmo verde, mesmos riscos curtos e compridos, mesmo ponteiro branco. **Duas
fitas com o mesmo desenho leem-se sem aprender a segunda.**

O teto do jogo é 5.200 e o chão −700: a faixa inteira em que se voa tem menos de
300 metros. Então a janela é de 60 para cada lado, risco a cada 10 e número a
cada 50 — mais fino vira grade, mais grosso não mostra nada mexendo. O chão
ganhou um traço alaranjado grosso: é o único risco da fita que se deve evitar.

### O que o teste mediu

Não a conta — os **pixels**, procurando o risco do chão dentro da fita:

```
a 10 m o risco do chão está a 20 px do ponteiro; a 40 m, a 87  ✔ subindo, o chão desce
30 m valeram 67 px (a escala manda 67) ........................ ✔ escala certa
a 200 m: o chão sai de cena em vez de grudar na borda ......... ✔
o número do ponteiro fica vermelho só perto do chão ........... ✔
a razão de subida aparece nos dois sentidos ................... ✔
a fita também existe na vista de fora ......................... ✔
```

### O meio da tela é por onde se olha

O botão da sala já morou em cima da caixa do combustível e depois logo abaixo
dela — no meio. **Meio de tela é por onde se olha para voar, e nada que não seja
de voar deveria morar ali.** Foi para o canto de baixo à esquerda, na fileira dos
outros botõezinhos (olho, qualidade), que é onde moram os comandos que não são
do voo.

### O terceiro desenho que não é elemento

O mapinha desvia de tudo sozinho — mas só sabe de **elementos do documento**, e
a fita da altura e as réguas do motor da cabine são desenhadas na lona. Resultado:
o disco plantou-se em cima das réguas.

As duas ganharam uma função que **diz onde elas estão** (`fitaAlturaOnde`,
`reguasOnde`), e o mapinha lê as três listas: os elementos, a fita e as réguas.
O mesmo padrão do radar — quem sabe onde está é quem desenha —, agora valendo
para o que não tem caixa no documento. E trocar de vista esquece a memória de
meio segundo, senão o disco fica um instante no lugar da vista anterior.

```
na cabine, nada encosta em nada: nenhuma sobreposição  ✔
```

(Esse teste pegou de brinde a fita encostando na caixa da FUSELAGEM: ela desceu
para o meio exato da tela e encolheu um fio — perde seis metros de janela e
ganha não brigar com um painel que está ali desde sempre.)

---

## O código que não contava

Terceiro relato seguido sobre a mesma coisa: **"não tremeu nada"** — e desta vez
nem o botão de teste, que é um dedo direto no vidro. Isso mata as duas
explicações que eu já tinha consertado: não é padrão fraco demais (o do teste é
longo de propósito) e não é recado que não chega (o botão fala com o próprio
aparelho). Sobra: a chamada sai e nada acontece.

E eu não tinha como saber qual dos casos era, porque este código era **surdo**:

```js
V.bate = p => { try{ navigator.vibrate(p); }catch(e){} };
```

`navigator.vibrate` devolve `false` quando o navegador **recusa** o pedido, e
pode lançar. Aquele `try/catch` jogava fora as duas respostas: recusado, aceito
e explodido ficavam exatamente iguais vistos daqui. Três rodadas de conserto sem
uma única evidência — porque eu tinha escrito um código que não conta o que
aconteceu.

Agora ele conta, e o botão de teste escreve na tela:

| o que o aparelho fez | o que aparece |
|---|---|
| aceitou | `caminho vibrador (Android) — chamei e o navegador aceitou` |
| recusou | `… — chamei e o navegador RECUSOU (devolveu false)` |
| lançou erro | `… — a chamada deu erro: <motivo>` |
| não tem `vibrate` | `caminho háptico do iPhone — agendei 3 tique(s) no interruptor` |

Os quatro casos são provados com o `navigator.vibrate` trocado por um de
mentira que aceita, recusa e explode, e com ele apagado para virar iPhone.

Um detalhe que o teste pegou: no caminho do iPhone o relato saía *"ainda não
tentei"*, porque os tiques são **agendados** e quem pergunta logo depois do
toque ainda não viu nenhum acontecer. O aviso passou a ser dito na hora de
agendar, não na hora de tocar.

**O que isto ainda não resolve:** se o relato vier `chamei e o navegador
aceitou` e mesmo assim não se sentir nada, o problema está fora do jogo — a
vibração do sistema desligada, o aparelho no silencioso, ou o "vibrar ao tocar"
desligado nas configurações. E se vier o caminho do iPhone: o Safari **nunca**
implementou a API de vibração, então lá o tremor depende inteiro do truque do
interruptor háptico, que é hack e pode simplesmente não funcionar naquele iOS.
Nesse caso a resposta honesta é que página nenhuma vibra num iPhone, e o que
resta é o som e a sacudida da imagem.

### E se nem no Android vibra

No Android o `navigator.vibrate` é caminho direto, sem truque. Se lá também não
vibra, ou o jogo não está chamando — e agora ele conta que chama — ou **o
navegador não é o que eu estou supondo**.

A hipótese que eu não tinha considerado, e que é das mais prováveis num jogo que
se manda por link: **navegador embutido de app**. Quem abre o endereço dentro do
WhatsApp, do Instagram ou do Facebook não cai no Chrome — cai numa **WebView**
hospedada pelo app. E WebView do Android só vibra se o **app hospedeiro** tiver
pedido a permissão de vibração ao sistema; os de mensagem não pedem.

O sintoma bate exatamente: `navigator.vibrate` existe, aceita o pedido, devolve
`true`, e não acontece nada. Um relato de "não tremeu" com o código antigo,
surdo, era indistinguível de qualquer outra causa.

Dá para reconhecer pela assinatura do navegador — a WebView do Android põe um
` wv` na string, e os apps grandes põem a marca deles. O botão de teste agora
escreve três linhas na tela, e uma quarta quando é o caso:

```
navegador: Chrome · WebView (navegador DENTRO de um app) · Android
navigator.vibrate: existe · a página está em foco: sim
um buzz simples de 500 ms: aceita
⚠ navegador de dentro de app quase nunca vibra —
  abra o link no Chrome (menu ⋮ → "Abrir no Chrome")
```

O "buzz simples" é de propósito a chamada **mais burra que existe**: um número
só, direto, dentro do toque, sem padrão nenhum. Se nem essa funciona, nenhuma
funciona — e o que ela devolve separa *"o navegador recusou"* de *"aceitou e o
aparelho não fez"*, que são dois problemas com dois donos diferentes.

Seis navegadores são reconhecidos no teste: Chrome no Android, WebView do
WhatsApp, Instagram, Facebook, Samsung Internet e Safari no iPhone.

### O que o aparelho respondeu

```
navegador: Samsung Internet · Android
navigator.vibrate: existe · a página está em foco: sim
um buzz simples de 500 ms: aceita
```

**Aceita.** Não é WebView, não é falta de gesto do dedo, não é recusa do
navegador, não é o padrão curto demais. O navegador pegou o pedido e passou
adiante — daqui para baixo é o Android, e página nenhuma tem como ver ou mexer
nisso.

Ou seja: o caminho todo do jogo está certo, e estava certo antes dos dois
consertos de verdade que saíram desta caçada (a metade dos tremores que caía no
chão, e os pulsos curtos demais). Os dois eram reais; nenhum dos dois era ESTE.

Parar no dado seria deixar a pessoa com um relatório e sem resposta, então
quando o buzz vem `aceita` o diagnóstico passa a dizer **onde olhar**:

```
⚠ o navegador ACEITOU: daqui para baixo é o Android, o jogo não alcança.
Se não sentiu nada, veja Configurações → Sons e vibração →
Intensidade da vibração → "Interação por toque" (não pode estar no zero),
e confira se o aparelho não está no silencioso.
```

Num Samsung essa intensidade vem num controle **separado** do toque de chamada e
das notificações — dá para ter o telefone vibrando em chamada e mudo para
interação por toque, que é exatamente o estado em que uma página não vibra.

**A lição, que vale mais que o conserto:** eu passei três rodadas consertando
código a partir de *"não tremeu"*. Dois dos consertos eram necessários, mas
nenhum era a causa — e eu só descobri isso quando **fiz o código contar o que
acontecia**. Um `try/catch` mudo custou mais tempo que todos os defeitos que ele
escondia.

### A fita em pé estava mais gorda que a deitada

Duas fitas que deviam ser irmãs, e uma conta diferente em cada:

```js
bussola:      H*0.050      // altura da caixa
fitaAltura:   W*0.055      // largura da caixa
```

Numa tela de 1100×700 isso dá **35 contra 60** — 73% mais gorda. Copiar o número
de uma para a outra não resolveria: em outra tela elas voltariam a divergir,
porque uma seguia a altura e a outra a largura. Passou a existir uma
`grossuraFita()`, e as duas a chamam.

**Os números tiveram de sair de dentro.** Na bússola eles cabem porque lá a fita
é comprida no sentido em que o texto corre; na fita em pé o texto corre
atravessado, e "295" pede mais largura do que a fita inteira tem. Foram para
fora, à direita, entre a fita e a borda da tela. Ficam legíveis sem engordar a
fita, que era o pedido.

### Medir também tem armadilha

A primeira medição leu a bússola numa coluna só, **no meio** — e pegou o
ponteiro e o número do rumo junto, dando 45 onde a caixa tem 35. A segunda
mudou de coluna e caiu em cima de um "NE", que desce abaixo da caixa: 39 onde a
caixa tem 26.

Medir numa coluna só é loteria. O teste passou a varrer trinta colunas e ficar
com a **menor** — a que não pode ter nada além da caixa —, e a comparar também
as duas contas declaradas, não só os pixels:

```
1280x800  bússola 41 px · fita 41 px   ✔
1100x700  bússola 35 px · fita 35 px   ✔
 844x390  bússola 27 px · fita 27 px   ✔
 915x412  bússola 27 px · fita 27 px   ✔
 667x375  bússola 27 px · fita 27 px   ✔
```

---

## O que não dá para fazer por código

> *"Não consegue fazer por código? Não quero tirar o celular do silencioso. O
> jogo tem que conseguir extrair a vibração do celular."*

Não dá, e vale dizer com todas as letras em vez de tentar mais uma rodada.

O `navigator.vibrate` é um **pedido**. Quem decide se o motorzinho gira é o
Android, abaixo do navegador — e no modo silencioso a Samsung desliga a vibração
inteira, não só o som. Não existe API, permissão ou truque de página para furar
isso; nem aplicativo nativo faz sem sinalizadores de sistema aos quais uma
página não tem acesso. O diagnóstico do próprio aparelho já tinha dito o
essencial: **o navegador aceitou e nada aconteceu**. Daquele ponto para baixo o
jogo não alcança.

Mas o que se quer não é o motorzinho — é **sentir o tiro**. E para isso sobra um
caminho que nenhum modo de silêncio desliga: a **imagem**.

### O baque

Cada evento que treme passa a dar também um **coice na câmera** e um **clarão de
cor nas bordas**. As cores dizem o que aconteceu sem ninguém precisar aprender:

| evento | coice | borda |
|---|---|---|
| travar a mira | 0,07 | verde |
| soltar míssil | 0,17 | laranja |
| levar tiro | 0,52 | **vermelho** |
| bater | 0,85 | vermelho forte |
| metralhar | 0,13 por tiro | amarelo fraco, no ritmo |

Isto mora colado no `Controles.bate`, e não espalhado pelos lugares que atiram —
é a lição da tabela duplicada do tremor: **duas listas que precisam ser iguais um
dia ficam diferentes**. Aqui só existe uma, e o teste confere que todo padrão de
tremor tem o seu baque.

O coice da metralhadora era 0,05 — três centésimos de pixel, ou seja, nada.
Enquanto havia tremor no aparelho não fazia falta; num telefone no silencioso é
o único retorno de que a arma está cuspindo.

E o pedido de vibração **continua saindo**: quem puder vibrar, vibra. O baque é
soma, não troca.

### Duas coisas que o teste pegou

**A câmera que "andou 424".** A primeira medição do coice teleportou o avião e
mediu logo em seguida — e a câmera persegue o avião, então quase todo aquele
movimento era perseguição, não coice. Com a câmera assentada primeiro: 0,0 por
quadro em repouso contra 49 com o baque de bater.

**O clarão que não aparecia.** O degradê ia até 0,60 da maior dimensão da tela —
logo *adiante* dos cantos, então a parte forte caía fora do quadro. Fechado para
0,50 e com mais tinta. Medido no pixel: canto com alfa 184, meio com alfa 0 — a
borda acende e a mira continua limpa.

```
os 9 tremores têm baque na imagem: todos ........................ ✔
travar 0,07 · levar tiro 0,52 · bater 0,85, e a cor muda ........ ✔
um tiro de metralhadora: dá para ver a arma cuspindo ............ ✔
0,66 s depois o clarão apagou .................................. ✔
o pedido de vibração continua saindo ............................ ✔
```

---

## O dobro da velocidade, e o tremor mais forte

### "Aumenta a intensidade"

**Não existe intensidade.** A API de vibração da web só aceita **tempos** —
ligado, desligado, ligado — e nada de amplitude; o `navigator.vibrate` não tem
onde receber "mais forte". Quem manda na força é o sistema.

O que dá para mexer é o que o corpo **lê** como força, e são duas coisas:

1. **Pulso mais longo.** O vibrador é um solenoide: leva uns 20 ms para pegar
   embalo e só depois chega à amplitude cheia. Um pulso de 40 ms passa a vida
   inteira acelerando e morre antes de chegar lá; um de 130 ms fica a maior
   parte do tempo no máximo. O mesmo motor, o dobro de sensação.
2. **Menos buraco entre os pulsos.** Pausa longa deixa o solenoide parar por
   completo, e o pulso seguinte recomeça do zero.

| | antes | agora |
|---|---|---|
| míssil (tempo ligado) | 250 ms | **450 ms** |
| travar a mira | 150 ms | **310 ms** |
| metralhadora, por pulso | 42 ms | **80 ms** |
| metralhadora, tempo ligado | 58% | **82%** |

Na mão, 82% contra 58% é a diferença entre um cutucão ritmado e uma arma
tremendo de verdade.

### O dobro da velocidade

Dobrar velocidade não é mexer num número: é mexer em **doze**, e todos têm de
andar juntos. Dobrando só a velocidade de cruzeiro, o avião passaria a voar
sempre acima do teto do trem de pouso, o estol nunca mais aconteceria, a corrida
de decolagem acabaria em meio segundo e todo pouso estouraria o limite de toque.
O jogo inteiro se desmancharia por um número.

Então existe **um fator só** — `VEL = 2` — e a família toda o multiplica: as
quatro velocidades de voo, os três estóis, os três tetos de flape, o teto do
trem, os limites de toque, a aceleração e o freio no chão. Trocar `VEL` volta o
jogo à velocidade antiga sem procurar nada.

O que **não** multiplica, de propósito:

- **as taxas de rolagem, arfagem e leme** — são graus por segundo. Mantê-las
  iguais com o dobro de velocidade **alarga a curva**, e curva larga em
  velocidade alta é exatamente a sensação de avião rápido;
- **o gasto de combustível** — assim um tanque dura os mesmos minutos e rende o
  dobro de mapa;
- **o mundo**, que continua do mesmo tamanho. É por isso que dobra a emoção: a
  cidade passa duas vezes mais depressa.

A física roda em **passo fixo**, então nem numa máquina lenta o avião pula por
cima de um prédio: a 6.000 são 100 por passo, contra prédios e aviões de
centenas de raio.

```
corrida até a rotação: 6,0 s, 3.881 de pista (era 1.940), precisa de 1.274  ✔
decolou usando 4.777 de 22.000 de pista ................................... ✔
subiu para 5.892, voo 4.400 ............................................... ✔
pousou na pista, freando em 2,5 s e 2.036 de pista ........................ ✔
os quatro jeitos errados de pousar continuam batendo ...................... ✔
```

### Os testes tinham a escala velha escrita na mão

Dois quebraram, e nenhum era defeito do jogo:

**"descendo como pedra" passou a pousar.** O teste fixava `voo = 1200` e um
ângulo — números da escala antiga. Com o jogo dobrado, aquela mesma descida
virou uma aproximação mansa. Agora ele pede o que quer dizer: *descer 1,4 vez
mais depressa do que o trem aguenta*, e calcula o ângulo a partir disso.

**O estresse aerodinâmico deu 1,00 em tudo.** A sonda ia de 1200 a 640, que
antes era "de bem acima do estol até encostar nele" — e virou uma lista inteira
**abaixo** do novo estol de 1280. Agora ela é escrita em múltiplos do estol:
1,9× · 1,4× · 1,25× … 1,0×, e acompanha qualquer escala.

É o mesmo erro nas duas: **o teste guardava o número em vez da intenção.**
Enquanto a escala não muda, os dois jeitos parecem iguais.

---

## A física básica da aviação

> *"O estol tem que acontecer quando abaixa muito a potência, e tem que tender o
> avião a baixar. E ao subir muito tem que estolar também. São a física básica
> da aviação."*

Faltava metade dela. Até aqui a velocidade dependia **só da manete**: o avião
subia a 80° sem perder um nó, e o estol só chegava a quem fechasse a potência.
Faltava o principal — **quem sobe troca velocidade por altura, e quem desce
troca altura por velocidade**.

É um termo só, e resolve as três coisas de uma vez:

```js
voo -= SUBIDA_CUSTO * eixoF.y * dt;   // eixoF.y é o seno do ângulo de subida
```

- fechar a manete derruba a velocidade, e o estol vem;
- **subir demais derruba a velocidade também**, e o estol vem sem ninguém ter
  tocado na manete;
- e baixar o nariz **devolve** velocidade — que é como se sai de um estol, a
  única saída que existe num avião de verdade.

### O número saiu da escada, não do chute

O primeiro valor que pus, 8000, fazia até a vertical com manete cheia estolar —
e de quebra **matava a decolagem**: com o trem fora o motor só entrega 2.800, e
a subida de 35° que a rotação produz sozinha custava mais do que isso. Medido
quadro a quadro: o avião saía da pista, estolava e voltava a assentar nela.

Com 6.800:

```
 0° cruzeiro -> 3392  aguenta
30° cruzeiro -> 2032  aguenta
45° cruzeiro -> 1469  aguenta, no limite (estresse 0,33)
55° cruzeiro -> 1164  ESTOLA
60° cruzeiro -> 1036  ESTOLA
45° cheia    -> 2477  aguenta
80° cheia    -> 1721  aguenta
90° cheia    -> 1680  aguenta
```

Com manete cheia dá para subir reto, e isto **não é falha**: caça com empuxo
maior que o peso sobe na vertical mesmo. O que mata é puxar **sem potência**,
que é o erro de verdade.

### "Tender a baixar"

Antes do estol declarado existe a faixa em que a asa ainda sustenta mas já está
no limite — e ali um avião de verdade **afunda**, com o nariz apontando para
cima. Sem isso o voo lento era mágico: dava para ficar pendurado no ar até o
estol estourar de repente. Agora a altura começa a cair sozinha antes de
qualquer alarme: **583 num segundo**, no meio da faixa.

### O estol tem de comprometer

Com o mergulho devolvendo velocidade, o estol virou um chacoalho: o nariz caía
um grau, a velocidade voltava um fio, a asa "sustentava" outra vez, e recomeçava.

Duas correções, as duas de manual:

**Histerese.** Asa estolada não volta a sustentar no instante em que recupera um
nó — o fluxo tem de colar de novo, e isso pede margem. Entra no estol em
`velMin()`, só sai em **1,15 vez** isso.

**O profundor perde autoridade.** O endireitamento de arfagem ("mão solta, o
nariz procura o horizonte") estava brigando com o estol e ganhando. Numa asa
estolada a cauda também perde ar — é por isso que num estol de verdade o manche
fica mole. Calado durante o estol, o nariz cai e **fica** caído até a velocidade
voltar.

### O fugóide, e três testes que mediam o instante errado

Com o mergulho devolvendo velocidade, o avião solto passou a **porpotear**: cai,
recupera, sobe, cai de novo. Isso é o **fugóide**, e todo avião solto faz.

E derrubou três testes que não tinham nada de errado com o jogo — todos mediam
**um instante de uma oscilação**:

| teste | media | passou a medir |
|---|---|---|
| estol sem flape | a arfagem aos 2,5 s exatos | estolou em algum momento? perdeu altura? |
| as seis atitudes | o nariz no último quadro | o nariz **mais baixo** da passagem |
| a escada de estresse | velocidades fixas de 1200 a 640 | múltiplos do estol |

O padrão é sempre o mesmo, e já apareceu três vezes neste arquivo: **o teste
guardava o número em vez da intenção.** Enquanto nada muda, os dois jeitos
parecem iguais.

```
manete fechada, mão solta, sem flape: estolou, nariz a -20°, perdeu 2.935  ✔
a mesma com flape 2: não estolou, nariz a 0°                               ✔
as seis atitudes, inclusive de cabeça para baixo: todas caem de bico       ✔
mergulhando 40°: 5.140 contra 3.392 nivelado                               ✔
```

---

## O mundo ganhou vida (e ficou maior)

Cinco pedidos de uma vez. O primeiro — *"o nariz para cima perde velocidade, para
baixo ganha"* — já estava pronto desde a rodada anterior; os outros quatro são
desta.

### Avião não fica parado no ar

> *"Não quero mais avião parado no mapa; se for parado que seja um helicóptero,
> os aviões de pontuação devem estar em movimento."*

Os aviões tinham uma `deriva` de ±300 e ficavam balançando em volta do mesmo
ponto: de longe, parados. **Avião parado no ar é a única coisa que um avião não
faz.**

Agora quem é avião **cruza o mapa** num rumo, com uma curva mansa, e dá a volta
pelo outro lado quando chega ao fim — sem isso, em dois minutos o céu fica vazio
de um lado e entupido do outro. E quem tinha de ficar parado virou
**helicóptero**, que é o que pode.

O helicóptero não é enfeite: por estar parado é o alvo fácil, e vale **120**
contra os **200** do avião, que obriga a mirar adiante. Construído com as mesmas
peças do dragão para não destoar, e fundido por cor como todo o resto — um
figurante não pode custar mais ordens de desenho que o avião do jogador.

### A nuclear virou míssil ar-terra

> *"A bomba nuclear não tem muita graça, nem vejo onde ela cai."*

Era literal: uma cápsula largada da barriga, que caía por parábola **atrás** do
avião enquanto ele seguia em frente. Quando ela chegava ao chão, o jogador
estava a quilômetros dali olhando para a frente. A arma mais destrutiva do jogo
era a única que ninguém via funcionar.

Agora ela é **lançada, não largada**: sai na direção da mira a quase o dobro da
velocidade do avião, e estoura no chão **ou no primeiro prédio que encontrar** —
antes ela atravessava a cidade inteira e só acordava no asfalto.

E o chão diz onde ela vai cair. Um alvo desenhado no ponto de impacto, com a
distância escrita e um anel que aperta conforme ela chega; quando o anel fecha, é
agora. Se a pessoa disparar apontando para **cima**, não há ponto de impacto — e
o jogo diz isso (`NUCLEAR — APONTE PARA BAIXO`) em vez de inventar uma marca.

O que ela ganhou em graça, cobra em risco: ir ver de perto é entrar no raio de
9.000 dela, e o HUD avisa com um **SAIA DAQUI** por cima da marca.

### O mapa dobrou e não ficou mais caro

O motivo é o avião ter dobrado de velocidade: o mundo passou a ser atravessado na
metade do tempo. Mas ampliar sem pensar **quadruplica a conta** — 53 aviões
viram 212, 344 tambores viram 1.376.

O princípio que resolve é o mesmo que motivou a ampliação: **se o avião voa o
dobro, o espaçamento tem de dobrar junto.** O número de coisas no mundo não muda,
e o ritmo com que elas aparecem na janela também não — que é o que a pessoa
sente.

Os prédios são a exceção de propósito: eles são **uma** ordem de desenho
(`InstancedMesh`), então a cidade pode crescer de verdade.

```
                 antes            agora
mapa             120 mil de lado  240 mil de lado
prédios          774              3.255
aviões           53               54
ordens de desenho 1.400           1.483
```

### Bairros, de graça

O campo que decide onde há cidade já existia como um **sim/não**. Usando o
**valor** dele, o mesmo sorteio produz bairros: onde o campo é forte fica o
centro, com torres passando de 3.000, estreitas e escuras (vidro); na borda ficam
galpões baixos, largos e claros (reboco). Nenhuma peça nova, nenhuma ordem de
desenho a mais — só parar de jogar fora um número que já estava ali.

Num mundo que acabou de quadruplicar, isso é o que dá para saber onde se está.

### Um `undefined` que viraria NaN

Os obstáculos novos ganharam `vel` e `giro`. Um obstáculo montado sem eles — e
existem, em teste e em recado de rede antigo — fazia `Math.sin(rumo)*undefined`
virar **NaN**, e dali em diante a posição inteira do bicho era NaN. É a mesma
armadilha do `y` que faltava nos alvos de chão e que já tinha estourado a
perseguição do míssil: **um campo ausente não avisa, só contamina.** Os dois
ganharam `|| 0`.

---

## O degrau entre a pista e o céu

> *"Parece que estou grudado no chão, e quando decola do nada parece um foguete.
> É muito discrepante. Suavizar a decolagem e a aterrissagem."*

### A teoria errada, e por que ela quebrou o jogo

Minha primeira leitura foi a aceleração, e havia mesmo um degrau feio:

```
no chão   +215 por segundo
no ar     +3.775 por segundo, no quadro seguinte
```

Dezessete vezes, no exato instante em que as rodas deixam o asfalto. Pus um
**teto** na aceleração do ar — e **quebrei o jogo**: a escada de subida inteira
passou a estolar, inclusive 30° com potência de cruzeiro.

A razão é bonita e eu não a tinha visto. A perseguição `(alvo − voo)*2,5` não é
só pressa: ela é o que **equilibra** o custo da subida. Quanto mais a subida
drena velocidade, mais forte ela puxa de volta, e o avião assenta onde as duas se
igualam — é dela que sai a escada de ângulos. Um teto fixo corta esse braço, e o
avião não tem mais como pagar subida nenhuma.

### O foguete era o manche

Medido no traço quadro a quadro: a puxada de rotação, 0,6 s de manche, levava o
nariz a **46°** — e o avião, recém-saído do chão a 1.300, apontava para o céu e
subia 740 por segundo. *Isso* é o foguete.

A causa é o comando ter a mesma força a qualquer velocidade. **Num avião não
tem:** o profundor e os ailerons trabalham com o ar que passa por eles, e a força
cresce com o **quadrado** da velocidade. Devagar o manche é mole, rápido é firme.
É por isso que ninguém arranca um avião do chão em 46°.

Com a autoridade amarrada à velocidade, três coisas se resolveram de uma vez e
sem nenhum caso especial:

- a **decolagem** fica mansa (rotação a 14° em vez de 46°);
- o **pouso lento** fica delicado;
- o **voo perto do estol** fica mole, que é exatamente como se sente um avião no
  limite.

A corrida no chão também ficou mais forte — 6 s viraram 3,6 —, que era a metade
*"grudado"* da queixa.

```
rodou 3,6 s até 1.305 (rotação em 1.274)
depois da rotação: 261 -> 489 -> 769 -> 1.083 de altura   (subida firme)
antes:             329 -> 737 -> 1.073                    (salto)
a cambalhota ainda fecha, em 6,1 s em vez de 5
```

### E a asa que nivelava num quadro

No toque, `eixoC = (0,1,0)` era posto de uma vez: quem pousasse com 10° de banco
via o avião **estalar** para o nivelado entre um quadro e o outro. Agora o banco
do toque escorre para zero em meio segundo — é o amortecedor comprimindo e a asa
assentando.

---

## O nitro, e a sensação de velocidade

> *"Caprichar no efeito da turbina, que era só um cone. Ligar o nitro no chão
> também tem que dar sensação de velocidade."*

Três coisas, e as três somam:

**A chama em camadas.** Cone sozinho não parece fogo — fogo tem **miolo**. Um
núcleo branco curto e quase opaco colado no bocal, um envelope longo e
transparente por fora somando luz, e os **anéis de choque** (aqueles losangos
espaçados dentro do jato de um caça em pós-combustão). São a assinatura visual do
troço, quase ninguém desenha porque não sabe que existem, e são o detalhe que faz
alguém dizer *"esse fogo está certo"*. Tudo treme a cada quadro: chama parada é
plástico.

**As riscas.** O que faz uma tela parecer rápida não é o número na caixa da
velocidade: é ter **coisas passando perto**. A cidade passa longe e no céu não há
nada. Setenta riscos finos vivem num tubo em volta do avião, correm para trás na
velocidade do voo e reaparecem na frente — e como andam **com o avião**, o truque
vale igual no chão, que era o pedido. É **uma** ordem de desenho: um
`LineSegments` com as pontas reescritas a cada quadro.

**O soco de campo de visão.** É o truque mais forte que existe, e custa uma
linha: no nitro a lente abre de 58° para 74°. O mundo nas bordas passa a correr
muito mais depressa que no meio, que é o que o olho lê como *"estou
acelerando"*. Vai e volta macio — abrir de repente enjoa.

```
nitro: campo de visão 58° -> 74°, riscas acesas a 0,55    ✔
solto: volta a 58°, riscas somem                          ✔
nitro na PISTA: noChao=true e as riscas acendem igual     ✔
```

---

## Duas coisas do HUD

**A marca dos outros aviões era um grandão.** A caixa crescia até 70 px de
meio-lado — 140 de lado, num HUD onde nada passa de 30. De perto ela tomava o
meio da tela e tapava justamente o avião que se está tentando acertar.

O erro foi querer que a caixa **envolvesse** o alvo. Mira de caça não faz isso:
ela aponta, e quem enxerga o avião é o olho. Virou uma marca pequena, de tamanho
quase fixo, com **quatro cantos** em vez de um retângulo fechado.

**A metralhadora não dizia onde atira.** A mira do meio da tela diz para onde o
*nariz* aponta; os tiros saem por ali mas morrem a uma distância certa. Sem ver o
alcance, atira-se longe demais e não se entende por que não acerta.

Agora o HUD desenha o **caminho real da bala** — a mesma direção, velocidade e
tempo de vida que o `dispara()` usa —, com traços nos quartos do alcance e um
círculo onde a bala acaba. Alvo além do círculo é alvo que não vai ser atingido,
e isso passa a ser visto em vez de adivinhado.

*(Este teste pegou de brinde o `baque`: a prova de "o clarão acende a borda e
deixa o meio limpo" passou a medir a mira nova, que mora no meio. Ela passou a
medir com o míssil selecionado.)*

---

## O tiro que não ia onde se mirava

> *"A mira nova da metralhadora mora justamente no meio, mas ela tem que projetar
> onde vai pegar na frente. O tiro não vai onde se dispara, só se estiver muito
> perto — e fazendo curva os tiros ainda se desviam no ar."*

A queixa estava certa e tinha **duas** causas. Uma eu adivinhei errado; a outra
era o defeito de verdade.

### O que eu achei que era (e a medição desmentiu)

Raciocínio: numa curva o nariz varre enquanto a bala viaja, então a linha da
mira tinha que **encurvar para trás** de `ω·t` — a *mira giroscópica* dos caças
de verdade. Implementei, ficou bonito, e fui medir. O teste solta **uma** bala e
vai ver onde ela parou:

```
em linha reta : 399 da mira reta · 399 da giroscópica   (alcance 14247)
em curva leve : 249 da mira reta · 1950 da giroscópica  (alcance  9803)
em curva forte: 496 da mira reta · 5946 da giroscópica  (alcance 14990)
```

A giroscópica errava **doze vezes mais** na curva forte. O raciocínio tinha um
buraco: a bala que sai **agora** viaja reta a partir de agora, e o nariz
continuar girando depois não a entorta. A curva mostrava onde estão as balas do
**passado** — que é exatamente o rastro torto que se enxerga, e por isso parecia
certa — mas a mira precisa dizer para onde vai a **próxima**. A linha é reta.

Fica registrado porque a lição é essa: a medição desmontou o raciocínio que a
produziu, e quem manda é a medição.

### O que era de verdade: os canos nunca se cruzavam

A bala nascia deslocada até 110 para o lado — os canos ficam nas asas, não no
nariz — e saía **paralela** ao nariz. Paralela nunca encontra: o rastro corria
eternamente ao lado da mira, e só de bem perto o erro ficava pequeno o bastante
para acertar. Era literalmente *"o tiro não vai onde se dispara, só se estiver
muito perto"*.

Caça de verdade resolve isso torcendo os canos um tantinho para dentro, para os
tiros se cruzarem numa distância escolhida: chama-se **harmonização**. Aqui cada
bala é apontada para o ponto da linha da mira a **62% do alcance**.

```
1) em linha reta : a bala terminou a 2 da linha da mira   ✔ (o raio de acerto é 320)
2) em curva leve : a bala terminou a 2 da linha da mira   ✔
3) em curva forte: a bala terminou a 2 da linha da mira   ✔
4) harmonização: nascem a até 106 do eixo e cruzam a mira a 0  ✔
```

---

## O alarme de atirar

> *"Tem que ter o mesmo alarme sonoro do travador de alvo do míssil quando a
> projeção dos disparos estiver correta — um aviso sonoro para poder atirar com
> a metralhadora."*

O buscador do míssil pergunta *"o alvo está no cone?"*. Da metralhadora a
pergunta é outra e é mais dura: **"se eu apertar agora, a bala encontra o
alvo?"** — o míssil corrige o caminho sozinho, a bala não corrige nada. Então a
conta é a de artilharia:

1. quanto tempo a bala leva para chegar — `t = distância / velocidade`;
2. onde o alvo vai estar depois desse tempo — a **dianteira**;
3. esse ponto adiantado está em cima da linha do cano, e dentro do alcance?

O passo 1 depende do passo 2 (alvo mais longe = mais tempo = alvo mais adiantado
ainda), então a conta roda **duas vezes**; converge rápido porque a bala é seis
vezes mais rápida que o avião.

A tolerância não foi escolhida a dedo: é o **raio de acerto de verdade**, o mesmo
que o `atingeAr()` usa — 320 da bala mais o raio do alvo —, com uma folga de 25%
para o alarme avisar um instante antes de o dedo precisar apertar. Quando toca, é
porque acerta.

E é o **mesmo tom** do míssil travado, que é o pedido: aquele que já era o som
favorito da casa. Some meio quarto de segundo depois de perder a solução — sem
essa folga, um alvo cruzando ligava e desligava o tom várias vezes por segundo.

Só entra o que a metralhadora **mata**: aviões, helicópteros, pombos e gente de
verdade na batalha. Alvo de chão não vale, porque a bala nem colide com ele — e
alarme que toca para o que não morre é mentira.

Na tela, a solução aparece onde ela está: um **losango** no ponto de encontro, o
traço fino que liga esse ponto ao alvo de agora — a dianteira que se está dando,
e ver o tamanho dela ensina a mirar na frente sem ninguém explicar — e a palavra
`ATIRE`. A linha da mira engrossa e clareia junto.

```
5) alvo parado bem na frente   : alarme toca    ✔
6) alvo parado 3000 fora       : alarme calado  ✔
7) alvo cruzando a 1700/s      : centrado agora, calado · 935 atrás, toca  ✔ dá dianteira
8) o tom contínuo é o do míssil                  ✔
9) trocando de arma, o tom cala                  ✔
```

Para a dianteira valer contra **gente de verdade**, o avião de rede ganhou
velocidade estimada: a rede só manda posição, 20 vezes por segundo, e a
velocidade sai da diferença entre dois pacotes (alisada, senão pacote atrasado
vira um pico absurdo). Sem isso o alarme só tocaria para alvo parado.

*(De brinde, o `fim()` passou a soltar as duas miras: ganhar a missão com um alvo
travado deixava o alarme tocando na tela de fim, para sempre — o laço morre ali,
e com ele os `passo()` que desligariam o tom sozinhos.)*

---

## Quatro coisas que só aparecem jogando

### 1. A mira era um risquinho parado no meio

> *"O HUD da metralhadora ficou muito curto ainda, e a extensão dele não
> acompanha o movimento do avião."*

A linha ia de **28% a 100%** do alcance — e esse trecho inteiro mora perto do
ponto de fuga, onde a perspectiva amontoa tudo. Dava trinta pixels parados no
centro da tela, por mais que o avião manobrasse.

Agora começa a **2,5%** do alcance — praticamente no cano — e vai até o fim. O
pedaço perto do avião é o que se espalha na tela: a linha nasce no nariz e sobe
até o horizonte, e como uma ponta está colada no avião e a outra está longe,
**virar varre a linha inteira pela tela**. Os passos dobram (2,5 · 6 · 13 · 26 ·
50 · 100%) porque na tela a distância anda com o inverso da profundidade — passos
que dobram no mundo dão pedaços parecidos no vidro. Os traços viraram
**perpendiculares à linha** em vez de horizontais: numa curva a linha deita, e
traço horizontal em linha deitada vira escada torta.

### 2. Na cabine só aparecia o ponto do meio

> *"Na visão de simulação parece que está no zero. Só mesmo o central aparece,
> não aparece o rastro."*

Também certo — e não tem conserto, porque é **geometria**: na cabine a câmera
fica dentro do avião, olhando ao longo do cano. Uma linha vista de ponta é um
ponto; os 700 metros de trajetória caem todos no mesmo pixel. É o mesmo motivo
pelo qual você não enxerga o comprimento de uma flecha que vem na sua direção.

Então na cabine a mira **troca de forma**, como troca num caça de verdade: em vez
do rastro, um **anel com o ponto no meio** — o *pipper*. O anel dá o tamanho
angular do alvo, o ponto diz por onde a bala passa, o número embaixo diz até onde
ela chega. Mesma informação, outro desenho, porque mudou o ponto de vista.

A troca é **medida, não chutada**: se a linha inteira couber em menos de 5% da
altura da tela, ela não é linha — é ponto, e vira anel. Isso pega a cabine e
pega também qualquer outro caso em que a câmera fique alinhada com o cano.

### 3. O teto ficava a 295 metros

> *"Aumenta o teto do jogo."*

`TETO` era 5.200 e o chão é -700: a coluna inteira de ar tinha **295 metros**, e
dava para encostar no limite numa subida só — o aviso "AR RAREFEITO" aparecia no
meio de manobra. Subiu para 11.000: **585 metros**, o dobro. As nuvens, que moram
entre 4.200 e 9.400, passaram a ficar *dentro* do espaço de voo em vez de serem
enfeite inalcançável.

E o tráfego subiu junto, senão a metade de cima do céu seria um deserto: aviões,
helicópteros e tambores sorteiam a altura com `random × random`, o que empurra o
sorteio para baixo — a maioria continua onde sempre esteve (o jogo baixo não
mudou) e uma minoria vive lá em cima, que é o que dá **motivo** para subir.

### 4. O estol chegava cedo demais, e chegava educado

> *"Quando o estol acontece o avião tem que descontrolar um pouco. O estol está
> acontecendo muito rápido na subida."*

**Cedo demais.** O custo de subir era 6.800, e a escada de ângulos com manete de
cruzeiro terminava em 55° — que é uma subida que se faz sem pensar. A varredura:

```
custo    45°    55°    65°    75°    90°
 5200   1921   1688   1507   1383   1312   <- sobe reto de cruzeiro: apaga a gravidade
 5800   1752   1492   1289    ✘      ✘     <- este
 6800   1469    ✘      ✘      ✘      ✘     <- o de antes
```

5.200 deixava subir na **vertical** com manete de cruzeiro, e isso tira a
gravidade do jogo — o pedido antigo era justamente pôr a gravidade dentro dele.
**5.800**: 45° tranquilo, 55° passa já reclamando (é o aviso), 70° para cima
mata. Manete cheia continua subindo reto, porque empuxo maior que peso sobe reto
mesmo.

**Educado demais.** O estol era simétrico: o nariz caía reto, e avião que cai
reto é avião que continua obedecendo. Asa de verdade não larga junto — uma
descola primeiro e o avião **rola para o lado dela**. É o *wing drop*, e é o que
transforma um estol num susto.

O lado é sorteado **uma vez, na entrada**, e vale enquanto durar aquele estol.
Sorteando a cada quadro daria chacoalho de brinquedo; sorteando uma vez o avião
cai sempre para o mesmo lado — e é isso que dá para corrigir com o manche. Junto
vai uma guinada no mesmo sentido, porque asa estolada arrasta mais.

**E o nivelador teve que calar a boca.** Na primeira medição o tombo empacava em
27° — *sempre* 27°, nas seis provas. Número redondo assim é sinal de duas forças
se anulando, nunca de física: era o nivelador automático puxando de volta com a
mesma força. E ele é que estava errado ali, porque representa a estabilidade da
asa, que é justamente o que se perde quando ela estola. Avião estolado não se
endireita sozinho: é o piloto que endireita, ou ninguém.

```
a asa larga: bancos de 30°, 30°, -30°, -30°, -30°, -30°   ✔ tomba
   para os dois lados, sorteado                            ✔
   sempre para o mesmo lado durante um mesmo tombo         ✔
   com o manche: 12° contra 30° de mão solta               ✔ dá para corrigir
```

---

## Olhar com a cabeça — a prova antes do avião

> *"Vi um vídeo sobre FaceMesh, dá para colocar no nosso jogo?"* — e depois,
> quando perguntei quem estaria com a cara na frente da câmera: *"eu tava
> pensando em usar isso só no notebook, que tem a câmera nativa."*

Essa segunda frase é que fez a coisa existir. **No celular não dá**: o telefone
é o *manche*, está na mão sendo torcido, e a câmera dele aponta para o teto. Só
faz sentido na montagem em que o monitor é a tela e o celular é o controle — ali
as mãos estão ocupadas e a cabeça está livre, olhando para a webcam.

### O FaceMesh não entrou, e o motivo é o preço

Medido, baixando as peças:

```
MediaPipe tasks-vision (wasm)   9,0 MB
modelo face_landmarker          3,7 MB      478 pontos do rosto
                               ~13 MB
```

Treze megabytes não cabem no jeito que o jogo é montado — o `montar.py` costura
tudo num arquivo só, que abre offline. E, principalmente: **não precisa**. Os 478
pontos servem para ler expressão. Para virar a câmera de um avião basta saber
*onde* a cabeça está e *quanto* ela ocupa da imagem.

Isso é achar um retângulo, e um detector de 1998 faz isso com o custo de nada:

```
pico.js       5,6 KB    (MIT, Nenad Markuš)
facefinder     234 KB   a cascata treinada
              ~240 KB   — cinquenta vezes menor
```

### Posição, não rotação

Ler para que lado o rosto está *virado* é o caro. Ler para onde a cabeça *andou*
é o barato — e, para pilotar, dá no mesmo: quando você olha para a esquerda, você
também leva a cabeça para a esquerda. O corpo faz isso sozinho. Basta amplificar
(aqui, 150° de olhar por unidade de cabeça andada).

### O centro não é o centro da imagem

Ninguém senta exatamente na frente da webcam. Então o repouso é **aprendido**: uma
média muito lenta de onde a sua cabeça costuma estar. Fique dois minutos olhando
para a esquerda e ela vira o seu novo "reto" — é o que fazem os rastreadores de
cabeça de verdade, e é por isso que existe o botão de recalibrar.

### Quinze vezes por segundo, não sessenta

Uma busca custa de 8 a 12 ms. Um quadro de jogo a 60 por segundo tem 16,7 ms
*no total*. Procurar rosto a cada quadro comeria metade do orçamento do jogo.

E não precisa: cabeça humana não muda de lugar 60 vezes por segundo. A busca
acontece **15 vezes por segundo** e o alisamento roda todo quadro — mesmo
princípio da posição dos outros aviões na batalha, que chega 20 vezes por segundo
e é desenhada 60.

### A câmera é assunto sério neste site

Este é o site oficial da Comissão. Então: botão explícito, desligado por padrão,
dito na tela que **a imagem não sai do aparelho** (e não sai — a conta inteira
acontece dentro da página), e o botão de desligar solta a câmera na hora.

### O que foi medido

Com seis fotos de rosto de verdade, passando pelo mesmo caminho da página:

```
sample1: rosto achado, confiança 139 ·  8,0 ms por leitura   ✔
sample2: rosto achado, confiança 129 ·  8,0 ms               ✔
sample3: rosto achado, confiança 171 · 12,5 ms               ✔
sample4: rosto achado, confiança  32 ·  9,3 ms               ✔
sample5: rosto achado, confiança  73 ·  9,9 ms               ✔
sample6: rosto achado, confiança 462 · 13,7 ms               ✔
```

E com a câmera de mentira do navegador, que não tem rosto nenhum:

```
a câmera abriu (640 px)                        ✔
não inventou rosto onde não tem                ✔
o olhar ficou parado no zero                   ✔
ao desligar, a câmera é solta                  ✔
```

*(A primeira rodada não achou nenhum dos seis rostos. O detector estava certo e
eu estava errado: eu só procurava rostos maiores que 28% da altura da imagem —
tamanho de quem está sentado na frente do notebook — e as fotos de teste eram
cenas largas, com rostos pequenos. O piso caiu para 16% e todos apareceram.)*

Isto é `jogos/rosto.html`, uma página solta: ainda **não** encosta no avião.

---

## A cabeça entrou no avião

Três coisas de uma vez, e as três se encaixam porque são a mesma ideia vista de
ângulos diferentes: **o piloto olha, e o avião entende**.

### 1. A vista obedece à cabeça

Um giro só, aplicado ao trio da câmera, serve às duas vistas — e cada uma pelo
motivo dela:

**Na cabine** é o esperado: o piloto vira a cabeça e o mundo passa.

**De fora** girar só a mira jogaria o próprio avião para fora da tela. Mas
reparei numa coisa ao ler a câmera de perseguição: ela já olha *exatamente* para
o ponto `avião + cima×210`, porque está a `CAMD` atrás dele na direção de `camF`.
Então basta **reancorar a câmera nesse mesmo ponto** depois de girar o trio,
mantendo a distância: ela **orbita** o avião e continua apontada para ele. É o
*check six* — você olha para trás e vê o seu avião e quem vem atrás. Saiu de
graça, sem nenhum caso especial.

```
cabine, olhando 40° à direita: a vista girou 40° para a direita       ✔
e o avião não girou junto: o nariz mudou 0°                           ✔
de fora, olhando 150° para trás: a câmera orbitou, distância 655→655  ✔
e continua olhando para o avião                                       ✔
```

E como com a vista torta é fácil esquecer para onde o **avião** aponta, um risco
no canto diz de que lado está a frente e quantos graus faltam.

### 2. A cabeça escolhe o alvo — mira de capacete

> *"Alvos múltiplos: a minha cabeça indica o alvo que escolhi para o abate."*

Isso tem nome e existe em caça de verdade: **mira de capacete**. E a divisão é a
parte bonita:

- o **cano** continua preso ao avião — bala vai onde o avião aponta, e isso não
  muda nunca;
- o **buscador do míssil** passa a olhar para onde o piloto olha.

Vira a cara para o avião que está na sua esquerda, o míssil trava nele, você
dispara sem apontar o nariz. Sem o olhar ligado, `direcaoDoOlhar()` devolve o
nariz e absolutamente nada muda.

Faltava uma coisa para isso funcionar de verdade: o buscador **não trocava de
alvo depois de travado**, de propósito, para uma turbulência não derrubar a
trava. Com o capacete, trocar de alvo é justamente o que se quer — então ele
passa a trocar quando o alvo antigo **sai do cone do olhar**. É a diferença entre
"a trava é firme" e "a trava é teimosa".

```
sem a cabeça, o buscador pega o que está na frente          ✔
virando a cara para a esquerda, ele troca para o outro      ✔
a metralhadora continua saindo pelo cano, a 0° do nariz     ✔
```

### 3. A nuclear trava no chão

> *"No chão a nuclear também tem que travar, e fazer aquele barulhinho de alvo
> travado. kkkkk"*

Só que a pergunta dela é outra. O míssil pergunta *"o alvo está no cone?"*; a
nuclear é ar-terra e pergunta **"onde é que isto vai cair?"**. Então a conta é a
de um visor de bombardeio: estende-se o raio da mira até o chão e vê-se que alvo
está perto do ponto de impacto. Travou = **se largar agora, acerta**. A cesta é
de 3.000 (150 m); o estrago tem raio 9.000, então quem trava destrói com folga —
a trava aqui não é sobre matar, é sobre **precisão**.

Travada, ela ainda **corrige o rumo atrás do alvo**, com taxa de curva menor que
a do míssil, porque é um bicho pesado.

E aprendi uma coisa medindo: na primeira versão ela travava em alvo a 60 km e a
bomba morria no ar antes de chegar — 9 segundos de vida a `voo × 1,9` dão uns 58
km. **A trava passou a exigir alcance.** O barulhinho de travado é uma promessa
("larga agora que pega"), e mira que promete o que a arma não alcança é mira
mentindo. É a mesma regra do círculo de alcance da metralhadora.

```
alvo de chão a 1105m: travou, é do chão, o tom contínuo tocando   ✔
largando travada: saiu perseguindo, e acertou em 3,5 s            ✔
alvo a 6824m com alcance de 2746m: NÃO travou                     ✔
parada na pista: não trava (largar ali é suicídio)                ✔
```

### E o preço de tudo isso

O detector roda **15 vezes por segundo**, não 60 — uma busca custa de 8 a 12 ms e
um quadro de jogo tem 16,7 no total. O alisamento roda todo quadro, então o
movimento na tela continua contínuo com a leitura entrecortada. Mesmo princípio
da posição dos outros aviões na batalha: chega 20 vezes por segundo, é desenhada
60.

*(O botão nasceu ao lado do olho e da qualidade, em `left:130px`, e a prova de
sobreposição do HUD reprovou na hora: `cPouso` mora exatamente ali. A fileira de
baixo está cheia; ele foi para o vão do canto de cima à esquerda, entre os
painéis e o radar.)*

O botão só aparece em **computador com câmera** — no celular o aparelho *é* o
manche, está na mão sendo torcido e a câmera aponta para o teto. `C` liga; com o
olhar já ligado, `C` recalibra o "reto", que é o que se quer apertar depois de se
acomodar melhor na cadeira. A imagem não sai do aparelho, e desligar solta a
câmera na hora.

---

## Quatro correções, e duas delas eu tinha causado

### 1. O rastro da metralhadora não é para ser desenhado — é para ser medido

> *"Ela está com um rastro fixo e grande. Não é isso: o rastro se forma
> dependendo do movimento do avião."*

Terceira versão desta mira, e as três valem a pena ficar registradas:

1. **linha curta**, de 28% a 100% do alcance — trinta pixels parados no meio da
   tela: *"ficou muito curto e não acompanha o movimento"*;
2. **linha longa**, começando colada no cano — varria a tela ao manobrar, mas
   virou um trilho fixo atravessando tudo, atirando ou não;
3. **esta** — e o pedido, relido, é uma ideia melhor do que as minhas duas.

Agora são duas peças com papéis separados:

**O anel**, sempre presente e pequeno, onde o cano aponta. É a mira: o ponto do
meio é por onde a bala passa, o anel dá o tamanho angular do alvo, o número diz
até onde ela chega. Nada de trilho quando não se está atirando.

**O rastro**, só quando há bala no ar, desenhado pelas **posições reais** das
balas que estão voando. Voando reto sai reto; numa curva encurva sozinho, porque
as balas ficaram para trás de verdade. Não é efeito: é o estado do mundo lido e
projetado na tela. Aparece quando o dedo aperta e some quando solta.

*(A média móvel de três pontos existe porque as balas nascem espalhadas até 110
para o lado — os canos são nas asas. Sem ela a linha ficava serrilhada de perto.)*

### 2. A órbita da cabeça estava errada, e o erro era meu

> *"O movimento da cabeça funcionou, mas ao olhar para a esquerda ele fez a tela
> girar para a direita."*

Na vista de fora eu fazia a câmera **orbitar** o avião e continuar apontada para
ele. No papel era bonito — você vê o seu avião e quem vem atrás. Na mão é outra
coisa: com a mira colada no avião, ele fica **cravado no meio da tela e o mundo
inteiro roda em volta dele**. O olho não lê isso como "virei a cabeça"; lê como
"a tela girou". Virar a cabeça, na vida real, deixa o mundo parado e faz as
coisas passarem pelo campo de visão.

Agora é o mesmo giro nas duas vistas, e **só** o giro: a câmera fica onde está e
o olhar é que vira. Seu avião escorrega para o lado e sai de cena quando você
olha para trás — que é o certo, porque olhar para trás é deixar de olhar para a
frente. O risco no canto continua dizendo de que lado ficou o nariz.

```
de fora, olhando 150° para trás: a câmera andou 0          ✔ o mundo não roda
olhando 50° à esquerda, a vista aponta para a esquerda     ✔
```

### 3. Um trem, com vagões

> *"Quero mais alvos no chão, inclusive em movimento. Coloca um trem com vagões
> para servir de alvo para treinar os movimentos."*

É o melhor alvo de treino que existe, e por um motivo específico: anda depressa,
anda **reto** e anda no chão. Alvo parado ensina a apontar; alvo que manobra é
frustrante; alvo que corre em linha reta ensina exatamente o que falta — **dar
dianteira**. Erra atrás, corrige, erra na frente, corrige, e em três passagens a
mão aprende.

Uma locomotiva e oito vagões, na linha férrea que corre paralela à pista. Cada
vagão é um **obstáculo como qualquer outro**, então entrou de graça no radar, no
travamento do míssil, na solução de tiro, na pontuação (150 o vagão, 300 a
locomotiva) e na colisão. Só a *posição* não vem do passo genérico: vem do trem,
senão ao dar a volta no fim do mapa um vagão viraria antes do outro e o trem se
partiria no meio.

E os alvos de chão passaram de **18 para 26** — o mapa tinha dobrado de tamanho e
continuado com a mesma conta.

*(Ele se chama `Ferrovia` no código, e não `Trem`, porque neste jogo `trem` já é
o trem de POUSO e existe um `mexeTrem()` a poucas linhas dali.)*

**E aqui o teste me corrigiu.** Eu tinha escrito uma prova ingênua: "mirar no
vagão parado não deve travar; mirar adiante deve". Ela falhou — travava nos dois
casos. O jogo estava certo e a pergunta estava errada: mirando no vagão nº 1
parado, a solução de tiro **é o vagão nº 2**, o de trás, porque é ele que vai
estar ali quando a bala chegar. A prova passou a perguntar *qual* vagão a mira
escolhe:

```
mirando no vagão 1 parado, a solução é o vagão 2;
mirando 997 à frente, é o vagão 1          ✔ a dianteira escolhe o vagão
```

### 4. O estol não tinha culpa: o profundor é que era reto

> *"No estol de subida o piloto não consegue ficar com o nariz voltado para cima
> por muito tempo; sempre o estol faz ele embicar."*

Fui medir antes de mexer no estol, e ele era inocente. **Duas** coisas, as duas
no comando:

**O profundor era reto enquanto o aileron já tinha curva.** Inclinando o celular
só 8° e segurando 2 segundos, o nariz ia parar a 40°; a 11°, ia a 55°. Não dá
para escolher 20° de subida com um comando desses — passa-se direto, e aí sim vem
o estol, que levava a culpa. Agora ele tem a mesma gramática do aileron: perto do
meio o avião levanta o nariz devagar, e a taxa cheia só vem no fim do curso. A
taxa **máxima** não mudou — cambalhota fecha no mesmo tempo.

**E o nivelador automático tinha um penhasco.** Esta eu só vi medindo: ele valia
até 26° de nariz e ali parava de repente. O resultado era um jogo sem meio-termo
— puxar até 19° e soltar levava o nariz de volta a 2°; puxar até 28° deixava o
nariz cravado em 28° para sempre. Não existia "subir um pouco". Agora ele
desvanece entre 8° e 35°, e é **assimétrico**: nariz para baixo com a mão solta é
o que mata o iniciante, e ali o endireitamento continua firme; nariz para cima é
**intenção**, e ali o avião só abaixa o bico devagarinho, como um avião fora de
compensação.

```
inclinando o celular 0,5 s e soltando, o nariz assenta em:
   antes:  5°→0°    8°→1°    11°→2°    15°→28°   22°→41°
   agora:  5°→1°    8°→2°    11°→5°    15°→9°    22°→24°

segurando 2 s:
   antes:  8°→40°   11°→55°   22°→87°
   agora:  8°→10°   11°→26°   22°→73°
```

De brinde, a decolagem ficou muito melhor: o traço quadro a quadro sobe suave de
8° a 16° de nariz, onde antes rampava até 39° e estolava.

---

## O pescoço: um limite que é limite, e o sinal decidido na mão

> *"Ainda está estranho. E tem um limite: não tem como eu estar num avião e
> olhar 180 graus. Tem uma limitação angular, e tem que ser suave."*
>
> *"Ao olhar para a direita — nariz apontando para a direita, minha mão direita
> — a tela deveria ir para a direita. A tela está indo para o outro lado."*

Quatro coisas produziam o "estranho", e vale separar porque cada uma tinha uma
causa diferente.

### O teto era uma parede

Era um corte (`Math.min`) em 145°. Corte não é limite de pescoço, é parede: você
chega lá e o mundo simplesmente para de se mexer por mais que você continue
virando. Pescoço vai ficando **duro** até não ir mais.

Virou uma `tanh`: perto do meio ela não faz nada, e quanto mais perto do limite,
mais comprime. Nunca passa, nunca bate. E o limite caiu de 145° para **100°**,
que é o que um piloto amarrado no assento alcança torcendo o tronco — 145° era
olhar por cima do encosto, coisa que ninguém faz voando.

```
os últimos degraus, com passos iguais de cabeça: +0,9°  +0,2°  +0,0°
                                                  ✔ vai endurecendo, não bate
```

### A resposta era reta

Um fio de cabeça no meio já mexia a vista inteira. Mesmo remédio que resolveu o
manche e o aileron: **curva** (expoente 1,6). A região do meio — onde a cabeça
vive — fica calma, e o ganho só aparece quando você realmente vira.

```
 5% da imagem ->   0,4°        30% ->  64°
10% da imagem ->   7,2°        45% ->  92°
20% da imagem ->  33,3°        60% ->  99°
```

### O repouso aprendia enquanto você olhava

Ele aprendia **sempre**, inclusive com a sua cabeça virada — e aí, segurando o
olhar dez segundos, o "reto" andava atrás de você e a vista voltava sozinha para
o meio com a cabeça ainda torta. Isso é estranho de um jeito difícil de
descrever, que é exatamente como a queixa chegou.

Agora ele só aprende quando você está **perto do meio**: é onde a cabeça fica
quando não está fazendo nada, que é a definição de repouso.

### Perder o rosto soltava a vista

E perde-se o rosto justamente quando se vira muito — quando você mais quer que a
vista fique parada. Agora ela **segura firme por 0,7 s** e só então escorre de
volta, em uns dois segundos. Piscada de detector não mexe mais em nada.

```
15 s com a cabeça virada: a vista foi de 85° para 85°   ✔ não escorrega
duas leituras sem rosto:  ficou em 85°                  ✔ segura
3 s sem rosto nenhum:     voltou para 24°               ✔ volta sozinha
```

### E o sinal estava invertido — a mão ganhou do papel

Eu tinha espelhado o X por raciocínio, e o raciocínio é bom: a webcam vê você
como outra pessoa veria, então o seu lado direito cai na esquerda da imagem.

Só que isso vale para quem se **desloca** de lado. E ninguém desliza: as pessoas
**viram o rosto**. Girando a cabeça, ela não escorrega — ela pivota num eixo que
fica *atrás* do rosto, no pescoço. O nariz vai para a direita e o bloco do rosto
varre para o outro lado.

Não há teoria que ganhe de *"ao olhar para a direita, a tela está indo para o
outro lado"*. A página de prova (`jogos/rosto.html`) mudou junto — duas páginas
com convenções contrárias seria uma armadilha guardada para daqui a três meses.

### E aí veio a teoria contrária, também certa

> *"É que se você está dentro do computador olhando para mim, seria a sua
> esquerda... kkkkk"*

Perfeitamente certo — e é o argumento do espelho, o mesmo que eu tinha usado na
primeira versão. Ou seja: **duas explicações honestas puxando para lados
opostos**, cada uma valendo para um jeito de mexer a cabeça.

- **Deslizando** de lado vale o espelho: a webcam te vê como outra pessoa veria.
- **Virando** o rosto vale o contrário: a cabeça pivota num eixo atrás do rosto.

Qual das duas manda depende de como cada pessoa mexe a cabeça, de onde está a
webcam e de quão longe se senta. Isso não se decide no papel — eu já tentei duas
vezes, e a segunda foi guiada por um teste real que ainda assim não fecha a
questão para todo mundo.

Então tem **tecla**: `X` inverte o lado e fica guardado no aparelho. Dois
segundos para acertar, para sempre, em vez de mais uma rodada de adivinhação. É
o tipo de coisa que devia ter nascido com botão.

---

## O HUD é vidro preso no avião — e havia um bug escondido atrás disso

> *"Já sei o que pode estar causando esse desconforto: é o HUD! Ao mexer a
> cabeça o HUD não pode ir junto; tudo tem que estar estático quando a cabeça
> se move."*
>
> *"Aí dá a sensação de mover a cabeça e não mover o avião — você não controla o
> avião, controla apenas o campo de visão."*

Esse é o diagnóstico inteiro, e é de manual. HUD de verdade é uma placa de vidro
montada na frente do piloto, **presa à fuselagem**. Virando a cabeça, ela sai do
campo de visão como sai qualquer outra coisa do avião — o painel, a moldura da
cabine, a asa. Ela não acompanha o olho.

O nosso estava desenhado num canvas colado na tela, então acompanhava. O mundo
varria e os instrumentos ficavam grudados na cara — e é essa contradição que o
corpo lê como enjoo: metade da imagem diz *"você virou"* e a outra metade diz
*"você não virou"*.

Agora o vidro anda com o nariz, e os painéis em HTML vão junto (pela propriedade
`translate`, que é separada do `transform` — assim os painéis que já se
centralizam com `translateX(-50%)` continuam inteiros).

O que **não** se desloca, e por quê:

- o clarão e o pulso nas bordas — são coisas do **olho**, não do avião;
- tudo o que já vem projetado pela câmera (mira, travas, marcas dos outros
  aviões, escada de arfagem): a projeção já contém o giro, e deslocar de novo
  seria contar duas vezes;
- o aviso de `NARIZ 40°`, que existe justamente para quem está olhando de lado;
- os botões, que precisam continuar clicáveis.

### Perguntar em vez de deduzir

A primeira versão calculava o deslocamento a partir do ângulo da cabeça, com
`tan(θ)/tan(fov/2)` e um sinal que eu deduzi. A conta estava certa e **o sinal
estava errado** — o HUD corria para o lado oposto ao do nariz, que é o dobro do
defeito que se estava consertando.

Deduzir de que lado o nariz cai na tela exige acertar, de cabeça, a mão do
sistema de eixos, a ordem do produto vetorial e a convenção da câmera do
three.js. Não é preciso: **basta perguntar**. O nariz é um ponto do mundo e a
câmera sabe onde ele cai. A conta põe o nariz no espaço da câmera e lê o desvio
direto de lá — sem sinal nenhum para eu errar, e continua certa se um dia a
convenção mudar.

```
olhando 30°: o nariz caiu em x=762 (meio da tela = 450) e o vidro andou 312  ✔
os painéis em HTML foram junto: x=14 -> 327                                  ✔
olhando 80°: painel em x=1454, fora da tela de 900                           ✔
pixels de HUD desenhados: 40492 parado -> 29743 a 30° -> 1568 a 80°          ✔
```

### E o bug que estava embaixo

A prova do vidro desenterrou algo bem pior, que era boa parte do *"ainda está
estranho"*: **o giro da cabeça estava realimentando a câmera**.

Na vista de fora, `camF` é **estado** — ele persegue o nariz de um quadro para o
outro (`camF += (eixoF - camF)*k`). Eu estava girando o próprio `camF`. Então o
giro da cabeça entrava no estado: no quadro seguinte a perseguição puxava 11% de
volta e a cabeça somava os mesmos graus **outra vez**. O erro se acumulava até a
perseguição empatar com ele — umas **nove vezes** maior do que devia. Vinte graus
de cabeça viravam uma câmera girada quase noventa, chegando lá devagar,
escorrendo.

Realimentação é a coisa mais difícil de enxergar num laço de câmera, porque o
resultado não parece um bug: parece calibração ruim. Agora o olhar devolve uma
**cópia** — o estado segue o avião, o olhar é aplicado por cima na hora de olhar,
e não sobra nada para o quadro seguinte.

```
depois de 120 quadros com 20° de cabeça, o estado da câmera
está a 0° do nariz                          ✔ o olhar não realimenta
```

*(E a prova do `cabeca` teve de mudar junto: ela lia `camF` para saber para onde
se estava olhando, e `camF` deixou de ser essa resposta. Agora ela pergunta à
câmera do three.js, que é quem sabe.)*


### E na cabine, duas peças que tinham ficado para trás

A foto com a cabeça a 35° dentro da cabine mostrou o HUD inteiro escorrendo com
o nariz e **duas coisas paradas na tela**: a cruz do canhão e as réguas de
potência/nitro.

Ambas são do vidro, e pelo mesmo motivo. A **cruz do canhão** marca para onde o
nariz aponta — uma cruz de mira flutuando no meio de uma vista que não é a do
nariz é a mentira mais confusa que este HUD poderia contar. As **réguas** são
instrumento de cabine como qualquer outro.

A escada de arfagem, ao lado da cruz no mesmo bloco, é o contrário: vem da
projeção da câmera, já contém o giro, e continua desenhada na tela crua.

```
a cruz do canhão, a 25° de cabeça: 49 px no meio da tela
                                  e 234 px em cima do nariz   ✔ foi com o vidro
```

---

## A duplicata das duas miras, e o vazamento que ela desenterrou

> *"Sobre a mira da metralhadora: só com o 'olhar com a cabeça' é que libera a
> segunda mira?"*

Não libera nada. O que havia era **duplicata**, e a pergunta a encontrou. Medido
na cabine:

```
olhar desligado     cruz em 450, anel em 450   ->  0 px de distância
olhar ligado a  0°  cruz em 450, anel em 450   ->  0 px
olhar ligado a 15°  cruz em 590, anel em 590   ->  0 px
```

Sempre no mesmo pixel, e não por acaso: as duas marcam **a mesma coisa** — para
onde o nariz aponta. Uma é a cruz antiga da cabine, a outra é o anel novo da
metralhadora, que ainda traz o alcance escrito embaixo.

Com a metralhadora na mão, agora só existe o anel. Com o míssil e com a nuclear,
que não têm anel, a cruz continua: é ela que diz onde é o meio.

### E o teto do vidro estava aberto

A prova de contar pixels no meio do vidro achou algo pior de tabela: na cabine,
com a cabeça a 15°, o anel **sumia**. Ele não sumia — estava sendo desenhado
140 px adiante do lugar.

O `presoNaTela()` que fecha o vidro depois das réguas do motor tinha caído no
lugar errado do arquivo, quarenta linhas abaixo, no meio do bloco das marcas dos
outros aviões. Tudo o que era desenhado entre um ponto e outro saía deslocado
duas vezes: o anel, a caixa do buscador, as marcas dos outros jogadores — tudo o
que já vinha projetado pela câmera.

Vale a lição: transformação de canvas é **estado global**, e estado global que se
abre num lugar e se fecha em outro é uma armadilha silenciosa — nada quebra, tudo
só aparece um pouco fora do lugar. A prova que mede *"quantos pixels verdes há
onde eu espero"* pega isso; ler o código não pegava.

---

## As duas miras da metralhadora (e o erro de interpretação que me custou uma volta)

> *"A metralhadora tem que ter duas miras, uma interna e outra externa, sendo a
> mesma mira: quando o avião desloca, a externa acompanha onde vai o disparo.
> Reto, as duas centralizam; em curva, se separam — e a linha da bala liga as
> duas. E essa linha sempre existe, não só quando atira."*

Isto é uma **mira giroscópica**, que é como se atira de caça desde 1943. É a
quarta versão desta mira, e a lição desta rodada não é de conta — é de leitura.

### Eu já tinha construído esta curva, e joguei fora

Numa rodada anterior eu fiz exatamente esta curva, medi e concluí *"está
errada"*. A medição dizia: **uma bala disparada agora termina na linha reta do
cano, não na curva**. Isso era verdade e continua sendo. O erro foi meu, ao
perguntar à curva uma coisa que não é o trabalho dela.

As duas marcas respondem a **duas perguntas diferentes**:

- **A cruz (interna) é o cano.** Bala que sai agora vai por ali. É a resposta
  daquela medição, e é por isso que a cruz existe.
- **O anel (externo) é onde o rastro está.** As balas que já estão no ar saíram
  quando o nariz apontava para outro lugar; em curva elas ficam para trás de
  `ω·t`. É o que se enxerga pela janela.

E é o anel que serve para **mirar** num alvo que você acompanha na curva: pondo o
anel em cima dele, o cano fica automaticamente adiantado do tanto certo. Essa é a
ideia inteira da mira giroscópica.

Voando reto, `ω` é zero: a curva vira um ponto e as duas marcas viram uma. Não
por gentileza — é a geometria.

### Duas armadilhas de geometria, as duas pegas medindo

**A câmera não fica na linha do cano.** A primeira tentativa desenhou a
trajetória de verdade, cada ponto a uma distância diferente. Reprovou: a câmera
de perseguição fica 210 acima da linha do cano, então o ponto perto do avião e o
ponto longe caem em lugares diferentes da tela **mesmo voando reto** — as duas
marcas nasciam separadas por 63 px sem curva nenhuma. Agora todos os pontos ficam
à mesma distância e só o ângulo muda: vira um arco que sai da cruz e termina no
anel, ligando as duas nas duas vistas.

**O batente.** Numa curva violenta — 58°/s de nariz, que este avião faz — a
dianteira dá 64°, e o anel saía voando para fora da tela com a linha
atravessando tudo. Mira giroscópica de verdade tem batente pelo mesmo motivo: o
retículo é uma imagem num vidro que tem tamanho. O limite aqui é 16°, e no
batente o anel fica âmbar e vazado — que é o que um batente diz: *"a dianteira
que você precisa é maior do que eu mostro; alivie a curva"*.

### A prova, e as três provas erradas antes dela

Comparar o anel com *"a bala mais velha do ar"* não presta: na curva a velocidade
cai (a bala velha saiu mais rápida que as de agora), o avião ainda percorre o
arco, e qual é a bala mais velha depende de quantos quadros o teste atirou. Foi
assim que a primeira versão da prova acusou 42° de erro que não existiam.

A afirmação que a mira giroscópica realmente faz é exata:

> Acompanhando um alvo — o nariz varrendo na mesma taxa em que a linha de visada
> gira —, o **anel cai em cima do alvo** no instante em que o **cano** está
> apontado para a dianteira certa.

Sai da conta, sem aproximação: a taxa de visada de um alvo que cruza a `Vt` a uma
distância `D` é `Vt/D`; o giro do nariz que o acompanha é o mesmo; então o
deslocamento do anel é `ω·t = (Vt/D)·(D/vB) = Vt/vB` — exatamente a dianteira.

Montar essa situação no teste me custou mais três erros, todos meus:

1. pus `giroNariz` na mão com um sinal chutado — circular, o teste passou a medir
   o meu chute. Passou a ser **derivado** do jeito que o jogo deriva: produto
   vetorial entre o nariz de antes e o de agora;
2. perguntei a solução de tiro **antes** de apontar o cano, então o travamento
   não pegava e a mira supunha o alcance cheio em vez da distância do alvo;
3. o próprio teste não copiava a regra de alcance do HUD, e media um anel que o
   jogo não desenha.

Corrigidos os três:

```
1) voando reto: as duas marcas a 0,0 px uma da outra          ✔ viram uma só
2) em curva a 58°/s: separadas por 143 px, dianteira de 16°   ✔ e sem sair da tela
3) acompanhando um alvo que cruza a 1500 a 13.464 de distância:
   o cano aponta 4,2° adiante do alvo (a dianteira)
   o anel cai a 0,0° do alvo                                  ✔
   (com o sinal trocado cairia a 8,4°)
4) a cruz interna está a 0 px da linha reta do cano           ✔ é o cano mesmo
```


### Uma cor só

> *"Coloca tudo verde o HUD do canhão. Deixa a mesma cor."*

Havia três tintas ali sem querer: o verde do HUD (`120,255,170`), um verde mais
claro que tinha entrado junto com a solução de tiro (`150,255,190`) e um âmbar
para o batente. Agora é **uma só**, e o que muda entre travado, solto e no
batente é a **grossura** e o **desenho** — o anel no batente perde os riscos —,
nunca a tinta.

Num HUD, cor que muda é cor que quer dizer alguma coisa. Aquelas não queriam.

*(De tabela: a palavra `ATIRE` ia logo acima do losango, e o losango vive dentro
do anel quando o alvo está centrado — a palavra saía escrita por cima do aro.
Agora ela sobe acima do que estiver mais alto dos dois.)*

---

## O míssil passou a cobrar caro

> *"Acho que não pode ser tão fácil o disparo com o míssil, fica muito apelão no
> combate aéreo — fica como quem cravar primeiro. Tem que cravar e continuar na
> trava; se perder o HUD de trava, o míssil perde o rumo."*

Este é um problema de **jogo**, não de física, e é o problema clássico da arma
que não cobra nada de quem atira: se disparar é grátis, o combate degenera em
quem aperta o botão primeiro. Todo jogo de caça que ficou bom resolveu isso
cobrando alguma coisa depois do disparo.

Agora a trava **não se gasta** no tiro. Ela continua, e o míssil só se guia
enquanto ela existir:

- o alvo saiu do cone do olhar → perdeu a trava → o míssil segue reto até morrer;
- o piloto olhou para outro alvo → mesma coisa;
- trocou de arma → mesma coisa.

E **uma vez burro, burro para sempre**: recuperar a trava não traz o míssil de
volta. Se trouxesse, a regra não custaria nada — bastaria piscar o olhar e
retomar.

O preço, na prática, é ficar **preso ao alvo** durante os segundos em que o
míssil voa: sem manobrar à vontade, sem procurar o próximo. Que é exatamente o
que o pedido descreve.

No HUD a caixa do buscador passa a dizer **GUIANDO** em vez de `TRAVADO` quando
há míssil no ar dependendo daquela trava — a diferença importa, porque soltar o
alvo nesse momento custa um míssil. E quando a trava cai com míssil no ar, o
aviso é explícito: `TRAVA PERDIDA — MÍSSIL SEM RUMO`, com um bipe grave.

A nuclear continua sendo largada e esquecida: ela é ar-terra, o alvo não desvia,
e a regra existe para equilibrar combate aéreo — não para punir bombardeio.

### E o capacete estava certo

> *"Ao selecionar o alvo com o capacete, eu olhei para a esquerda e a mira foi
> para a direita. Não sei se já arrumou isso."*

Já, e de graça: a tecla `X` inverte o lado da cabeça, e o buscador lê **o mesmo
valor** que a câmera. Medido, com o espelho nos dois sentidos:

```
com espelho +1: o buscador aponta a 0,0° de onde a vista aponta   ✔
com espelho -1: o buscador aponta a 0,0° de onde a vista aponta   ✔
```

Ou seja: se a vista vai para o lado certo depois do `X`, a trava vai junto,
sempre. Não há como um ficar certo e o outro errado.

```
de frente trava o alvo em frente; virando a cabeça trava o de lado   ✔
depois de disparar, a trava continua e o míssil segue                ✔
segurando o alvo na mira o tempo todo: acertou                       ✔
largando a trava no meio do voo: o míssil perde o rumo               ✔
e o alvo escapa                                                      ✔
travando de novo, o míssil perdido continua perdido                  ✔
```

*(A prova ainda encontrou um buraco de estado: `Cabeca.passo` estourava se
alguém ligasse o olhar sem passar pela câmera. O jogo não faz isso, mas um
`liga()` que falhasse no meio poderia — e estado que só é coerente por convenção
é estado que um dia quebra. Ganhou uma guarda de uma linha.)*

---

## Contramedidas, e o alerta que as torna uma escolha

> *"Quero incluir um antimíssil, contramedida, uns fogos que o avião joga para o
> míssil perder o rumo. Aí acho que ficará mais legal o combate aéreo."*

Ficará, e vale dizer por quê: sem elas o combate é decidido por quem trava
primeiro, e a única defesa é não ser visto. Com elas existe uma **resposta** — e
resposta é o que transforma troca de tiros em duelo. Quem atira tem de segurar a
trava; quem é travado tem de gastar chama na hora certa. Os dois têm o que fazer
no mesmo instante, que é a definição de um bom combate.

Três regras fazem isso funcionar como jogo:

- são **contadas** (doze), senão a resposta certa é apertar sempre;
- têm **espera** entre uma e outra, senão bastava esvaziar tudo de uma vez;
- e são **tardias**: com o míssil a menos de 3.500 do alvo, não salvam mais
  ninguém.

A terceira é a que cria a decisão interessante. Quem foge tem de soltar cedo, sem
saber se já foi disparado míssil nenhum, gastando carga à toa se errar a hora.
Quem atira aprende a esperar a chama do outro acabar antes de puxar o gatilho.
Nenhum dos dois tem resposta automática.

### O alerta, que não era opcional

Sem saber que está sendo travado, soltar chama é adivinhação. Então entrou junto
o **receptor de alerta**: quem trava avisa o alvo pela rede, e o alvo vê
`TRAVADO` piscando e ouve um som novo.

Os dois sons são o oposto um do outro de propósito: o de travamento é firme e
agudo e quer dizer *"consegui"*; o de alerta é rápido, repetido e desconfortável
e quer dizer *"corre"*. Num jogo que se joga com o celular na mão e os olhos na
tela, som é o único canal que sobra livre.

*(Duas coisas que a foto do HUD corrigiu: o clarão vermelho de borda estava indo
junto com o alerta, e estar travado DURA — a tela ficava vermelha o combate
inteiro. Clarão de borda é para o instante em que se leva tiro. E o baque
reaproveitado era o do `levou`, um soco de 0,52; virou um susto próprio de 0,16,
uma vez só, na hora em que a trava fecha.)*

```
uma salva: 12 -> 11 cargas, 8 chamas no ar; a segunda logo em seguida não sai  ✔
as chamas somem sozinhas · passada a espera, sai outra · sem carga não sai     ✔
recado de trava: o alerta toca; quando ele solta, o alerta cala                ✔
ele solta chama: a minha trava cai                                             ✔
com o míssil a 1200 dele: a chama NÃO salva (tarde demais)                     ✔
com o míssil a 9000 dele: salva                                                ✔
```

---

## O rastro não é um arco

> *"A linha entre a mira externa e a central não pode ser retilínea. Tem que ser
> o traçado onde a bala vai: se o avião faz várias curvas, o traço das balas
> também faz curva."*

Certo, e a versão anterior não dava conta. Ela desenhava um arco a partir da taxa
de giro **de agora** — o que só está certo se a curva for constante. Num S, o
rastro de verdade serpenteia, e um arco de raio fixo mente.

Um instante da rotação não tem essa informação. Quem tem é a **história**: cada
bala no ar saiu num instante diferente, na direção em que o nariz estava naquele
instante. Então o jogo guarda essa direção quadro a quadro, por um segundo e
meio, e a curva do HUD é lida dessa fita.

Ela sai reta quando se voou reto, em arco quando a curva foi constante, e
serpenteando quando o avião serpenteou — **sem nenhum caso especial**, é a mesma
leitura.

```
numa curva mansa os segmentos dobram sempre para o mesmo lado (-1,-1,-1,-1,-1,-1)  ✔
logo depois de inverter o aileron, dobram para os dois (1,1,1,1,1,-1)              ✔
voando reto as duas marcas continuam a 0,0 px uma da outra                         ✔
acompanhando um alvo, o anel continua caindo a 0,0° dele                           ✔
```

O batente passou a ser aplicado **à fita**: ela é lida do presente para trás e
cortada exatamente nos 16° (interpolando entre duas amostras — cortar na amostra
seguinte deixava o batente parar onde calhasse, a 25° ou a 30°). Numa curva
violenta isso quer dizer que só o quarto de segundo mais recente aparece: o sight
está nos limites e não mostra o passado, que é o certo.

*(E a prova `novo` pegou um defeito de tabela: recomeçar o jogo não limpava a
fita, então no primeiro segundo do voo novo a mira lia direções do voo anterior —
que podiam estar até atrás da câmera, apagando a mira inteira. Ela agora é limpa
no reinício, e a curva corta no primeiro ponto que estiver atrás em vez de
sumir toda.)*

---

## O cogumelo, refeito com partículas

> *"A explosão nuclear está muito ruim. Faz uma física melhor de partículas para
> a explosão, está muito feio."*

Estava, e o motivo era estrutural: um **cilindro** com uma esfera achatada em
cima. Cilindro e esfera são superfícies lisas, e nuvem nenhuma é lisa — a
leitura instantânea de "nuvem" vem da textura **fervendo**, não do contorno.
Nenhum ajuste de cor salvaria aquilo.

O que uma nuclear é, e que dá para reproduzir barato — quatro famílias de
partículas, cada uma com a sua física:

**A bola de fogo.** Nasce, cresce depressa e **esfria**: branco, amarelo,
laranja, vermelho escuro, apaga. É a única parte quente, e dura dois segundos.

**O anel de vórtice.** Isto é o coração do troço e é o que quase ninguém
desenha. O "chapéu" não é uma bola: é um anel de fumaça — um toro — que sobe
**girando em torno do próprio tubo**. É esse rolamento que faz a nuvem ferver.
Cada partícula tem um ângulo em volta do eixo e uma fase dentro do tubo, e a
fase avança sozinha. Sai de graça, e é o que dá vida.

**A haste.** Não é um cano: é poeira sugada do chão subindo **em espiral**,
alimentando o anel.

**A saia de base.** O jato que bate no chão e escorre rasteiro para os lados. É
a assinatura de um estouro no solo, e é ela que amarra o cogumelo ao chão em vez
de deixá-lo pairando.

Custa **três ordens de desenho**, as mesmas da versão feia: um `InstancedMesh`
com trezentas bolinhas — a placa recebe uma esfera e uma lista de matrizes —,
mais o anel de choque e a marca de queimado. A cor vai **por instância**, que é
o que deixa a bola de fogo esfriar de branco a preto sem material nenhum a mais,
e o que dá à nuvem um cinza diferente por bolinha (uma nuvem de uma cor só lê
como massa de plástico) com a parte de baixo do anel mais escura que a de cima.

### Duas medidas que a foto corrigiu

**Estava pequeno.** O raio de morte da bomba é 9.000 e a nuvem tinha 3.000 de
largura — a explosão parecia menor do que é. Subiu para 8.200 de altura e 4.400
de raio de anel: uma nuclear tem de encher o céu.

**E a haste sumia de longe.** Medida numericamente a 38 km: 1.026 de raio contra
6.113 do chapéu. Isso é a proporção real, e é ilegível — o cogumelo virava uma
nuvem flutuando. Engrossou para 1.220: menos realista, mais reconhecível, e o
que faz reconhecer um cogumelo é o **T**.
