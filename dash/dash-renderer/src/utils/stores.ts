export function getStores() {
    const stores = ((window as any).dash_stores =
        (window as any).dash_stores || []);
    return stores;
}
