import { env } from "cloudflare:workers";

const PAGE = (site: string) => `<!doctype html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${site}</title>
<style>
  :root { color-scheme: light dark; }
  body {
    margin: 0; min-height: 100vh;
    display: grid; place-items: center;
    font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif;
    background: #fbfaf8; color: #1b1b1a;
  }
  main { max-width: 34rem; padding: 2.5rem 1.5rem; }
  h1 { font-size: 1.9rem; letter-spacing: -0.02em; margin: 0 0 0.75rem; }
  p { margin: 0 0 1rem; color: #444240; }
  a { color: #1b1b1a; }
  @media (prefers-color-scheme: dark) {
    body { background: #14130f; color: #f3f1ec; }
    p { color: #b6b2aa; }
    a { color: #f3f1ec; }
  }
</style>
</head>
<body>
  <main>
    <h1>${site}</h1>
    <p>Esta página está no ar. Serve de domínio de referência para os emails
    que o Sellbird envia, para que nenhuma mensagem aponte para um site que
    não existe.</p>
    <p>Substitui este conteúdo em <code>site/src/index.ts</code>.</p>
  </main>
</body>
</html>
`;

export default {
  fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({
        status: "ok",
        site: env.SITE_NAME,
        time: new Date().toISOString(),
      });
    }

    return new Response(PAGE(env.SITE_NAME), {
      headers: {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "public, max-age=300",
      },
    });
  },
} satisfies ExportedHandler;
