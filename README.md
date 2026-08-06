# Comissão Mista do Subsídio dos Militares Estaduais — Roraima

Publicação estática do material do estudo: painel interativo, relatório final,
planilha de conferência e minuta.

## O que é cada arquivo

| arquivo | o que é |
|---|---|
| `index.html` | página de entrada. **É o endereço impresso no QR Code do relatório.** |
| `painel.html` | o painel interativo (arquivo único, autocontido) |
| `Relatorio_Final_Comissao_Subsidio_2026.pdf` | o relatório final |
| `Planilha_Companheira_Subsidio_PMRR.xlsx` | os dados de conferência |

## Regras que não podem ser quebradas

1. **Os nomes do PDF e da planilha não mudam.** Os botões de download dentro do
   painel apontam para eles por link relativo; renomear quebra o download.
2. **O endereço da `index.html` não muda.** Ele está impresso em papel. Se o
   material mudar de servidor, não reimprima nada: abra a `index.html`, preencha
   a variável `DESTINO` com o novo endereço e publique. Quem ler o QR vai parar
   no lugar certo.
3. **Atualizar é substituir arquivo, mantendo o nome.**

## Como atualizar

Substitua o arquivo, faça o commit e o push. O GitHub Pages republica sozinho em
cerca de um minuto.

O `painel.html` é gerado por `Dados_fonte/reconstruir_painel.ps1` no repositório
de trabalho e sai de lá com o nome `Painel .html` — aqui ele é renomeado, e é o
único que pode mudar de nome.

## Nota

O painel não faz chamada a servidor externo: não usa CDN, fonte, script, mapa nem
imagem de fora. Tudo está embutido no próprio arquivo.

## O que a pasta `proposta-ia/` NÃO é

`proposta-ia/` é trabalho separado — uma proposta de painel sobre inteligência
artificial no apoio à decisão, com **dados ilustrativos**. Não faz parte da
publicação da Comissão, não é referenciada pela `index.html` e não entra em nada
do que está impresso. O QR Code do relatório continua levando só ao material da
Comissão. Ver `proposta-ia/README.md`.
