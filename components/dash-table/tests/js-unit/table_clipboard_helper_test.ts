import {expect} from 'chai';

import TableClipboardHelper from 'dash-table/utils/TableClipboardHelper';

describe('table clipboard helper tests', () => {
    it('test parse basic', () => {
        const res = TableClipboardHelper.parse('abc\tefg\n123\t456');
        expect(res.length).to.equal(2);
        expect(res[0].length).to.equal(2);
        expect(res[1].length).to.equal(2);
        expect(res[0][0]).to.equal('abc');
        expect(res[0][1]).to.equal('efg');
        expect(res[1][0]).to.equal('123');
        expect(res[1][1]).to.equal('456');
    });

    it('test parse with double quotes', () => {
        const res = TableClipboardHelper.parse('a""bc\tefg\n123\t456');
        expect(res.length).to.equal(2);
        expect(res[0].length).to.equal(2);
        expect(res[1].length).to.equal(2);
        expect(res[0][0]).to.equal('a""bc');
        expect(res[0][1]).to.equal('efg');
        expect(res[1][0]).to.equal('123');
        expect(res[1][1]).to.equal('456');
    });

    it('test with multiline', () => {
        const res = TableClipboardHelper.parse('"a\nb\nc"\tefg\n123\t456');
        expect(res.length).to.equal(2);
        expect(res[0].length).to.equal(2);
        expect(res[1].length).to.equal(2);
        expect(res[0][0]).to.equal('a\nb\nc');
        expect(res[0][1]).to.equal('efg');
        expect(res[1][0]).to.equal('123');
        expect(res[1][1]).to.equal('456');
    });

    it('test with multiline and double quotes', () => {
        const res = TableClipboardHelper.parse('"a\nb""c"\te""fg\n123\t456');
        expect(res.length).to.equal(2);
        expect(res[0].length).to.equal(2);
        expect(res[1].length).to.equal(2);
        expect(res[0][0]).to.equal('a\nb"c');
        expect(res[0][1]).to.equal('e""fg');
        expect(res[1][0]).to.equal('123');
        expect(res[1][1]).to.equal('456');
    });
});
