const initialChange = {
    id: null,
    props: {}
};

function changed(state = initialChange) {
    // This is empty just to initialize the store. Changes
    // are actually recorded in reducer.js so that we can
    // resolve paths to id.
    return state;
}

export default changed;
