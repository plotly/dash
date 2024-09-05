const initialGraph = {};

const graphs = (state = initialGraph, action) => {
    if (action.type === 'SET_GRAPHS') {
        return action.payload;
    }
    return state;
};

export default graphs;
