import { defineConfig, presetWind4 } from 'unocss';
import { colors, colorsCss } from './src/lib/colors';

export default defineConfig({
	presets: [presetWind4({ preflights: { reset: true } })],
	theme: { colors },
	preflights: [{ getCSS: () => colorsCss }]
});
