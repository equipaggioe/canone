import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import UnoCSS from 'unocss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		UnoCSS(),
		sveltekit({
			adapter: adapter({ fallback: '200.html' }),
			csp: {
				mode: 'hash',
				directives: { 'default-src': ['self'] }
			}
		})
	]
});
