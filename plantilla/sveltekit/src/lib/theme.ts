import { initialTheme, themes, type Theme } from '#lib/colors.js';

const modes = ['system', 'light', 'dark'] as const;

export type Mode = (typeof modes)[number];

/** Reads the mode the user chose, which starts as the system one. */
export function chosenMode(): Mode {
	return pick(modes, localStorage.getItem('mode') ?? 'system');
}

/** Reads the color theme the user chose, which starts as the initial one. */
export function chosenTheme(): Theme {
	return pick(themes, localStorage.getItem('theme') ?? initialTheme);
}

/** Saves the mode the user chose and applies it; «system» follows the system. */
export function chooseMode(mode: Mode): void {
	if (mode === 'system') {
		localStorage.removeItem('mode');
		delete document.documentElement.dataset.mode;
	} else {
		localStorage.setItem('mode', mode);
		document.documentElement.dataset.mode = mode;
	}
}

/** Saves the color theme the user chose and applies it. */
export function chooseTheme(theme: Theme): void {
	localStorage.setItem('theme', theme);
	document.documentElement.dataset.theme = theme;
}

function pick<T extends string>(allowed: readonly T[], value: string): T {
	const found = allowed.find((item) => item === value);
	if (found === undefined) throw new Error(`${value} is not one of ${allowed.join(', ')}`);
	return found;
}
