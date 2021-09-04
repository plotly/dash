import {assert} from 'chai';

import shouldComponentUpdate from 'dash-table/components/Table/shouldComponentUpdate';

describe('shouldComponentUpdate', () => {
    it('should update on undefined -> defined props', () => {
        assert(shouldComponentUpdate({}, {a: 0}, {}, {}));
    });

    it('should update on undefined -> defined state', () => {
        assert(shouldComponentUpdate({}, {}, {}, {a: 0}));
    });

    it('should update on defined -> undefined props', () => {
        assert(shouldComponentUpdate({a: 0}, {}, {}, {}));
    });

    it('should update on defined -> undefined state', () => {
        assert(shouldComponentUpdate({}, {}, {a: 0}, {}));
    });

    it('should not update on derived props', () => {
        assert(
            !shouldComponentUpdate({derived_test: 0}, {derived_test: 1}, {}, {})
        );
    });

    it('should update on derived state', () => {
        assert(
            shouldComponentUpdate({}, {}, {derived_test: 0}, {derived_test: 1})
        );
    });
});
