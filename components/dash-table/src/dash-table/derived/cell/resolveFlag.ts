import * as R from 'ramda';

export default <T>(tableFlag: T, columnFlag: T | null | undefined): T =>
    R.isNil(columnFlag) ? tableFlag : columnFlag;
