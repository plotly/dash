import * as R from 'ramda';
import React from 'react';

import { arrayMap } from 'core/math/arrayZipMap';
import { matrixMap3 } from 'core/math/matrixZipMap';

import { ControlledTableProps } from 'dash-table/components/Table/props';
import derivedHeaderContent from 'dash-table/derived/header/content';
import getHeaderRows from 'dash-table/derived/header/headerRows';
import getIndices from 'dash-table/derived/header/indices';
import getLabels from 'dash-table/derived/header/labels';
import derivedHeaderOperations from 'dash-table/derived/header/operations';
import derivedHeaderWrappers from 'dash-table/derived/header/wrappers';
import { derivedRelevantHeaderStyles } from 'dash-table/derived/style';
import derivedHeaderStyles from 'dash-table/derived/header/wrapperStyles';

export default class HeaderFactory {
    private readonly headerContent = derivedHeaderContent();
    private readonly headerOperations = derivedHeaderOperations();
    private readonly headerWrappers = derivedHeaderWrappers();

    private get props() {
        return this.propsFn();
    }

    constructor(
        private readonly propsFn: () => ControlledTableProps,
        private readonly headerStyles = derivedHeaderStyles(),
        private readonly relevantStyles = derivedRelevantHeaderStyles()
    ) { }

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
            sorting_type,
            style_cells_and_headers,
            style_headers
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

        const relevantStyles = this.relevantStyles(style_cells_and_headers, style_headers);

        const wrapperStyles = this.headerStyles(
            columns,
            headerRows,
            relevantStyles
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

        const headers = matrixMap3(
            wrappers,
            wrapperStyles,
            content,
            (w, s, c) => React.cloneElement(w, { children: [c], style: s }));

        return arrayMap(operations, headers, (o, h) => Array.prototype.concat(o, h));
    }
}