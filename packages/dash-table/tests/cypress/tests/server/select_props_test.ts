import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';
import { map, xprod } from 'ramda';

function expectArray(selector: string, vals: number[], sorted?: boolean) {
    cy.get(selector).should($container => {
        const valsOut = JSON.parse($container.text()) as number[];
        if (sorted !== false) {
            valsOut.sort();
        }
        expect(valsOut).to.deep.equal(vals);
    });
}

function expectCellSelection(
    rows: number[],
    rowIds?: number[],
    cols?: number[],
    colIds?: number[],
    activeItem?: number[], // indices within rows/cols, dflt [0,0]
    startItem?: number[] // same^
) {
    function makeCell(rc: number[]) {
        const [r, c] = rc;
        return {
            row: rows[r],
            row_id: rowIds && rowIds[r],
            column: cols && cols[c],
            column_id: colIds && colIds[c]
        };
    }

    let activeCell: any;
    let startCell: any;
    let endCell: any;
    let selectedCells: any;
    if (rows.length && cols) {
        activeCell = makeCell(activeItem || [0, 0]);
        startCell = makeCell(startItem || [0, 0]);
        endCell = makeCell(startItem ? [0, 0] : [rows.length - 1, cols.length - 1]);
        selectedCells = map(makeCell, xprod(range(0, rows.length - 1), range(0, cols.length - 1)));
    } else {
        activeCell = startCell = endCell = selectedCells = null;
    }

    cy.get('#active_cell_container').should($container => {
        expect(JSON.parse($container.text())).to.deep.equal(activeCell);
    });
    cy.get('#start_cell_container').should($container => {
        expect(JSON.parse($container.text())).to.deep.equal(startCell);
    });
    cy.get('#end_cell_container').should($container => {
        expect(JSON.parse($container.text())).to.deep.equal(endCell);
    });
    cy.get('#selected_cells_container').should($container => {
        if (selectedCells && selectedCells.length) {
            expect(JSON.parse($container.text())).to.deep.equal(selectedCells);
        } else {
            expect($container.text()).to.be.oneOf(['null', '[]']);
        }
    });
}

// NOTE: this function includes both endpoints
// easier to compare with the full arrays that way.
function range(from: number, to: number, step?: number) {
    const _step = step || 1;
    const out: number[] = [];
    for (let v = from; v * _step <= to * _step; v += _step) {
        out.push(v);
    }
    return out;
}

describe('select row', () => {
    describe('be pagination & sort', () => {
        beforeEach(() => cy.visit('http://localhost:8081'));

        it('can select row', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(0).within(() => cy.get('input').should('be.checked'));
        });

        it('can select row when sorted', () => {
            cy.get('tr th.column-0 .column-header--sort').last().click({ force: true });
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(0).within(() => cy.get('input').should('be.checked'));
        });

        it('select, sort, new row is not selected', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(0).within(() => cy.get('input').should('be.checked'));
            cy.get('tr th.column-0 .column-header--sort').last().click({ force: true });
            DashTable.getSelect(0).within(() => cy.get('input').should('not.be.checked'));
        });
    });

    describe('fe pagination & sort', () => {
        beforeEach(() => cy.visit('http://localhost:8083'));

        it('selection props are correct, no sort / filter', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(1).within(() => cy.get('input').click());

            expectCellSelection([]);

            // single cell selection
            DashTable.getCell(3, 1).click();
            expectCellSelection([3], [3003], [1], [1]);

            // region up & left - active & start stay at the bottom right
            DOM.focused.type(Key.Shift, { release: false });
            DashTable.getCell(1, 0).click();
            expectCellSelection([1, 2, 3], [3001, 3002, 3003], [0, 1], [0, 1], [2, 1], [2, 1]);

            // shrink the selection
            DOM.focused.type(Key.Shift, { release: false });
            DashTable.getCell(2, 1).click();
            expectCellSelection([2, 3], [3002, 3003], [1], [1], [1, 0], [1, 0]);

            // move the active cell without changing the selection
            DOM.focused.type(Key.Shift); // and release
            DashTable.getCell(2, 1).click();
            expectCellSelection([2, 3], [3002, 3003], [1], [1], [0, 0], [1, 0]);

            expectArray('#selected_rows_container', [0, 1]);
            expectArray('#selected_row_ids_container', [3000, 3001]);
            expectArray('#derived_viewport_selected_rows_container', [0, 1]);
            expectArray('#derived_viewport_selected_row_ids_container', [3000, 3001]);
            expectArray('#derived_virtual_selected_rows_container', [0, 1]);
            expectArray('#derived_virtual_selected_row_ids_container', [3000, 3001]);
            expectArray('#derived_viewport_indices_container', range(0, 249), false);
            expectArray('#derived_viewport_row_ids_container', range(3000, 3249), false);
            expectArray('#derived_virtual_indices_container', range(0, 999), false);
            expectArray('#derived_virtual_row_ids_container', range(3000, 3999), false);
        });

        it('selection props are correct, with filter', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(1).within(() => cy.get('input').click());
            DashTable.getSelect(2).within(() => cy.get('input').click());

            cy.get('tr th.column-0.dash-filter input').type(`is even${Key.Enter}`);

            // filtered-out data is still selected
            expectArray('#selected_rows_container', [0, 1, 2]);
            expectArray('#selected_row_ids_container', [3000, 3001, 3002]);
            expectArray('#derived_viewport_selected_rows_container', [0, 1]);
            expectArray('#derived_viewport_selected_row_ids_container', [3000, 3002]);
            expectArray('#derived_virtual_selected_rows_container', [0, 1]);
            expectArray('#derived_virtual_selected_row_ids_container', [3000, 3002]);
            expectArray('#derived_viewport_indices_container', range(0, 498, 2), false);
            expectArray('#derived_viewport_row_ids_container', range(3000, 3498, 2), false);
            expectArray('#derived_virtual_indices_container', range(0, 998, 2), false);
            expectArray('#derived_virtual_row_ids_container', range(3000, 3998, 2), false);
        });

        it('selection props are correct, with filter & sort', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(1).within(() => cy.get('input').click());

            DashTable.getCell(3, 1).click();
            expectCellSelection([3], [3003], [1], [1]);

            cy.get('tr th.column-0.dash-filter input').type(`is even${Key.Enter}`);

            expectCellSelection([]);

            DashTable.getCell(3, 1).click();
            expectCellSelection([3], [3006], [1], [1]);

            cy.get('tr th.column-0 .column-header--sort').last().click({ force: true });

            expectCellSelection([]);

            cy.get('tr th.column-0 .column-header--sort').last().click({ force: true });

            DashTable.getSelect(0).within(() => cy.get('input').click());

            DashTable.getCell(3, 1).click();
            expectCellSelection([3], [3992], [1], [1]);

            expectArray('#selected_rows_container', [0, 1, 998]);
            expectArray('#selected_row_ids_container', [3000, 3001, 3998]);
            expectArray('#derived_viewport_selected_rows_container', [0]);
            expectArray('#derived_viewport_selected_row_ids_container', [3998]);
            expectArray('#derived_virtual_selected_rows_container', [0, 499]);
            expectArray('#derived_virtual_selected_row_ids_container', [3000, 3998]);
            expectArray('#derived_viewport_indices_container', range(998, 500, -2), false);
            expectArray('#derived_viewport_row_ids_container', range(3998, 3500, -2), false);
            expectArray('#derived_virtual_indices_container', range(998, 0, -2), false);
            expectArray('#derived_virtual_row_ids_container', range(3998, 3000, -2), false);
        });
    });
});
