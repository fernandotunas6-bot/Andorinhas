import { SELF } from "cloudflare:test";
import { expect, it } from "vitest";

it("serves the landing page", async () => {
	const response = await SELF.fetch("https://example.com/");
	expect(response.status).toBe(200);
	expect(response.headers.get("content-type")).toContain("text/html");
	expect(await response.text()).toContain("Andorinhas");
});

it("answers the health check", async () => {
	const response = await SELF.fetch("https://example.com/health");
	expect(response.status).toBe(200);
	expect(await response.json()).toMatchObject({ status: "ok", site: "Andorinhas" });
});
