import isEditable from 'dash-table/derived/cell/isEditable';

describe('isEditable', () => {
    it('returns false if table=false, column=false', () =>
        expect(isEditable(false, false)).to.equal(false)
    );

    it('returns false if table=false, column=undefined', () =>
        expect(isEditable(false, undefined)).to.equal(false)
    );

    it('returns true if table=false, column=true', () =>
        expect(isEditable(false, true)).to.equal(true)
    );

    it('returns false if table=true, column=false', () =>
        expect(isEditable(true, false)).to.equal(false)
    );

    it('returns true if table=true, column=undefined', () =>
        expect(isEditable(true, undefined)).to.equal(true)
    );

    it('returns true if table=true, column=true', () =>
        expect(isEditable(true, true)).to.equal(true)
    );
});