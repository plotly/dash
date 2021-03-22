import {expect} from 'chai';

import resolveFlag from 'dash-table/derived/cell/resolveFlag';

describe('isEditable', () => {
    it('returns false if table=false, column=false', () =>
        expect(resolveFlag(false, false)).to.equal(false));

    it('returns false if table=false, column=undefined', () =>
        expect(resolveFlag(false, undefined)).to.equal(false));

    it('returns true if table=false, column=true', () =>
        expect(resolveFlag(false, true)).to.equal(true));

    it('returns false if table=true, column=false', () =>
        expect(resolveFlag(true, false)).to.equal(false));

    it('returns true if table=true, column=undefined', () =>
        expect(resolveFlag(true, undefined)).to.equal(true));

    it('returns true if table=true, column=true', () =>
        expect(resolveFlag(true, true)).to.equal(true));
});
