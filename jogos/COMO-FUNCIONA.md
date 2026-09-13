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
