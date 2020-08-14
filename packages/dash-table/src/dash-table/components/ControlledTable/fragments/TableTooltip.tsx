import React, {Component} from 'react';

import Tooltip, {ITooltipProps, Arrow} from 'dash-table/components/Tooltip';
import tooltipHelper from 'dash-table/components/tooltipHelper';
import ReactDOM from 'react-dom';
import {isEqual} from 'core/comparer';

interface IState {
    arrow?: Arrow;
    cell?: any;
}

export default class TableTooltip extends Component<ITooltipProps, IState> {
    constructor(props: ITooltipProps) {
        super(props);

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
                ref='tooltip'
                arrow={arrow}
                {...this.props}
            />
        );
    }

    private adjustPosition() {
        const {cell} = this.state;

        const el = ReactDOM.findDOMNode(this.refs.tooltip) as any;

        const {positionalParent, parent} = tooltipHelper(el, cell);

        if (!positionalParent || !parent || !el) {
            return;
        }

        const positionalBounds = positionalParent.getBoundingClientRect();
        const parentBounds = parent.getBoundingClientRect();

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

        const {
            scrollLeft: vwLeft,
            scrollTop: vwTop,
            clientWidth: vwWidth,
            clientHeight: vwHeight
        } = document.body;

        let arrow: Arrow | undefined = Arrow.Top;

        let delta = 0;

        // too far left
        if (left < vwLeft) {
            delta = vwLeft - left;
            left = vwLeft;
        }

        // too far right
        if (left + elWidth > vwLeft + vwWidth) {
            delta = vwLeft + vwWidth - elWidth - left;
            left = vwLeft + vwWidth - elWidth;
        }

        // too low
        if (top + elHeight > vwTop + vwHeight) {
            top =
                parentBounds.top -
                positionalBounds.top +
                positionalParent.scrollTop -
                (elHeight + elAnchorHeight);
            arrow = Arrow.Bottom;
        }

        delta = Math.abs(delta);
        if (delta > parent.clientWidth / 2) {
            arrow = undefined;
        }

        el.style.top = `${top}px`;
        el.style.left = `${left}px`;
        el.style.position = 'absolute';

        if (this.state.arrow !== arrow) {
            this.setState({arrow});
        }
    }
}
