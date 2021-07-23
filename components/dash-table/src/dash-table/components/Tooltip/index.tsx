import * as R from 'ramda';
import React, {PureComponent} from 'react';
import {Remarkable} from 'remarkable';

import {isEqual} from 'core/comparer';

import {MAX_32BITS} from 'dash-table/derived/table/tooltip';
import {TooltipSyntax} from 'dash-table/tooltips/props';

export enum Arrow {
    Bottom = 'bottom',
    Left = 'left',
    Right = 'right',
    Top = 'top'
}

export interface ITooltipProps {
    arrow?: Arrow;
    className?: string;
    tooltip: {
        delay: number;
        duration: number;
        type?: TooltipSyntax;
        value?: string;
    };
}

interface ITooltipState {
    display?: boolean;
    displayTooltipId?: any;
    hideTooltipId?: any;
    md: Remarkable;
}

export default class Tooltip extends PureComponent<
    ITooltipProps,
    ITooltipState
> {
    constructor(props: ITooltipProps) {
        super(props);

        this.state = {
            md: new Remarkable()
        };
    }

    UNSAFE_componentWillReceiveProps(nextProps: ITooltipProps) {
        const {delay, duration} = nextProps.tooltip;

        if (
            isEqual(R.omit(['arrow'], this.props), R.omit(['arrow'], nextProps))
        ) {
            return;
        }

        this.setState({
            display: false,
            displayTooltipId:
                Boolean(clearTimeout(this.state.displayTooltipId)) ||
                setTimeout(() => this.setState({display: true}), delay),
            hideTooltipId:
                Boolean(clearTimeout(this.state.hideTooltipId)) ||
                setTimeout(
                    () => this.setState({display: false}),
                    Math.min(delay + duration, MAX_32BITS)
                )
        });
    }

    render() {
        const {arrow, className} = this.props;
        const {type, value} = this.props.tooltip;
        const {md} = this.state;

        if (!type || !value) {
            return null;
        }

        const props =
            type === TooltipSyntax.Text
                ? {children: value}
                : {dangerouslySetInnerHTML: {__html: md.render(value)}};

        const {display} = this.state;

        return (
            <div
                className='dash-tooltip'
                data-attr-anchor={arrow}
                style={{visibility: display ? 'visible' : 'hidden'}}
            >
                <div className={className} {...props} />
            </div>
        );
    }
}
