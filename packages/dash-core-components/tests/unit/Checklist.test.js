import Checklist from '../../src/components/Checklist.react.js';
import React from 'react';
import {mount, render} from 'enzyme';
import {validate} from './utils';

test('Checklist renders', () => {
    const dd = render(<Checklist />);

    expect(dd.html()).toBeDefined();
});

describe('Props can be set properly', () => {
    const testPropsNoValue = {
        id: 'radio-1',
        options: [
            {label: 'A', value: 'a'},
            {label: 1, value: 2},
            {label: 'Disabled', value: 'x', disabled: true},
        ],
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

    const testProps = Object.assign({}, testPropsNoValue, {value: ['a', 2]});

    const checklist = mount(<Checklist {...testProps} />);
    const checklistNoValue = mount(<Checklist {...testPropsNoValue} />);

    test('props are being set', () => {
        validate(Checklist, testProps);
        expect(checklist.props()).toBeDefined();
        expect(checklist.props()).toEqual(testProps);
    });

    test('it works with options but no value supplied', () => {
        validate(Checklist, testPropsNoValue);
        expect(checklistNoValue.props()).toBeDefined();
        expect(checklistNoValue.props()).toEqual(
            Object.assign({}, testPropsNoValue, {value: []})
        );
    });

    test('props.id is set as the outer element id', () => {
        // test if id is in the actual HTML string
        const ddTag = checklist.render();
        expect(ddTag.attr('id')).toEqual(testProps.id);
    });
});
