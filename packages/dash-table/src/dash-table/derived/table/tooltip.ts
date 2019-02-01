import * as R from 'ramda';

import { IUSerInterfaceTooltip, ITableTooltips, ITableStaticTooltips, IVirtualizedDerivedData } from 'dash-table/components/Table/props';
import { ifColumnId, ifRowIndex, ifFilter } from 'dash-table/conditional';
import { ConditionalTooltip, TooltipSyntax } from 'dash-table/tooltips/props';
import { memoizeOne } from 'core/memoizer';

// 2^32-1 the largest value setTimout can take safely
export const MAX_32BITS = 2147483647;

function getSelectedTooltip(
    tooltip: IUSerInterfaceTooltip,
    tooltips: ITableTooltips | undefined,
    column_conditional_tooltips: ConditionalTooltip[],
    column_static_tooltip: ITableStaticTooltips,
    virtualized: IVirtualizedDerivedData
) {
    if (!tooltip) {
        return undefined;
    }

    const { id, row } = tooltip;

    if (id === undefined || row === undefined) {
        return undefined;
    }

    const legacyTooltip = tooltips &&
        tooltips[id] &&
        (
            tooltips[id].length > row ?
                tooltips[id][row] :
                null
        );

    const staticTooltip = column_static_tooltip[id];

    const conditionalTooltips = R.filter(tt => {
        return !tt.if ||
            (
                ifColumnId(tt.if, id) &&
                ifRowIndex(tt.if, row) &&
                ifFilter(tt.if, virtualized.data[row - virtualized.offset.rows])
            );
    }, column_conditional_tooltips);

    return conditionalTooltips.length ?
        conditionalTooltips.slice(-1)[0] :
        legacyTooltip || staticTooltip;
}

function convertDelay(delay: number | null) {
    return typeof delay === 'number' ?
        delay :
        0;
}

function convertDuration(duration: number | null) {
    return typeof duration === 'number' ?
        duration :
        MAX_32BITS;
}

function getDelay(delay: number | null | undefined, defaultTo: number) {
    return typeof delay === 'number' || delay === null ?
        convertDelay(delay) :
        defaultTo;
}

function getDuration(duration: number | null | undefined, defaultTo: number) {
    return typeof duration === 'number' || duration === null ?
        convertDuration(duration) :
        defaultTo;
}

export default memoizeOne((
    tooltip: IUSerInterfaceTooltip,
    tooltips: ITableTooltips | undefined,
    column_conditional_tooltips: ConditionalTooltip[],
    column_static_tooltip: ITableStaticTooltips,
    virtualized: IVirtualizedDerivedData,
    defaultDelay: number | null,
    defaultDuration: number | null
) => {
    const selectedTooltip = getSelectedTooltip(
        tooltip,
        tooltips,
        column_conditional_tooltips,
        column_static_tooltip,
        virtualized
    );

    let delay = convertDelay(defaultDelay) as number;
    let duration = convertDuration(defaultDuration) as number;

    let type: TooltipSyntax = TooltipSyntax.Text;
    let value: string | undefined;

    if (selectedTooltip) {
        if (typeof selectedTooltip === 'string') {
            value = selectedTooltip;
        } else {
            delay = getDelay(selectedTooltip.delay, delay);
            duration = getDuration(selectedTooltip.duration, duration);
            type = selectedTooltip.type || TooltipSyntax.Text;
            value = selectedTooltip.value;
        }
    }

    return { delay, duration, type, value };
});