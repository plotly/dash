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
            DashTable.getCellById(0, 'rows').click();
            DashTable.getSelectedCells().should('have.length', 1);

            cy.get('.row-1').scrollTo(0, 1000);
            DashTable.getSelectedCells().should('have.length', 0);
        });

        it('keeps active cell', () => {
            DashTable.getCellById(0, 'rows').click();
            DashTable.getActiveCell().should('have.length', 1);

            cy.get('.row-1').scrollTo(0, 1000);
            DashTable.getActiveCell().should('have.length', 0);

            cy.get('.row-1').scrollTo(0, 0);
            DashTable.getActiveCell().should('have.length', 1);
        });

        it('keep selected cells', () => {
            DashTable.toggleScroll(false);
            DashTable.getCell(0, 1).click();
            DOM.focused.type(Key.Shift, { release: false });
            DashTable.getCell(2, 2).click();
            DashTable.toggleScroll(true);

            DashTable.getSelectedCells().should('have.length', 6);

            cy.get('.row-1').scrollTo(0, 1000);
            DashTable.getSelectedCells().should('have.length', 0);

            cy.get('.row-1').scrollTo(0, 0);
            DashTable.getSelectedCells().should('have.length', 6);
        });

        it('can edit cell', () => {
            DashTable.toggleScroll(false);
            DashTable.getCell(0, 0).click();
            DashTable.toggleScroll(true);

            cy.get('.row-1').scrollTo(0, 1000);
            cy.wait(1000);

            DashTable.getCell(10, 1).click();
            DOM.focused.type(`Edited${Key.Enter}`);

            DOM.focused.type(`${Key.ArrowUp}`);
            DOM.focused.should('have.value', 'Edited');
        });
    });
});