import { defineConfig, presetWind4 } from 'unocss';

export default defineConfig({
	presets: [presetWind4({ preflights: { reset: true } })],
	theme: {
		colors: {
			background: '#ffffff',
			surface: '#f3f4f6',
			text: '#111827',
			primary: '#2563eb',
			onPrimary: '#ffffff',
			danger: '#b91c1c'
		}
	}
});
