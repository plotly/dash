import {expect} from 'chai';

import reconcile from 'dash-table/type/reconcile';
import {
    ColumnType,
    ChangeAction,
    ChangeFailure
} from 'dash-table/components/Table/props';

describe('reconcile', () => {
    describe('coerce/validate', () => {
        it('applies default ', () => {
            const res = reconcile(null, {
                type: ColumnType.Numeric,
                on_change: {
                    action: ChangeAction.Coerce,
                    failure: ChangeFailure.Default
                },
                validation: {
                    default: 0
                }
            });

            expect(res.success).to.equal(true);
            expect(res.value).to.equal(0);
        });
    });
});
