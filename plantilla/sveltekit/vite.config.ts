import { paraglideVitePlugin } from '@inlang/paraglide-js';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import UnoCSS from 'unocss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	build: { assetsInlineLimit: 0 },
	plugins: [
		paraglideVitePlugin({
			project: './project.inlang',
			outdir: './src/lib/paraglide',
			emitTsDeclarations: true,
			devErrorResponse: true
		}),
		UnoCSS(),
		sveltekit({
			adapter: adapter({ fallback: '200.html' }),
			compilerOptions: { runes: true },
			paths: { relative: false },
			csp: {
				mode: 'hash',
				directives: {
					'default-src': ['self'],
					'script-src': ['self'],
					'style-src-attr': ['unsafe-inline'],
					'object-src': ['none'],
					'base-uri': ['none'],
					'form-action': ['self']
				}
			}
		})
	],
	server: { proxy: { '/api': { target: 'http://localhost:8000', ws: true } } },
	test: { include: ['src/**/*.test.ts'] }
});
