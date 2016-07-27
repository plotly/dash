import React from 'react';
import {shallow} from 'enzyme';
import DropdownComponent from '../Dropdown.react';

describe('Dropdown component', () => {

    it('renders', () => {
        const component = shallow(<DropdownComponent/>);
        expect(component).to.be.ok;
    });

    describe('options', () => {
        it('renders passed-in options');
    });
});