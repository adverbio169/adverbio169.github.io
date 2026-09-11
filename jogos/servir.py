#!/usr/bin/env python3
"""
SERVIDOR LOCAL PARA TESTAR OS JOGOS, SEM PUBLICAR NADA.

Por que existe: o sensor de inclinação do celular só liga se a página vier de um
endereço seguro (https). Um arquivo baixado no celular não serve, e um servidor
comum (http) também não. Este script serve esta pasta por https, na sua rede.

COMO USAR
  1. Abra o terminal NESTA pasta e rode:      python3 servir.py
     (no Windows costuma ser:                 py servir.py)
  2. Ele imprime um endereço, tipo  https://192.168.0.15:8443/aviao-tv.html
  3. No computador, abra esse endereço: ele vira a TELA do jogo e mostra um código.
  4. No celular (mesma WiFi), abra o MESMO endereço. Vai aparecer um aviso de
     "conexão não é particular" — é esperado, o certificado é caseiro. Toque em
     Avançado -> Continuar. Depois escolha "Sou o controle" e digite o código.

O aviso de certificado é o preço de não publicar: o navegador não conhece quem
assinou. Nada sai da sua rede.

Para parar: Ctrl+C.
"""
import http.server, socketserver, ssl, socket, os, sys, tempfile

PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
AQUI = os.path.dirname(os.path.abspath(__file__))

