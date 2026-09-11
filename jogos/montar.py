#!/usr/bin/env python3
"""
Monta tv.html e controle.html a partir das partes:

  tv.html       = tv.modelo.html  + PeerJS + gerador de QR + núcleo de aviao.html
  controle.html = controle.modelo.html + PeerJS

O núcleo do jogo (mundo, desenho, regras) vive em aviao.html e é copiado sem
alteração para dentro de tv.html: para mudar o jogo, mude aviao.html e rode
este script. As bibliotecas ficam embutidas para cada página ser um arquivo só.

Uso:  python3 montar.py            (precisa de node_modules com peerjs e
                                     qrcode-generator: npm install peerjs qrcode-generator)
"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)

def acha_modulo(rel):
    pastas = [os.path.join(AQUI, 'node_modules'), os.path.join(os.path.dirname(AQUI), 'node_modules')]
    if os.environ.get('NODE_MODULES'):          # NODE_MODULES=/caminho/para/node_modules
        pastas.insert(0, os.environ['NODE_MODULES'])
    for pasta in pastas:
        cand = os.path.join(pasta, rel)
        if os.path.exists(cand):
            return cand
    sys.exit('não achei node_modules/%s — rode: npm install peerjs qrcode-generator' % rel)

peer = open(acha_modulo('peerjs/dist/peerjs.min.js'), encoding='utf-8').read()
qr   = open(acha_modulo('qrcode-generator/qrcode.js'), encoding='utf-8').read()
av   = open('aviao.html', encoding='utf-8').read().split('\n')

i2 = next(i for i, l in enumerate(av) if 'PARTE 2 — O MUNDO' in l) - 1
i4 = next(i for i, l in enumerate(av) if 'ENTRADA DO USUÁRIO' in l) - 1
nucleo = '\n'.join(av[i2:i4])
assert 'function quadro' in nucleo and 'function fim' not in nucleo, 'o núcleo de aviao.html mudou de lugar'

cab = ('/* ---------------------------------------------------------------------------\n'
       '   NÚCLEO DO JOGO — copiado de aviao.html, sem alteração. Para mudar o jogo,\n'
       '   mude lá e rode jogos/montar.py, que refaz este arquivo.\n'
       '   --------------------------------------------------------------------------- */\n')

def seguro(js):  # um "</script>" dentro da biblioteca fecharia o bloco antes da hora
    return js.replace('</script', '<\\/script')

tv = open('tv.modelo.html', encoding='utf-8').read()
tv = tv.replace('__PEERJS__', seguro(peer)).replace('__QRCODE__', seguro(qr)).replace('__NUCLEO__', cab + nucleo)
open('tv.html', 'w', encoding='utf-8').write(tv)

ct = open('controle.modelo.html', encoding='utf-8').read().replace('__PEERJS__', seguro(peer))
open('controle.html', 'w', encoding='utf-8').write(ct)

print('tv.html: %d KB   controle.html: %d KB   (núcleo: linhas %d-%d de aviao.html)' % (len(tv)//1024, len(ct)//1024, i2+1, i4))
