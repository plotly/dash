import {expect} from 'chai';

import dataLoading from 'dash-table/derived/table/data_loading';

describe('loading state uneditable', () => {
    it('returns true when data are loading', () => {
        const loading = dataLoading({
            is_loading: true,
            prop_name: 'data',
            component_name: ''
        });

        expect(loading).to.equal(true);
    });

    it('returns false when a non-data prop is loading', () => {
        const loading = dataLoading({
            is_loading: true,
            prop_name: 'style_cell_conditional',
            component_name: ''
        });

        expect(loading).to.equal(false);
    });

    it('returns false when table is not loading', () => {
        const loading = dataLoading({
            is_loading: false,
            prop_name: 'data',
            component_name: ''
        });

        expect(loading).to.equal(false);
    });
});
