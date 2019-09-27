import Dropdown from '../../src/components/Dropdown.react.js';
import React from 'react';
import {mount, render} from 'enzyme';
import {validate} from './utils';

test('Dropdown renders', () => {
    const dd = render(<Dropdown />);

    expect(dd.html()).toBeDefined();
});

describe('Props can be set properly', () => {
    const singleProps = {
        id: 'dd-1',
        options: [
            {label: 'A', value: 'a'},
            {label: 1, value: 2},
            {label: 'Disabled', value: 'x', disabled: true},
        ],
        value: 2,
        optionHeight: 50,
        className: 'dd-class',
        clearable: true,
        disabled: true,
        multi: false,
        placeholder: 'pick something',
        searchable: true,
        search_value: 'hello',
        style: {backgroundColor: 'hotpink'},
        loading_state: {
            is_loading: false,
            component_name: '',
            prop_name: '',
        },
        persisted_props: ['value'],
        persistence_type: 'local',
    };

    const multiProps = Object.assign({}, singleProps, {
        multi: true,
        value: ['a', 2],
    });
    const singleDD = mount(<Dropdown {...singleProps} />);
    const multiDD = mount(<Dropdown {...multiProps} />);

    test('props are being set', () => {
        validate(Dropdown, singleProps);
        expect(singleDD.props()).toBeDefined();
        expect(singleDD.props()).toEqual(singleProps);

        validate(Dropdown, multiProps);
        expect(multiDD.props()).toBeDefined();
        expect(multiDD.props()).toEqual(multiProps);
    });

    test('props.id is set as the outer element id', () => {
        // test if id is in the actual HTML string
        const ddTag = singleDD.render();
        expect(ddTag.attr('id')).toEqual(singleProps.id);
    });
});
