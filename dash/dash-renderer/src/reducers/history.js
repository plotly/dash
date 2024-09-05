const initialHistory = {
    past: [],
    present: {},
    future: []
};

function history(state = initialHistory, action) {
    switch (action.type) {
        case 'UNDO': {
            const {past, present, future} = state;
            const previous = past[past.length - 1];
            const newPast = past.slice(0, past.length - 1);
            return {
                past: newPast,
                present: previous,
                future: [present, ...future]
            };
        }

        case 'REDO': {
            const {past, present, future} = state;
            const next = future[0];
            const newFuture = future.slice(1);
            return {
                past: [...past, present],
                present: next,
                future: newFuture
            };
        }

        case 'REVERT': {
            const {past, future} = state;
            const previous = past[past.length - 1];
            const newPast = past.slice(0, past.length - 1);
            return {
                past: newPast,
                present: previous,
                future: [...future]
            };
        }

        default: {
            return state;
        }
    }
}

export default history;
