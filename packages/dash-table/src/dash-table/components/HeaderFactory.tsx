import * as R from 'ramda';
import React from 'react';

import { arrayMap } from 'core/math/arrayZipMap';
import { matrixMap } from 'core/math/matrixZipMap';

import { ControlledTableProps } from 'dash-table/components/Table/props';
import derivedHeaderContent from 'dash-table/derived/header/content';
import getHeaderRows from 'dash-table/derived/header/headerRows';
import getIndices from 'dash-table/derived/header/indices';
import getLabels from 'dash-table/derived/header/labels';
import derivedHeaderOperations from 'dash-table/derived/header/operations';
import derivedHeaderWrappers from 'dash-table/derived/header/wrappers';

export default class HeaderFactory {
    private readonly headerContent = derivedHeaderContent();
    private readonly headerOperations = derivedHeaderOperations();
    private readonly headerWrappers = derivedHeaderWrappers();

    private get props() {
        return this.propsFn();
    }

    constructor(private readonly propsFn: () => ControlledTableProps) {

    }

    public createHeaders() {
        const props = this.props;

        let {
            columns,
            merge_duplicate_headers,
            pagination_mode,
            row_deletable,
            row_selectable,
            setProps,
            sorting,
            sorting_settings,
            sorting_type
        } = props;

        const headerRows = getHeaderRows(columns);

        const labels = getLabels(columns, headerRows);
        const indices = getIndices(columns, labels, merge_duplicate_headers);

        const labelsAndIndices = R.zip(labels, indices);

        const operations = this.headerOperations(
            headerRows,
            row_selectable,
            row_deletable
        );

        const wrappers = this.headerWrappers(
            columns,
            labelsAndIndices,
            merge_duplicate_headers
        );

        const content = this.headerContent(
            columns,
            labelsAndIndices,
            sorting,
            sorting_type,
            sorting_settings,
            pagination_mode,
            setProps,
            props
        );

        const headers = matrixMap(wrappers, content, (w, c) => React.cloneElement(w, { children: [c] }));

        return arrayMap(operations, headers, (o, h) => Array.prototype.concat(o, h));
    }
}