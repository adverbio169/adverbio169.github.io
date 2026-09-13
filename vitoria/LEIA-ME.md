# O desenho da Vitória

Vídeo animado feito a partir do desenho da Vitória.

- `desenho-da-vitoria.mp4` — o vídeo (900x1120, 30 fps, 21 s, com trilha)
- `capa.png` — imagem de capa
- `index.html` — página simples que toca o vídeo
- `gerar_video.py` — script que gera a animação
- `gerar_musica.py` — script que gera a trilha (`trilha.wav`)
- `jogo/` — **Corrida da Vitória**, um jogo 3D com a personagem do desenho

O desenho original (círculo, quadradinhos dos olhos, retângulos, triângulo
vermelho do chapéu) foi remontado em vetores dentro do script. A animação tem
três partes: o título aparecendo, o desenho sendo feito traço a traço, e o
personagem ganhando vida (pulinho, braços acenando, olhos piscando e corações).

A trilha é uma musiquinha instrumental original, no estilo caixinha de música /
piano de brinquedo, sintetizada do zero pelo `gerar_musica.py` — nada de música
de terceiros, então pode publicar sem problema de direito autoral. Ela está a
120 bpm e os cortes da animação caem certinho nos compassos: a melodia calma
acompanha o desenho sendo feito (2 s a 12 s) e a parte animada, com chocalho e
bumbo, entra exatamente quando o desenho ganha vida (12 s a 20 s).

## Como gerar de novo

```bash
pip install pillow imageio-ffmpeg numpy
python3 gerar_video.py desenho-mudo.mp4   # animação (e capa.png)
python3 gerar_musica.py                   # trilha.wav
ffmpeg -i desenho-mudo.mp4 -i trilha.wav -c:v copy -c:a aac -b:a 192k \
       -shortest -movflags +faststart desenho-da-vitoria.mp4
```

Para mudar o desenho, edite as coordenadas em `PARTS` no `gerar_video.py`;
para mudar o ritmo, os tempos `dur` de cada parte e as constantes `T_*`.
Para mudar a música, a lista `MELODIA` (tempo, duração, nota, volume) e os
acordes em `ACORDES` no `gerar_musica.py`.

## O jogo (`jogo/`)

`jogo/index.html` é um arquivo só, sem build: abre direto no navegador do
celular ou do computador. É um corre-sem-fim em 3D (estilo Sonic/Mario: só
para a frente) com a Vitória do desenho, montada em 3D com as mesmas formas —
círculo, retângulos, triângulo vermelho do chapéu — e o mundo inteiro em
"papel": branco com traço preto.

- **Controle por acelerômetro**: incline o celular para os lados para desviar.
  No iPhone o navegador pede permissão do sensor no primeiro toque em Começar.
- **Toque na tela** para pular (no computador: setas e barra de espaço).
  Sem sensor, dá para arrastar o dedo para os lados.
- Pegue corações, desvie dos blocos vermelhos, pule nas molas amarelas.
  Três vidas; a velocidade vai aumentando. O recorde fica salvo no aparelho.
- A música e os efeitos são sintetizados na hora pelo próprio navegador
  (Web Audio), sem nenhum arquivo de áudio.
- O 3D usa a biblioteca Three.js, carregada de CDN — precisa de internet na
  primeira abertura.
