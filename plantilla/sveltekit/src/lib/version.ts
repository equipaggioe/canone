import { beforeNavigate } from '$app/navigation';
import { updated } from '$app/state';

/**
 * Turn the next navigation into a full page load once a new build is out.
 *
 * SvelteKit reloads on its own only when a navigation fails, so an open tab or the PWA would
 * keep running the old build against the new server. Call it from the root +layout.svelte.
 */
export function reloadOnNewVersion(): void {
	beforeNavigate(({ willUnload, to }) => {
		if (updated.current && !willUnload && to?.url) {
			location.href = to.url.href;
		}
	});
}
