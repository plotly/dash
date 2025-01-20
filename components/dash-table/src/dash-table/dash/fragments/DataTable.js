import React, {useMemo} from 'react';

import RealTable from 'dash-table/components/Table';

import genRandomId from 'dash-table/utils/generate';
import isValidProps from '../validate';
import Sanitizer from '../Sanitizer';

import {propTypes, defaultProps} from '../DataTable';

const DataTable = props => {
    const ctx = window.dash_component_api.useDashContext();
    const isLoading = ctx.useLoading(
        loading =>
            loading.property === 'data' ||
            loading.property === '' ||
            loading.property === undefined
    );
    const id = useMemo(() => id || genRandomId('table-'), [id]);
    const sanitizer = useMemo(() => new Sanitizer(), []);

    if (!isValidProps(props)) {
        return <div>Invalid props combination</div>;
    }

    const sanitizedProps = sanitizer.sanitize(props, isLoading);
    return props.id ? (
        <RealTable {...sanitizedProps} />
    ) : (
        <RealTable {...sanitizedProps} id={id} />
    );
};

DataTable.defaultProps = defaultProps;
DataTable.propTypes = propTypes;

export default DataTable;
