/** Cached renderer ID for this page instance */
let cachedRendererId: string | null = null;

/**
 * Generate a unique renderer ID for this page instance.
 *
 * Each page load gets a fresh ID to avoid conflicts with stale
 * connections in the SharedWorker after page reloads.
 */
export function getRendererId(): string {
    if (!cachedRendererId) {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            cachedRendererId = crypto.randomUUID();
        } else {
            // Fallback for older browsers
            cachedRendererId = `${Date.now()}-${Math.random()
                .toString(36)
                .slice(2)}`;
        }
    }
    return cachedRendererId;
}
