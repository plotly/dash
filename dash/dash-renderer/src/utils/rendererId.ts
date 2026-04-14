/**
 * Generate or retrieve a unique renderer ID for this browser tab/session.
 *
 * The ID is stored in sessionStorage to persist across page reloads
 * but remain unique per tab.
 */
export function getRendererId(): string {
    const key = '__dash_renderer_id';
    let id = sessionStorage.getItem(key);

    if (!id) {
        // Generate a unique ID
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            id = crypto.randomUUID();
        } else {
            // Fallback for older browsers
            id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
        }
        sessionStorage.setItem(key, id);
    }

    return id;
}
