import * as R from 'ramda';
import React from 'react';

import { arrayMap2 } from 'core/math/arrayZipMap';
import { matrixMap2, matrixMap3 } from 'core/math/matrixZipMap';

import { ControlledTableProps } from 'dash-table/components/Table/props';
import derivedHeaderContent from 'dash-table/derived/header/content';
import getHeaderRows from 'dash-table/derived/header/headerRows';
import getIndices from 'dash-table/derived/header/indices';
import getLabels from 'dash-table/derived/header/labels';
import derivedHeaderOperations from 'dash-table/derived/header/operations';
import derivedHeaderWrappers from 'dash-table/derived/header/wrappers';
import { derivedRelevantHeaderStyles } from 'dash-table/derived/style';
import derivedHeaderStyles, { derivedHeaderOpStyles } from 'dash-table/derived/header/wrapperStyles';

import { IEdgesMatrices } from 'dash-table/derived/edges/type';

export default class HeaderFactory {
    private readonly headerContent = derivedHeaderContent();
    private readonly headerOperations = derivedHeaderOperations();
    private readonly headerStyles = derivedHeaderStyles();
    private readonly headerOpStyles = derivedHeaderOpStyles();
    private readonly headerWrappers = derivedHeaderWrappers();
    private readonly relevantStyles = derivedRelevantHeaderStyles();

    private get props() {
        return this.propsFn();
    }

    constructor(private readonly propsFn: () => ControlledTableProps) {

    }

    public createHeaders(headerEdges: IEdgesMatrices | undefined, headerOpEdges: IEdgesMatrices | undefined) {
        const props = this.props;

        const {
            columns,
            merge_duplicate_headers,
            page_action,
            row_deletable,
            row_selectable,
            setProps,
            sort_action,
            sort_by,
            sort_mode,
            style_cell,
            style_cell_conditional,
            style_header,
            style_header_conditional
        } = props;

        const headerRows = getHeaderRows(columns);

        const labels = getLabels(columns, headerRows);
        const indices = getIndices(columns, labels, merge_duplicate_headers);

        const labelsAndIndices = R.zip(labels, indices);

        const relevantStyles = this.relevantStyles(
            style_cell,
            style_header,
            style_cell_conditional,
            style_header_conditional
        );

        const operations = this.headerOperations(
            headerRows,
            row_selectable,
            row_deletable
        );

        const wrapperStyles = this.headerStyles(
            columns,
            headerRows,
            relevantStyles
        );

        const opStyles = this.headerOpStyles(
            headerRows,
            (row_selectable ? 1 : 0) + (row_deletable ? 1 : 0),
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
            sort_action,
            sort_mode,
            sort_by,
            page_action,
            setProps,
            props
        );

        const ops = matrixMap2(
            operations,
            opStyles,
            (o, s, i, j) => React.cloneElement(o, {
                style: R.mergeAll([
                    headerOpEdges && headerOpEdges.getStyle(i, j),
                    s,
                    o.props.style
                ])
            })
        );

        const headers = matrixMap3(
            wrappers,
            wrapperStyles,
            content,
            (w, s, c, i, j) => React.cloneElement(w, {
                children: [c],
                style: R.mergeAll([
                    s,
                    headerEdges && headerEdges.getStyle(i, j)
                ])
            }));

        return arrayMap2(ops, headers, (o, h) => Array.prototype.concat(o, h));
    }
}
