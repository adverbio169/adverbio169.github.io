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
3. **No iPhone e iPad é preciso pedir permissão**, e o pedido só é aceito se
   sair de um toque do usuário — por isso o pedido fica dentro do clique do
   botão "Jogar", nunca no carregamento da página:

```js
if (typeof DeviceOrientationEvent.requestPermission === 'function') {
  const r = await DeviceOrientationEvent.requestPermission();
  if (r !== 'granted') { /* cai para o controle por toque */ }
}
```

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
ronco) mais ruído filtrado (o ar). A altura do ronco acompanha a velocidade, o
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
