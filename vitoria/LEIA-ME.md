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
celular ou do computador. É um jogo de plataforma **em 3D com câmera lateral**
(a Vitória corre da esquerda para a direita, estilo Sonic/Mario clássico, só
que em 3D). Ela corre sozinha; você controla a velocidade e o pulo.

A personagem foi modelada em 3D a partir do desenho — o chapéu vermelho, os
olhinhos quadrados, a saia — com sombreado *cel shading* e contorno de tinta,
para parecer o desenho ganhando volume. Tem braços e pernas articulados
(cotovelo e joelho), cabelo com maria-chiquinhas e sapatinhos vermelhos.

- **Controle por acelerômetro**: o ângulo do aparelho manda no movimento —
  incline para a direita e ela anda para frente, para a esquerda e ela volta;
  no meio, ela fica parada. Quanto maior a inclinação, mais rápido. No iPhone
  o navegador pede permissão do sensor no primeiro toque em Começar.
- **Toque na tela** para pular (ela dá um mortal no ar). No computador:
  **→** acelera, **←** segura e **espaço** pula.
- Pule os buracos, suba nas plataformas, pegue corações, desvie dos blocos
  vermelhos e use as molas amarelas. Três vidas; se cair no buraco ela volta
  para a próxima plataforma. O recorde fica salvo no aparelho.
- **Quatro fases** que se revezam a cada 140 metros, com céu, luz, cores e
  andamento da música próprios: Campo, Pôr do sol, Praia e Noite dos
  vaga-lumes. A troca é suave — as cores vão se transformando aos poucos.
- **Bichinhos** andam de um lado para o outro nas plataformas: encostar de
  lado tira uma vida, mas pular em cima derrota o bichinho e dá dois corações
  (com um quique de volta, estilo Mario).
- **Estrelas douradas** valem cinco corações e soltam brilho.
- Faíscas ao pegar coração, poeira ao pousar, borboletas de dia, vaga-lumes à
  noite, nuvens passando e grama balançando no vento.
- A música e os efeitos são sintetizados na hora pelo próprio navegador
  (Web Audio), sem nenhum arquivo de áudio.
- O cenário tem sombras projetadas de verdade (shadow map), chão com beirada
  de grama, tufos e florzinhas, mato passando em primeiro plano e camadas de
  árvores, morros e montanhas ao fundo, para dar profundidade.
- O 3D usa a biblioteca Three.js, carregada de CDN — precisa de internet na
  primeira abertura.
