import {IAnyColumn} from 'dash-table/components/Table/props';

export default (value: any, _options: IAnyColumn) => {
    return {success: true, value};
};
