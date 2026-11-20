// plataformas/sveltekit.md, «Estilos»: the mode and the color theme the user chose, before the
// first paint.
for (const key of ['mode', 'theme']) {
	const value = localStorage.getItem(key);
	if (value !== null) document.documentElement.dataset[key] = value;
}
