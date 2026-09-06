# O desenho da Vitória

Vídeo animado feito a partir do desenho da Vitória.

- `desenho-da-vitoria.mp4` — o vídeo (900x1120, 30 fps, ~21 s, sem áudio)
- `capa.png` — imagem de capa
- `index.html` — página simples que toca o vídeo
- `gerar_video.py` — script que gera tudo

O desenho original (círculo, quadradinhos dos olhos, retângulos, triângulo
vermelho do chapéu) foi remontado em vetores dentro do script. A animação tem
três partes: o título aparecendo, o desenho sendo feito traço a traço, e o
personagem ganhando vida (pulinho, braços acenando, olhos piscando e corações).

## Como gerar de novo

```bash
pip install pillow imageio-ffmpeg
python3 gerar_video.py            # gera desenho-da-vitoria.mp4 e capa.png
```

Para mudar o desenho, edite as coordenadas em `PARTS` no script; para mudar
o ritmo, os tempos `dur` de cada parte e as constantes `T_*`.
