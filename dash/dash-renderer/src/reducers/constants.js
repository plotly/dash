export function getAppState(state) {
    const stateList = {
        STARTED: 'STARTED',
        HYDRATED: 'HYDRATED',
        DESTROYED: 'DESTROYED'
    };
    if (stateList[state]) {
        return stateList[state];
    }
    throw new Error(`${state} is not a valid app state.`);
}
