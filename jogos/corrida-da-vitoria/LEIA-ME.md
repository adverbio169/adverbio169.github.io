# Corrida da Vitória

`index.html` é um arquivo só, sem build: abre direto no navegador do
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