CERT = """-----BEGIN CERTIFICATE-----
MIIDKTCCAhGgAwIBAgIUJTiQDEPeXUErM1gPdj/3myKPXhYwDQYJKoZIhvcNAQEL
BQAwFjEUMBIGA1UEAwwLYXZpYW8tbG9jYWwwHhcNMjYwOTExMjAwNzIwWhcNMzYw
OTA4MjAwNzIwWjAWMRQwEgYDVQQDDAthdmlhby1sb2NhbDCCASIwDQYJKoZIhvcN
AQEBBQADggEPADCCAQoCggEBAMqgpPdPuCzBxzSz6G8NAH2jHot7kH1b3LVXbWwG
8xs8R3IpreZLpC1i7GPjcUZ796w4umF1oe0+EYr/Vyn+UnA/BBt68i6n2NiTlFpc
cvoSv9E7zJZ/a0VfgIxm21anI67XEBxoHwHkJ6AbsNRK0iRGtFi8gMiazlR4IlAp
uzGHsFdMRYugsi5LxCU2FU7Ln3E9inzzae+nHiWLrTgSRBxCkUIT1QEAyYWUdxZE
Qb9VcZr6bFphDesLwwuMbZfORyhbqpF6fC0IBXt1K4wjveLUR3Q29EC9fZVuL0EP
NmxR/M7s6RXSak6+gBNtR/AfS0xctlm9sNKDrZ1lLo/weYsCAwEAAaNvMG0wHQYD
VR0OBBYEFN2ZzO3pwAiVSp9ddWRX2Tcyjy1xMB8GA1UdIwQYMBaAFN2ZzO3pwAiV
Sp9ddWRX2Tcyjy1xMA8GA1UdEwEB/wQFMAMBAf8wGgYDVR0RBBMwEYIJbG9jYWxo
b3N0hwR/AAABMA0GCSqGSIb3DQEBCwUAA4IBAQCjs+w7Y4tMxEGnRRFi3j+9lENp
o1zR6Balp5kx4C0zHsqAhQTgYemVEucRsO7ozXz82rNcYDj+tgtTYgG6G7KafKm+
1BdA7liYjHYfVPUvWGZmFIjqWaXOx2X8WfP8ddpZBD4tMkWSyM/JNLAWmaUjDf45
qlogwzAGsUfH0tEh7xp960gQ2Pu5VRGosFJ5sm4xEP7RfQbcwT5Af0KPb8J7IkZS
VM7SOyynrrAKO343Rpanx/o3S0ydOL18Ohw5odmlPYwlcOK01UB9uJaGoUJwPQ/N
AK7PrWquXBUELdL6dDiXWUUND+ctz0pz6fzVpvF1o3vZQbr/PW56Qlu8NVKG
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDKoKT3T7gswcc0
s+hvDQB9ox6Le5B9W9y1V21sBvMbPEdyKa3mS6QtYuxj43FGe/esOLphdaHtPhGK
/1cp/lJwPwQbevIup9jYk5RaXHL6Er/RO8yWf2tFX4CMZttWpyOu1xAcaB8B5Ceg
G7DUStIkRrRYvIDIms5UeCJQKbsxh7BXTEWLoLIuS8QlNhVOy59xPYp882nvpx4l
i604EkQcQpFCE9UBAMmFlHcWREG/VXGa+mxaYQ3rC8MLjG2XzkcoW6qRenwtCAV7
dSuMI73i1Ed0NvRAvX2Vbi9BDzZsUfzO7OkV0mpOvoATbUfwH0tMXLZZvbDSg62d
ZS6P8HmLAgMBAAECgf88mkbewgGgclSAEOh8Tk2bikeP56C+ZhkLvUT0Rg7FHxeU
no1KwpkcLS1CKlVp+xAyA03/gtFaTi2KoMLgCCgGSCf63ORN7dR+aYMgDA8CAIiA
aa8CqW64v+AQhG6eHj0N4zOyoKTHnzmyOlGxcRW+GSM9zWeD7XO3ensNB0wPFNMr
pzH77wMBGKIC6r+h0aApULjYVC00FqZTkRin1tdfFdgSSPlax3z/7MNawc+8jlba
iIju0MPHAKIboRUZhnkxoSy8H3zFYLPmq6uYNTTRu8sqmgfzq58PZnAha7gqkSFB
E0s7kWvTkyFkrxp0jQLjuSd91/N4tMTPUKcr+40CgYEA6+99tZByFMyIt648Ygaq
CruEniQ18R8vwV0ykuFASZyUIAcpnJcgPbFD/kcf/Mlmaxu+OKNvXV0l6AtfH6m5
TF7dPhW5MMcryHe2Z49OCyaetM6+rELeBBBifZzS9XLzXUTv5ut0BRmCXGf+IJR6
1QYgHB0VYK3JdvBZaDUHwx0CgYEA29wC1dje1KVGGdAxAHa29BDAVZOG5piGHm6v
9SbHLZ5aPv/cXCrz6BGRWTn0WSeGrYcg0t3IdhEvCuOo7zZjFZUaOVXepJPk6GI7
dk/wG9pj5I/dQ1rRL/jhrvm+XxvadOUGbrDK/XdzHd6nHNyhrRWHdjBnwKhFDoAv
kB9/pscCgYEAk9T0B5gCY1XlNHJQE3vpf+APMKevxO2tlpM25SGOjpE1nvvd7ugi
o4U2/VTDjjkDm4k+n26IkQ+UeNjnOYe3O0sVhZlG+HFT1cBs4mbAl+wS9We1wWoE
grdhfyOMa48jPgW77A0MHUXmkM/4Q6HFdUTpSbRPeMxrt8LRwqG3w2ECgYAzYLec
56AzCyhVkexRkmxwnpWDqgUFUDFPXUhrPpOfGnk2ba4+L59t5OUVd9CdIPp9BK3r
+P4GcT+QCOGKfSgse/pz2Zg8137Pu1zv6gBPUfq0B9aKDegCkOOUczJEoYqsdHTL
Wy8kikxxd32P5hM2Emjkeq1UPT5eBCCZSnMXMwKBgQCg9MYTczTN8eHSrTjagz/j
MYyti5GwHgUoaPvbgjX+q15atQRfHvglm+VD+Y2/BYEEW8LtrJTLfQL0+ga+LEk8
52mjgTS+1t9J++mPeE3XuqvnZTleTGVORr8enp67ZTNdIVG1yVFsLEJJhoWlUuoZ
9eD5yHC/uzaQ481jSpWEzw==
-----END PRIVATE KEY-----"""

def ips_da_rede():
    ips = []
    try:                                  # o truque do socket UDP descobre o IP "de saída"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80)); ips.append(s.getsockname()[0]); s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith('127.') and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    return ips

class Silencioso(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=AQUI, **k)
    def log_message(self, *a): pass       # sem poluir o terminal a cada quadro

pem = os.path.join(tempfile.gettempdir(), 'aviao-local.pem')
with open(pem, 'w') as f: f.write(CERT)
os.chmod(pem, 0o600)

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(pem)

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('0.0.0.0', PORTA), Silencioso) as srv:
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    print()
    print('  Servindo ' + AQUI)
    print('  Abra ESTE endereço no computador E no celular (mesma WiFi):')
    print()
    for ip in ips_da_rede() or ['SEU-IP']:
        print('      https://%s:%d/aviao-tv.html' % (ip, PORTA))
    print()
    print('  O celular vai avisar que a conexão "não é particular".')
    print('  Toque em Avançado -> Continuar. É o certificado caseiro, e é esperado.')
    print()
    print('  Ctrl+C para parar.')
    print()
    try: srv.serve_forever()
    except KeyboardInterrupt: print('\n  Parado.')
