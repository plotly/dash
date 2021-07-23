import * as R from 'ramda';

import Logger from 'core/Logger';
import {SortBy, ISortBy, SortDirection} from 'core/sorting';

export default (sortBy: SortBy, sort: ISortBy): SortBy => {
    Logger.trace('multi - update sortBy', sortBy, sort);

    sortBy = R.clone(sortBy);

    if (sort.direction === SortDirection.None) {
        const currentIndex = R.findIndex(
            s => s.column_id === sort.column_id,
            sortBy
        );

        if (currentIndex !== -1) {
            sortBy.splice(currentIndex, 1);
        }
    } else {
        const current = R.find(s => s.column_id === sort.column_id, sortBy);

        if (current) {
            current.direction = sort.direction;
        } else {
            sortBy.push(sort);
        }
    }

    return sortBy;
};
