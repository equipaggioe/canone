import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: 'tests',
	webServer: { command: 'pnpm build && pnpm exec vite preview', port: 4173 }
});
