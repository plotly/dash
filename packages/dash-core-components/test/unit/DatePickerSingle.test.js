import DatePickerSingle from '../../src/components/DatePickerSingle.react';
import R from 'ramda';
import React from 'react';
import {mount, render} from 'enzyme';

test('DatePickerSingle renders', () => {
    const dps = render(<DatePickerSingle />);

    expect(dps.html()).toBeDefined();
});

describe('Date can be set properly', () => {
    const defaultProps = {};

    test('null date is not converted by moment', () => {
        const props = R.merge(defaultProps, {
            date: null,
        });

        const dps = mount(<DatePickerSingle {...props} />);

        expect(dps.props()).toBeDefined();
        expect(dps.props().date).toEqual(props.date);
        expect(dps.state().date).toEqual(null);
    });

    test('valid date is not converted by moment', () => {
        const props = R.merge(defaultProps, {
            date: '2019-01-01',
        });

        const dps = mount(<DatePickerSingle {...props} />);

        expect(dps.props()).toBeDefined();
        expect(dps.props().date).toEqual(props.date);
        expect(dps.state().date).not.toEqual(null);
    });
});
