import * as R from 'ramda';

import {
    IUSerInterfaceTooltip,
    ITableStaticTooltips,
    IVirtualizedDerivedData,
    DataTooltips
} from 'dash-table/components/Table/props';
import {ifColumnId, ifRowIndex, ifFilter} from 'dash-table/conditional';
import {ConditionalTooltip, TooltipSyntax} from 'dash-table/tooltips/props';
import {memoizeOne} from 'core/memoizer';

// 2^32-1 the largest value setTimout can take safely
export const MAX_32BITS = 2147483647;

function getSelectedTooltip(
    currentTooltip: IUSerInterfaceTooltip,
    tooltip_data: DataTooltips,
    tooltip_conditional: ConditionalTooltip[],
    tooltip_static: ITableStaticTooltips,
    virtualized: IVirtualizedDerivedData
) {
    if (!currentTooltip) {
        return undefined;
    }

    const {id, row} = currentTooltip;

    if (id === undefined || row === undefined) {
        return undefined;
    }

    const appliedStaticTooltip =
        (tooltip_data &&
            tooltip_data.length > row &&
            tooltip_data[row] &&
            tooltip_data[row][id]) ||
        tooltip_static[id];

    const conditionalTooltips = R.filter(tt => {
        return (
            !tt.if ||
            (ifColumnId(tt.if, id) &&
                ifRowIndex(tt.if, row) &&
                ifFilter(
                    tt.if,
                    virtualized.data[row - virtualized.offset.rows]
                ))
        );
    }, tooltip_conditional);

    return conditionalTooltips.length
        ? conditionalTooltips.slice(-1)[0]
        : appliedStaticTooltip;
}

function convertDelay(delay: number | null) {
    return typeof delay === 'number' ? delay : 0;
}

function convertDuration(duration: number | null) {
    return typeof duration === 'number' ? duration : MAX_32BITS;
}

function getDelay(delay: number | null | undefined, defaultTo: number) {
    return typeof delay === 'number' || delay === null
        ? convertDelay(delay)
        : defaultTo;
}

function getDuration(duration: number | null | undefined, defaultTo: number) {
    return typeof duration === 'number' || duration === null
        ? convertDuration(duration)
        : defaultTo;
}

export default memoizeOne(
    (
        currentTooltip: IUSerInterfaceTooltip,
        tooltip_data: DataTooltips,
        tooltip_conditional: ConditionalTooltip[],
        tooltip_static: ITableStaticTooltips,
        virtualized: IVirtualizedDerivedData,
        defaultDelay: number | null,
        defaultDuration: number | null
    ) => {
        const selectedTooltip = getSelectedTooltip(
            currentTooltip,
            tooltip_data,
            tooltip_conditional,
            tooltip_static,
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

        return {delay, duration, type, value};
    }
);
