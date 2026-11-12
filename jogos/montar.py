#!/usr/bin/env python3
"""
Monta tv.html e controle.html a partir das partes:

  aviao3d.html  = aviao3d.modelo.html + three.js embutido
  aviao-tv.html = aviao-tv.modelo.html + PeerJS + gerador de QR + núcleo de aviao.html
                  (arquivo único: decide sozinho se é tela, controle ou os dois)
  tv.html       = tv.modelo.html  + PeerJS + gerador de QR + núcleo de aviao.html
  controle.html = controle.modelo.html + PeerJS

O núcleo do jogo (mundo, desenho, regras) vive em aviao.html e é copiado sem
alteração para dentro de tv.html: para mudar o jogo, mude aviao.html e rode
este script. As bibliotecas ficam embutidas para cada página ser um arquivo só.

Uso:  python3 montar.py            (precisa de node_modules com peerjs e
                                     qrcode-generator: npm install peerjs qrcode-generator)
"""
import os, sys, base64

def imagem(nome):
    """A arte da cabine vai EMBUTIDA, pela mesma razão do three.js: o jogo tem
    de abrir sem depender de mais nada. WebP com transparência, ~83 KB — em
    PNG seriam 1,8 MB, e em base64 dentro do HTML, 2,4 MB."""
    cam = os.path.join(AQUI, nome)
    if not os.path.exists(cam):
        print('aviso: falta jogos/%s — o jogo cai na cabine 3D' % nome)
        return ''
    dados = base64.b64encode(open(cam, 'rb').read()).decode('ascii')
    return 'data:image/webp;base64,' + dados

def regras_da_capa():
    """A capa troca de foto conforme o avião escolhido, e a vitória tem a dela.
    Cada regra só é escrita quando a arte existe — `url()` vazio é CSS válido
    e apagaria o fundo; sem a arte, fica o hangar do AD-02."""
    out = []
    for tipo in ('terceiro', 'dragao'):
        nome = 'capa-hangar-%s.webp' % tipo
        if os.path.exists(os.path.join(AQUI, nome)):
            out.append('#capa.%s{--hangar:url(%s)}' % (tipo, imagem(nome)))
    if os.path.exists(os.path.join(AQUI, 'capa-vitoria.webp')):
        out.append('#capa.vitoria{--hangar:url(%s);justify-content:flex-end;'
                   'background:linear-gradient(270deg,rgba(4,8,16,.74) 0,rgba(4,8,16,.45) 30%%,rgba(4,8,16,0) 46%%),'
                   'var(--hangar) 30%% 50%%/cover no-repeat,#0b1020}' % imagem('capa-vitoria.webp'))
    return '\n  '.join(out) or '/* (sem artes extras: tudo no hangar do AD-02) */'

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

um = open('aviao-tv.modelo.html', encoding='utf-8').read()
um = um.replace('__PEERJS__', seguro(peer)).replace('__QRCODE__', seguro(qr)).replace('__NUCLEO__', cab + nucleo)
open('aviao-tv.html', 'w', encoding='utf-8').write(um)

tv = open('tv.modelo.html', encoding='utf-8').read()
tv = tv.replace('__PEERJS__', seguro(peer)).replace('__QRCODE__', seguro(qr)).replace('__NUCLEO__', cab + nucleo)
open('tv.html', 'w', encoding='utf-8').write(tv)

ct = open('controle.modelo.html', encoding='utf-8').read().replace('__PEERJS__', seguro(peer))
open('controle.html', 'w', encoding='utf-8').write(ct)

# --- a versão com three.js -------------------------------------------------
# A biblioteca vai EMBUTIDA, e não por link de CDN, pelo mesmo motivo de sempre:
# o jogo tem que abrir no navegador da TV sem depender de mais nada. São ~190 KB
# pela rede depois de comprimido.
tres_cam = os.path.join(AQUI, 'three.min.js')
if os.path.exists(tres_cam):
    tres = open(tres_cam, encoding='utf-8').read()
    t3 = open('aviao3d.modelo.html', encoding='utf-8').read()
    t3 = (t3.replace('<script>/* THREE */</script>', '<script>' + seguro(tres) + '</script>')
            .replace('__PEERJS__', seguro(peer))
            .replace('__QRCODE__', seguro(qr))
            .replace('__CABINE_LUCAS__', imagem('cabine-lucas.webp'))
            .replace('__CABINE_LUCAS_MANCHE__', imagem('cabine-lucas-manche.webp'))
            .replace('__CABINE_LUCAS_MANETES__', imagem('cabine-lucas-manetes.webp'))
            .replace('__CABINE_LUCAS_FLAPE__', imagem('cabine-lucas-flape.webp'))
            .replace('__CAPA_HANGAR_CACA__', imagem('capa-hangar-caca.webp'))
            .replace('/*__REGRAS_DA_CAPA__*/', regras_da_capa())
            .replace('__CABINE_CACA__', imagem('cabine-caca.webp'))
            .replace('__CABINE_CACA_TREM__', imagem('cabine-caca-trem.webp'))
            .replace('__CABINE_CACA_MANETE_A__', imagem('cabine-caca-manete-a.webp'))
            .replace('__CABINE_CACA_MANETE_B__', imagem('cabine-caca-manete-b.webp'))
            .replace('__CABINE_CACA_FLAPE__', imagem('cabine-caca-flape.webp'))
            .replace('__CABINE_CACA_MANCHE__', imagem('cabine-caca-manche.webp')))
    open('aviao3d.html', 'w', encoding='utf-8').write(t3)
    print('aviao3d.html: %d KB   (three.js embutido: %d KB)' % (len(t3)//1024, len(tres)//1024))
else:
    print('aviao3d.html: pulado (falta jogos/three.min.js)')

print('aviao-tv.html: %d KB   tv.html: %d KB   controle.html: %d KB   (núcleo: linhas %d-%d de aviao.html)'
      % (len(um)//1024, len(tv)//1024, len(ct)//1024, i2+1, i4))
