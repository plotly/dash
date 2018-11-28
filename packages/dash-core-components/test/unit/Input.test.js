import Input from '../../src/components/Input.react.js';
import React from 'react';
import {mount, render} from 'enzyme';

test('Input renders', () => {
    const input = render(<Input />);

    expect(input.html()).toBeDefined();
});

describe('Props can be set properly', () => {
    const defaultProps = {
        id: 'input-1',
        value: 'hello, dash',
        style: {backgroundColor: 'hotpink'},
        className: 'input-class',
        type: 'text',
        autoComplete: 'on',
        autoFocus: 'on',
        disabled: true,
        debounce: false,
        inputMode: 'verbatim',
        list: 'hello',
        max: '2',
        maxLength: '2',
        min: '1',
        minLength: '1',
        multiple: true,
        name: 'input one',
        pattern: '/([A-Z])w+/g',
        placeholder: 'enter text',
        readOnly: 'readonly',
        required: 'required',
        selectionDirection: 'forward',
        selectionEnd: '1',
        selectionStart: '1',
        size: '10',
        spellCheck: 'true',
        step: '2',
        n_blur: 0,
        n_blur_timestamp: -1,
        n_submit: 0,
        n_submit_timestamp: -1,
    };
    const input = mount(<Input {...defaultProps} />);

    test('props are being set', () => {
        expect(input.props()).toBeDefined();
        expect(input.props()).toEqual(defaultProps);
    });

    test('props.id is set as the <input> id', () => {
        // test if id is in the actual HTML string
        const inputTag = input.render();
        expect(inputTag.attr('id')).toEqual(defaultProps.id);
    });
    test('props.value is set as the <input> value', () => {
        // test if value is in the actual HTML string
        const inputTag = input.render();
        expect(inputTag.attr('value')).toEqual(defaultProps.value);
    });
    test('props.className is set as the <input> CSS class', () => {
        // test if className is actually set on HTML output
        const inputTag = input.render();
        expect(inputTag.attr('class')).toEqual(defaultProps.className);
    });
    test('props.multiple is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('multiple')).toBeDefined();
        expect(inputTag.attr('multiple')).toEqual('multiple');
    });
    test('props.name is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('name')).toBeDefined();
        expect(inputTag.attr('name')).toEqual(defaultProps.name);
    });
    test('props.pattern is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('pattern')).toBeDefined();
        expect(inputTag.attr('pattern')).toEqual(defaultProps.pattern);
    });
    test('props.placeholder is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('placeholder')).toBeDefined();
        expect(inputTag.attr('placeholder')).toEqual(defaultProps.placeholder);
    });
    test('props.readOnly is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('readonly')).toBeDefined();
        expect(inputTag.attr('readonly')).toEqual(defaultProps.readOnly);
    });
    test('props.required is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('required')).toBeDefined();
        expect(inputTag.attr('required')).toEqual(defaultProps.required);
    });
    test('props.size is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('size')).toBeDefined();
        expect(inputTag.attr('size')).toEqual(defaultProps.size);
    });
    test('props.spellCheck is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('spellcheck')).toBeDefined();
        expect(inputTag.attr('spellcheck')).toEqual(defaultProps.spellCheck);
    });
    test('props.step is set as an attribute on the input', () => {
        const inputTag = input.render();
        expect(inputTag.attr('step')).toBeDefined();
        expect(inputTag.attr('step')).toEqual(defaultProps.step);
    });
});

describe('Input with (default) type=text', () => {
    describe('Input without setProps() defined', () => {
        let input;
        beforeEach(() => {
            input = mount(<Input value="initial value" />);
        });
        test('Input updates value', () => {
            expect(input.find('input').instance().value).toEqual(
                'initial value'
            );

            input
                .find('input')
                .simulate('change', {target: {value: 'new value'}});

            expect(input.find('input').instance().value).toEqual('new value');
        });
        test('Input does not change state if it rerenders', () => {
            // dash-renderer could rerender a component with it's original
            // props, if dash-renderer is not aware of prop changes (that happen with setState
            // instead of setProps)
            input.setProps({value: 'new value'});

            // expect value prop to not be updated on state, and on the node itself
            expect(input.state().value).toEqual('initial value');
            expect(input.find('input').instance().value).toEqual(
                'initial value'
            );
        });
    });

    describe('Input with setProps() defined', () => {
        let mockSetProps, input;
        beforeEach(() => {
            mockSetProps = jest.fn();

            input = mount(
                <Input value="initial value" setProps={mockSetProps} />
            );
        });
        test('Input does not use state if setProps is defined, and debounce is false', () => {
            expect(input.state()).toBeFalsy();
        });

        test('Input will call setProps with value updates if provided', () => {
            input
                .find('input')
                .simulate('change', {target: {value: 'new value'}});

            expect(mockSetProps.mock.calls.length).toEqual(1);
            expect(mockSetProps.mock.calls[0][0]).toEqual({value: 'new value'});
        });

        test("Input updates it's value on recieving new props", () => {
            input.setProps({value: 'new value'});

            // expect value prop to not be updated on state, and on the node itself
            expect(input.find('input').instance().value).toEqual('new value');
        });
    });
});

