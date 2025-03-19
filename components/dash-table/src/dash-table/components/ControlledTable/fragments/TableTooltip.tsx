import React, {Component, createRef} from 'react';

import Tooltip, {ITooltipProps, Arrow} from 'dash-table/components/Tooltip';
import {getPositionalParent} from 'dash-table/components/tooltipHelper';

import {isEqual} from 'core/comparer';

interface IState {
    arrow?: Arrow;
    cell?: any;
}

export default class TableTooltip extends Component<
    Omit<ITooltipProps, 'divRef'>,
    IState
> {
    tooltipRef: React.RefObject<HTMLElement>;
    constructor(props: ITooltipProps) {
        super(props);

        this.tooltipRef = createRef();

        this.state = {
            arrow: Arrow.Bottom
        };
    }

    updateBounds = (cell: any) => {
        this.setState({cell});
    };

    shouldComponentUpdate(nextProps: ITooltipProps, nextState: IState) {
        this.adjustPosition();
        return (
            !isEqual(this.props, nextProps) || !isEqual(this.state, nextState)
        );
    }

    componentDidUpdate() {
        this.adjustPosition();
    }

    render() {
        const {arrow} = this.state;

        return (
            <Tooltip
                key='tooltip'
                divRef={this.tooltipRef}
                arrow={arrow}
                {...this.props}
            />
        );
    }

    private adjustPosition() {
        const {cell} = this.state;

        const el = this.tooltipRef.current;

        const positionalParent = getPositionalParent(el);

        if (!positionalParent || !cell || !el) {
            return;
        }

        const positionalBounds = positionalParent.getBoundingClientRect();
        const parentBounds = cell.getBoundingClientRect();

        const {clientWidth: elWidth, clientHeight: elHeight} = el;

        const elAnchorHeight = Math.max(
            parseFloat(getComputedStyle(el, ':before').borderWidth || '0'),
            parseFloat(getComputedStyle(el, ':after').borderWidth || '0')
        );

        const leftCorrection = (parentBounds.width - elWidth) / 2;

        let left =
            parentBounds.left -
            positionalBounds.left +
            positionalParent.scrollLeft +
            leftCorrection;

        let top =
            parentBounds.top -
            positionalBounds.top +
            positionalParent.scrollTop +
            parentBounds.height;

        const leftmost = left + positionalBounds.left;
        const rightmost = leftmost + elWidth;

        const topmost = top + positionalBounds.top;
        const bottommost = topmost + elHeight + elAnchorHeight;

        let arrow: Arrow | undefined = Arrow.Top;

        left -= Math.min(0, leftmost);
        left -= Math.max(0, rightmost - document.documentElement.clientWidth);

        if (bottommost > document.documentElement.clientHeight) {
            top -= elHeight + elAnchorHeight + parentBounds.height;
            arrow = Arrow.Bottom;
        }

        el.style.top = `${top}px`;
        el.style.left = `${left}px`;
        el.style.position = 'absolute';

        if (this.state.arrow !== arrow) {
            this.setState({arrow});
        }
    }
}
