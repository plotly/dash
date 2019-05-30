import RadioItems from '../../src/components/RadioItems.react.js';
import React from 'react';
import {mount, render} from 'enzyme';
import {validate} from './utils';


test('RadioItems renders', () => {
    const dd = render(<RadioItems />);

    expect(dd.html()).toBeDefined();
});

describe('Props can be set properly', () => {
    const testProps = {
        id: 'radio-1',
        options: [
            {label: 'A', value: 'a'},
            {label: 1, value: 2},
            {label: 'Disabled', value: 'x', disabled: true}
        ],
        value: 2,
        style: {backgroundColor: 'hotpink'},
        className: 'radio-class',
        inputStyle: {margin: '22px'},
        inputClassName: 'radio-input-class',
        labelStyle: {fontSize: '2.0em'},
        labelClassName: 'radio-label-class',
        loading_state: {
            is_loading: false,
            component_name: '',
            prop_name: '',
        },
    };

    const radio = mount(<RadioItems {...testProps} />);

    test('props are being set', () => {
        validate(RadioItems, testProps);
        expect(radio.props()).toBeDefined();
        expect(radio.props()).toEqual(testProps);
    });

    test('props.id is set as the outer element id', () => {
        // test if id is in the actual HTML string
        const ddTag = radio.render();
        expect(ddTag.attr('id')).toEqual(testProps.id);
    });
});
