import {LibraryResource} from './libraryTypes';

export default function fetchDist(
    pathnamePrefix: string,
    libraries: string[]
): Promise<LibraryResource[]> {
    return fetch(`${pathnamePrefix}_dash-dist`, {
        body: JSON.stringify(libraries),
        headers: {'Content-Type': 'application/json'},
        method: 'POST'
    }).then(response => response.json());
}
