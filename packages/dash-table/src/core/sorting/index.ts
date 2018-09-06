import * as R from 'ramda';

export interface ISortSetting {
    columnId: string | number;
    direction: SortDirection;
}

export enum SortDirection {
    Ascending = 'asc',
    Descending = 'desc',
    None = 'none'
}

export type SortSettings = ISortSetting[];

export default (dataframe: any[], settings: SortSettings): any[] => {
    if (!settings.length) {
        return dataframe;
    }

    return R.sortWith(
        R.map(setting => {
            return setting.direction === SortDirection.Descending ?
                R.comparator((d1: any, d2: any) => {
                    const id = setting.columnId;

                    const prop1 = d1[id];
                    const prop2 = d2[id];

                    if (prop1 === undefined || prop1 === null) {
                        return false;
                    } else if (prop2 === undefined || prop2 === null) {
                        return true;
                    }

                    return prop1 > prop2;
                }) :
                R.comparator((d1: any, d2: any) => {
                    const id = setting.columnId;

                    const prop1 = d1[id];
                    const prop2 = d2[id];

                    if (prop1 === undefined || prop1 === null) {
                        return false;
                    } else if (prop2 === undefined || prop2 === null) {
                        return true;
                    }

                    return prop1 < prop2;
                });
        }, settings),
        dataframe
    );
};