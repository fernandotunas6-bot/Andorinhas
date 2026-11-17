import { bindings, defineConfig } from "cf/config";
import * as entrypoint from "./src/index.ts" with { type: "cf-worker" };

export default defineConfig({
	worker: {
		name: "andorinhas",
		compatibilityDate: "2026-11-17",
		entrypoint,

		// The free *.workers.dev subdomain. After the first deploy the Worker
		// answers on https://andorinhas.<your-subdomain>.workers.dev
		workersDev: true,

		// A .dev domain you own and have added as a zone on this Cloudflare
		// account. Uncomment once the zone exists, then redeploy.
		// domains: ["andorinhas.dev", "www.andorinhas.dev"],

		env: {
			SITE_NAME: bindings.text("Andorinhas"),
		},
	},
});
