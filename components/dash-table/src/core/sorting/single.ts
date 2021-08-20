import Logger from 'core/Logger';
import {SortBy, ISortBy, SortDirection} from 'core/sorting';

export default (sortBy: SortBy, sort: ISortBy): SortBy => {
    Logger.trace('single - update sortBy', sortBy, sort);

    return sort.direction === SortDirection.None ? [] : [sort];
};
