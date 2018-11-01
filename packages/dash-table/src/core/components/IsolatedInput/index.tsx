import React, { PureComponent } from 'react';

type Submit = (value: string | undefined) => void;

interface IProps {
    placeholder?: string;
    updateOnBlur?: boolean;
    updateOnSubmit?: boolean;
    stopPropagation?: boolean;
    submit: Submit;
    value: string | undefined;
}

interface IDefaultProps {
    stopPropagation: boolean;
    updateOnBlur: boolean;
    updateOnSubmit: boolean;
}

interface IState {
    value: string | undefined;
}

type PropsWithDefaults = IProps & IDefaultProps;

export default class IsolatedInput extends PureComponent<IProps, IState> {
    public static readonly defaultProps = {
        stopPropagation: false,
        updateOnBlur: true,
        updateOnSubmit: true
    };

    private get propsWithDefaults() {
        return this.props as PropsWithDefaults;
    }

    constructor(props: PropsWithDefaults) {
        super(props);

        this.state = {
            value: props.value
        };
    }

    handleChange = (ev: any) => this.setState({
        value: ev.target.value
    })

    submit = () =>
        this.state.value !== this.props.value &&
        this.props.submit(this.state.value)

    render() {
        const {
            placeholder,
            stopPropagation,
            updateOnBlur,
            updateOnSubmit
        } = this.propsWithDefaults;

        let props = {
            onBlur: updateOnBlur ? this.submit : undefined,
            onKeyDown: stopPropagation ? (ev: any) => ev.stopPropagation() : undefined,
            onSubmit: updateOnSubmit ? this.submit : undefined
        };

        return (<input
            ref='input'
            type='text'
            value={this.state.value || ''}
            onChange={this.handleChange}
            placeholder={placeholder}
            {...props}
        />);
    }
}