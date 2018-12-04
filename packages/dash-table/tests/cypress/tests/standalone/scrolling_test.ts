import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

import { AppMode } from 'demo/AppMode';

const VirtualAppMode = [
    AppMode.FixedVirtualized,
    AppMode.Virtualized
];

Object.values(VirtualAppMode).forEach(mode => {
    describe(`scrolling, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
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
    });
});