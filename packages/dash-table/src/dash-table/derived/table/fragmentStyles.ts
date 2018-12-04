import * as R from 'ramda';
import { CSSProperties } from 'react';

import {
    IUserInterfaceCell,
    IUserInterfaceViewport,
    IDerivedData,
    IViewportPadding
} from 'dash-table/components/Table/props';

export default (
    virtualization: boolean,
    uiCell: IUserInterfaceCell | undefined,
    uiHeaders: IUserInterfaceCell[] | undefined,
    uiViewport: IUserInterfaceViewport | undefined,
    viewport: IDerivedData,
    rowPadding: IViewportPadding,
    scrollbarWidth: number
): { fragment?: CSSProperties, cell?: CSSProperties}[][] => {
    if (!virtualization || !uiCell || !uiViewport) {
        return [
            [{}, {}],
            [{}, {}]
        ];
    }

    const fullHeight = uiCell.height * viewport.data.length;
    const virtualizedHeight = (Math.floor(uiViewport.scrollTop / uiCell.height) - rowPadding.before) * uiCell.height;
    const headersHeight = R.sum(R.map(h => h.height, uiHeaders || []));

    const marginRight = scrollbarWidth;
    const marginTop = virtualization && uiViewport && uiCell ? Math.max(virtualizedHeight - headersHeight, 0) : 0;
    const height = Math.max(fullHeight - marginTop, 0);

    return [
        [{}, { fragment: { marginRight } }],
        [{ cell: { marginTop } }, { fragment: { height, marginTop } }]
    ];
};