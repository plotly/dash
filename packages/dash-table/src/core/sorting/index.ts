import * as R from 'ramda';

import { ColumnId } from 'dash-table/components/Table/props';

export interface ISortSetting {
    columnId: ColumnId;
    direction: SortDirection;
}

export enum SortDirection {
    Ascending = 'asc',
    Descending = 'desc',
    None = 'none'
}

export type SortSettings = ISortSetting[];
type IsNullyFn = (value: any) => boolean;
export const defaultIsNully: IsNullyFn = (value: any) => value === undefined || value === null;
export default (data: any[], settings: SortSettings, isNully: IsNullyFn = defaultIsNully): any[] => {
    if (!settings.length) {
        return data;
    }

    return R.sortWith(
        R.map(setting => {
            return setting.direction === SortDirection.Descending ?
                R.comparator((d1: any, d2: any) => {
                    const id = setting.columnId;

                    const prop1 = d1[id];
                    const prop2 = d2[id];

                    if (isNully(prop1)) {
                        return false;
                    } else if (isNully(prop2)) {
                        return true;
                    }

                    return prop1 > prop2;
                }) :
                R.comparator((d1: any, d2: any) => {
                    const id = setting.columnId;

                    const prop1 = d1[id];
                    const prop2 = d2[id];

                    if (isNully(prop1)) {
                        return false;
                    } else if (isNully(prop2)) {
                        return true;
                    }

                    return prop1 < prop2;
                });
        }, settings),
        data
    );
};