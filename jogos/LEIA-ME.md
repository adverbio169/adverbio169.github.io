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
