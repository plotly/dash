import {expect} from 'chai';

import {handleEnter, handleMove} from 'dash-table/handlers/cellEvents';

describe('cell events - tooltip row index with pagination', () => {
    it('uses the provided row index when entering a cell', () => {
        let state: any;
        const propsFn = () =>
            ({
                setState: (next: any) => {
                    state = next;
                },
                visibleColumns: [{id: 'Description'}],
                virtualized: {
                    indices: [5, 6, 7, 8, 9],
                    offset: {rows: 0, columns: 0}
                }
            }) as any;

        handleEnter(propsFn, 6, 0);

        expect(state.currentTooltip.row).to.equal(6);
        expect(state.currentTooltip.id).to.equal('Description');
        expect(state.currentTooltip.header).to.equal(false);
    });

    it('uses the provided row index when moving between cells', () => {
        let state: any;
        const propsFn = () =>
            ({
                currentTooltip: {
                    header: false,
                    id: 'Description',
                    row: 5
                },
                setState: (next: any) => {
                    state = next;
                },
                visibleColumns: [{id: 'Description'}],
                virtualized: {
                    indices: [5, 6, 7, 8, 9],
                    offset: {rows: 0, columns: 0}
                }
            }) as any;

        handleMove(propsFn, 6, 0);

        expect(state.currentTooltip.row).to.equal(6);
        expect(state.currentTooltip.id).to.equal('Description');
        expect(state.currentTooltip.header).to.equal(false);
    });
});
