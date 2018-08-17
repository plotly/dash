import Dropdown from 'react-select';
import React, {
    ChangeEvent,
    ClipboardEvent,
    Component,
    MouseEvent
} from 'react';

interface IDropdownOption {
    label: string;
    value: string;
}

interface IProps {
    active: boolean;
    clearable: boolean;
    dropdown: IDropdownOption[];
    editable: boolean;
    focused: boolean;
    onChange: (e: ChangeEvent) => void;
    onClick: (e: MouseEvent) => void;
    onDoubleClick: (e: MouseEvent) => void;
    onPaste: (e: ClipboardEvent) => void;
    selected: boolean;
    value: any;

    classes?: string[];
    style?: object;
    type?: string;
}

interface IDefaultProps {
    classes: string[];
    style: object;
    type: string;
}

interface IState {
    value: any;
}

type IPropsWithDefaults = IProps & IDefaultProps;

export default class Cell extends Component<IProps, IState> {
    public static defaultProps: IDefaultProps = {
        classes: [],
        style: {},
        type: 'text'
    };

    constructor(props: IProps) {
        super(props);

        this.state = {
            value: props.value
        };
    }

    get classes(): string[] {
        let {
            active,
            classes,
            editable,
            selected,
            type
        } = this.propsWithDefaults;

        return [
            ...(active ? ['focused'] : []),
            ...(!editable ? ['cell--uneditable'] : []),
            ...(selected ? ['cell--selected'] : []),
            ...(type === 'dropdown' ? ['dropdown'] : []),
            ...classes
        ];
    }

    get propsWithDefaults(): IPropsWithDefaults {
        return this.props as IPropsWithDefaults;
    }

    private renderDropdown() {
        const {
            clearable,
            dropdown,
            onChange,
            value
        } = this.propsWithDefaults;

        return !dropdown ?
            this.renderValue() :
            (<Dropdown
                ref='dropdown'
                clearable={clearable}
                onChange={(newValue: any) => {
                    onChange(newValue ? newValue.value : newValue);
                }}
                onOpen={this.handleOpenDropdown}
                options={dropdown}
                placeholder={''}
                value={value}
            />);
    }

    private renderInput() {
        const {
            active,
            focused,
            onClick,
            onDoubleClick,
            onPaste
        } = this.propsWithDefaults;

        const classes = [
            ...(active ? ['input-active'] : []),
            ...(focused ? ['focused'] : ['unfocused']),
            ...['cell-value']
        ];

        const attributes = {
            className: classes.join(' '),
            onClick: onClick,
            onDoubleClick: onDoubleClick
        };

        return !active ?
            this.renderValue(attributes) :
            (<input
                ref='textInput'
                type='text'
                value={this.state.value}
                onChange={this.handleChange}
                onPaste={onPaste}
                {...attributes}
            />);
    }

    private renderValue(attributes = {}) {
        const { value } = this.propsWithDefaults;

        return (<div
            {...attributes}
        >
            {value}
        </div>);
    }

    private renderInner() {
        const {
            type
        } = this.props;

        switch (type) {
            case 'text':
            case 'numeric':
                return this.renderInput();
            case 'dropdown':
                return this.renderDropdown();
            default:
                return this.renderValue();
        }
    }

    render() {
        let {
            style
        } = this.props;

        return (<td
            className={this.classes.join(' ')}
            style={style}
        >
            {this.renderInner()}
        </td>);
    }

    handleChange = (e: any) => {
        this.setState({ value: e.target.value });
    }

    handleOpenDropdown = () => {
        const { dropdown }: { [key: string]: any } = this.refs;

        const menu = dropdown.wrapper.querySelector('.Select-menu-outer');
        const parentBoundingRect = menu.parentElement.getBoundingClientRect();

        menu.style.width = `${parentBoundingRect.width}px`;
        menu.style.top = `${parentBoundingRect.y + parentBoundingRect.height}px`;
        menu.style.left = `${parentBoundingRect.x}px`;
        menu.style.position = 'fixed';
    }

    componentWillReceiveProps(nextProps: IPropsWithDefaults) {
        const { value } = this.props;
        const { value: nextValue } = nextProps;

        if (value !== nextValue) {
            this.setState({
                value: nextValue
            });
        }
    }

    componentDidUpdate() {
        const { active, onChange, value } = this.propsWithDefaults;

        if (active && this.refs.textInput) {
            (this.refs.textInput as HTMLElement).focus();
        }

        if (!active && this.state.value !==  value) {
            onChange({
                target: {
                    value: this.state.value
                }
            } as any);
        }
    }
}