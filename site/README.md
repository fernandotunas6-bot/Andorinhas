# site — Worker da Cloudflare

Página pública servida por um Worker da Cloudflare. Existe para que os emails
que o Sellbird envia tenham um domínio próprio para onde apontar, em vez de
ligarem para um site que não existe.

Construído com o CLI `cf` (beta). A configuração está em
[`cloudflare.config.ts`](cloudflare.config.ts) e o código em
[`src/index.ts`](src/index.ts). Rotas: `/` devolve a página, `/health` devolve
JSON com o estado.

## Atenção: não compila neste Mac

O runtime da Cloudflare (`workerd`) exige **macOS 13.5 ou superior**. Esta
máquina corre o macOS 12.6, logo `npm test`, `cf build`, `cf dev` e `cf deploy`
falham localmente, com a mensagem `Unsupported macOS version`.

Por isso o deploy vive no GitHub Actions, em
[`.github/workflows/cloudflare.yml`](../.github/workflows/cloudflare.yml), que
corre em Linux. Para trabalhar localmente seria preciso atualizar o macOS ou
usar um devcontainer com Linux (glibc 2.35+).

## Pôr no ar

1. Criar um token de API em **Cloudflare → My Profile → API Tokens**, com o
   modelo *Edit Cloudflare Workers*. Dá só as permissões de que o deploy
   precisa.
2. Copiar o **Account ID** do painel da Cloudflare.
3. No repositório, em **Settings → Secrets and variables → Actions**, criar:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
4. Fazer push para `main`, ou correr o workflow à mão em **Actions → Cloudflare
   → Run workflow**.

Sem os dois segredos o workflow continua a correr os testes, a build e a
verificação, e salta apenas o envio.

## O domínio

Depois do primeiro deploy o Worker responde no subdomínio gratuito
`*.workers.dev`:

```
https://andorinhas.<o-teu-subdominio>.workers.dev
```

Esse subdomínio vem incluído e não custa nada.

Um domínio `.dev` de verdade, como `andorinhas.dev`, é outra coisa: tem de ser
**comprado** num registrador, e o `.dev` obriga a HTTPS, porque o TLD está na
lista HSTS pré-carregada dos browsers. Depois de o comprar e de o adicionar
como zona nesta conta da Cloudflare, descomenta a linha `domains` em
[`cloudflare.config.ts`](cloudflare.config.ts) e faz push outra vez.

## Ligar ao Sellbird

Com o domínio no ar, põe-no em `channels.email.link_domains` no
`sellbird.yaml`. O Sellbird retém qualquer email que ligue para um domínio que
não seja o teu, e essa lista é a que ele aceita.
