import {getAction} from '../actions/constants';

const initialRendered: any[] = [];

type RenderedState = any[];
type RenderedAction = {
    payload: any[];
    type: string;
};

export default function renderedReducer(
    state: RenderedState = initialRendered,
    action: RenderedAction
) {
    if (action.type === getAction('SET_RENDERED')) {
        return action.payload;
    }
    return state;
}
