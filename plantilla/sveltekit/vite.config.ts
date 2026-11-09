import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import UnoCSS from 'unocss/vite';
import { defineConfig } from 'vite';

export default defineConfig(({ command }) => ({
	build: { assetsInlineLimit: 0 },
	plugins: [
		UnoCSS(),
		sveltekit({
			adapter: adapter({ fallback: '200.html' }),
			csp: {
				mode: 'hash',
				directives: {
					'default-src': ['self'],
					'script-src': command === 'build' ? ['strict-dynamic'] : ['self'],
					'style-src-attr': ['unsafe-inline'],
					'object-src': ['none'],
					'base-uri': ['none'],
					'form-action': ['self']
				}
			}
		})
	],
	server: { proxy: { '/api': { target: 'http://localhost:8000', ws: true } } }
}));
