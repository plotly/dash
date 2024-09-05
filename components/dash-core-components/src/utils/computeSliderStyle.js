import {memoizeWith, identity, includes} from 'ramda';

export default () => {
    return memoizeWith(identity, (vertical, verticalHeight, tooltip) => {
        const style = {
            padding: '25px',
        };

        if (vertical) {
            style.height = verticalHeight + 'px';

            if (
                !tooltip ||
                !tooltip.always_visible ||
                !includes(tooltip.placement, [
                    'left',
                    'topRight',
                    'bottomRight',
                ])
            ) {
                style.paddingLeft = '0px';
            }
        } else {
            if (
                !tooltip ||
                !tooltip.always_visible ||
                !includes(tooltip.placement, ['top', 'topLeft', 'topRight'])
            ) {
                style.paddingTop = '0px';
            }
        }

        return style;
    });
};