describe('Input with type=number', () => {
    describe('Without setProps(), using this.state', () => {
        describe('with min and max props', () => {
            let input;
            const props = {
                value: 0,
                min: 0,
                max: 2,
            };
            beforeEach(() => {
                input = mount(<Input type="number" {...props} />);
            });
            test('Input can not be updated lower than props.min', () => {
                input
                    .find('input')
                    .simulate('change', {target: {value: `${props.min - 1}`}});
                expect(Number(input.find('input').instance().value)).toEqual(
                    props.value
                );
            });
            test('Input can not be updated higher than props.max', () => {
                input
                    .find('input')
                    .simulate('change', {target: {value: `${props.max + 1}`}});
                expect(Number(input.find('input').instance().value)).toEqual(
                    props.value
                );
            });
        });
        describe('without min and max props', () => {
            let input;
            beforeEach(() => {
                input = mount(<Input type="number" value={0} />);
            });
            test('Input can be updated', () => {
                input.find('input').simulate('change', {target: {value: '-1'}});
                expect(Number(input.find('input').instance().value)).toEqual(-1);
                input.find('input').simulate('change', {target: {value: '100'}});
                expect(Number(input.find('input').instance().value)).toEqual(
                    100
                );
            });
        });
    });
    describe('With setProps', () => {
        describe('with min and max props', () => {
            let mockSetProps, input;
            const props = {
                value: 0,
                min: 0,
                max: 2,
            };
            beforeEach(() => {
                mockSetProps = jest.fn();
                input = mount(
                    <Input type="number" {...props} setProps={mockSetProps} />
                );
            });
            test('Input can not be updated lower than props.min', () => {
                input
                    .find('input')
                    .simulate('change', {target: {value: `${props.min - 1}`}});

                // if the target value is lower than min, don't even call setProps
                expect(mockSetProps.mock.calls.length).toEqual(0);
                // <input/>'s value should remain the same
                expect(Number(input.find('input').instance().value)).toEqual(0);
            });
            test('Input can not be updated higher than props.max', () => {
                input
                    .find('input')
                    .simulate('change', {target: {value: `${3}`}});
                // if the target value is higher than max, don't even call setProps
                expect(mockSetProps.mock.calls.length).toEqual(0);
                // <input/>'s value should remain the same
                expect(Number(input.find('input').instance().value)).toEqual(0);
            });
            test('Input can be updated normally', () => {
                input
                    .find('input')
                    .simulate('change', {target: {value: `${1}`}});
                // if the target value is higher than max, don't even call setProps
                expect(mockSetProps.mock.calls.length).toEqual(1);
                // input's value should remain the same
                expect(mockSetProps.mock.calls[0][0].value).toEqual(1);
            });
        });
        describe('without min and max props', () => {
            let mockSetProps, input;
            beforeEach(() => {
                mockSetProps = jest.fn();
                input = mount(
                    <Input type="number" value={0} setProps={mockSetProps} />
                );
            });
            test('Input can update normally', () => {
                input.find('input').simulate('change', {target: {value: '100'}});
                expect(mockSetProps.mock.calls.length).toEqual(1);
                expect(mockSetProps.mock.calls[0][0].value).toEqual(100);
            });
        });
        describe('with debouncing on', () => {
            let mockSetProps, input;
            beforeEach(() => {
                mockSetProps = jest.fn();
                input = mount(
                    <Input
                        type="number"
                        value={0}
                        debounce={true}
                        step={0.01}
                        setProps={mockSetProps}
                    />
                );
            });
            test('Input debounces update - only fires setProps on submit', () => {
                // Tests issue #169, where users couldn't input
                // 0.0 because setProps() would fire immediately, causing
                // 0.0 to be truncated to 0, making it impossible to input
                // 0.001 etc
                // eslint-disable-next-line no-magic-numbers
                const inputValues = ['0', '0.0', '0.0', '0.001'];

                for (let i = 0; i < inputValues.length; i++) {
                    input
                        .find('input')
                        .simulate('change', {target: {value: inputValues[i]}});
                }

                input.find('input').simulate('keypress', {key: 'Enter'});

                expect(mockSetProps.mock.calls.length).toEqual(1);
                expect(mockSetProps.mock.calls[0][0].value).toEqual(
                    Number(inputValues[inputValues.length - 1])
                );
            });
        });
    });
});
