export function APP_STATES(state) {
    const stateList = {
        'STARTED': 'STARTED',
        'HYDRATED': 'HYDRATED'
    }
    if (stateList[state]) return stateList[state];
    else throw new Error (`${state} is not a valid app state.`);
}
