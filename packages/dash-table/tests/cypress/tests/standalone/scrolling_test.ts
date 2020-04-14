import * as R from 'ramda';

import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode, AppFlavor } from 'demo/AppMode';

const variants: [AppMode, AppFlavor[]][] = R.xprod(
    [AppMode.Virtualized],
    [[AppFlavor.FixedColumn, AppFlavor.FixedRow]]
);

variants.forEach(([mode, flavors]) => {
    describe(`scrolling, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}&flavor=${flavors.join(';')}`);
        });

        it('selects cell and keeps it / loses it based on virtualization', () => {
            DashTable.clickCellById(0, 'rows');
            DashTable.getSelectedCells().should('have.length', 1);

            cy.get('.row-1').scrollTo(0, 1000);
            DashTable.getSelectedCells().should('have.length', 0);
        });

        it('keeps active cell', () => {
            DashTable.clickCellById(0, 'rows');
            DashTable.getActiveCell().should('have.length', 1);

            cy.get('.row-1').scrollTo(0, 1000);
            DashTable.getActiveCell().should('have.length', 0);

            cy.get('.row-1').scrollTo(0, 0);
            DashTable.getActiveCell().should('have.length', 1);
        });

        it('keep selected cells', () => {
            DashTable.toggleScroll(false);
            DashTable.clickCell(0, 1);
            DashTable.focusedType(Key.Shift, { release: false });
            DashTable.clickCell(2, 2);
            DashTable.toggleScroll(true);

            DashTable.getSelectedCells().should('have.length', 6);

            cy.get('.row-1').scrollTo(0, 1000);
            DashTable.getSelectedCells().should('have.length', 0);

            cy.get('.row-1').scrollTo(0, 0);
            DashTable.getSelectedCells().should('have.length', 6);
        });

        it('can edit cell', () => {
            DashTable.toggleScroll(false);
            DashTable.clickCell(0, 0);
            DashTable.toggleScroll(true);

            cy.get('.row-1').scrollTo(0, 1000);
            cy.wait(1000);

            DashTable.clickCell(10, 1);
            DashTable.focusedType(`Edited${Key.Enter}`);

            DashTable.focusedType(`${Key.ArrowUp}`);
            DOM.focused.should('have.value', 'Edited');
        });
    });
});