const pendingCallbacks = (state = [], action) => {
    switch (action.type) {
        case 'SET_PENDING_CALLBACKS':
            return action.payload;

        default:
            return state;
    }
};

export default pendingCallbacks;
