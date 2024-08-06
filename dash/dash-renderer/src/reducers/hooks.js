const customHooks = (
    state = {
        layout_pre: null,
        layout_post: null,
        request_pre: null,
        request_post: null,
        callback_resolved: null,
        request_refresh_jwt: null,
        bear: false
    },
    action
) => {
    switch (action.type) {
        case 'SET_HOOKS':
            return action.payload;
        default:
            return state;
    }
};

export default customHooks;
