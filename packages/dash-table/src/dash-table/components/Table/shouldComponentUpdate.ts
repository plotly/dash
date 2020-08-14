import * as R from 'ramda';
import {isEqual} from 'core/comparer';

const DERIVED_REGEX = /^derived_/;

export default (props: any, nextProps: any, state: any, nextState: any) =>
    R.any(
        key => !DERIVED_REGEX.test(key) && props[key] !== nextProps[key],
        R.keysIn({...props, ...nextProps})
    ) || !isEqual(state, nextState);
