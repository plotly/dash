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
        autoFocus: 'autofocus',
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
        loading_state: {
            is_loading: false,
            component_name: '',
            prop_name: '',
        },
        persisted_props: ['value'],
        persistence_type: 'local',
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
    let mockSetProps, input;
    beforeEach(() => {
        mockSetProps = jest.fn();

        input = mount(<Input value="initial value" setProps={mockSetProps} />);
    });

    test("Input updates it's value on receiving new props", () => {
        input.setProps({value: 'new value'});

        // expect value prop to not be updated on state, and on the node itself
        expect(input.find('input').instance().value).toEqual('new value');
    });
});

describe('Input with type=number', () => {
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
            input.find('input').simulate('change', {target: {value: `${3}`}});
            // if the target value is higher than max, don't even call setProps
            expect(mockSetProps.mock.calls.length).toEqual(0);
            // <input/>'s value should remain the same
            expect(Number(input.find('input').instance().value)).toEqual(0);
        });
    });
});
