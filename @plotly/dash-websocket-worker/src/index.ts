/**
 * Dash WebSocket Worker Package
 *
 * Provides a SharedWorker for WebSocket-based Dash callbacks.
 */

export * from './types';

/**
 * Get the URL for the WebSocket worker script.
 * This should be used to instantiate the SharedWorker.
 *
 * @param baseUrl Base URL where the worker script is served
 * @returns Full URL to the worker script
 */
export function getWorkerUrl(baseUrl: string): string {
    return `${baseUrl}/dash-ws-worker.js`;
}
