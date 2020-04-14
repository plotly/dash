import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';
import { AppMode } from 'demo/AppMode';

describe('formatting', () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.Formatting}`);
        DashTable.toggleScroll(false);
    });

    it('can edit formatted cell', () => {
        DashTable.getCellById(1, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', 'N/A')
        );
        DashTable.clickCellById(1, 'eee');
        DashTable.focusedType(`1${Key.Enter}`);
        DashTable.getCellById(1, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', '1')
        );
        DashTable.clickCellById(1, 'eee');
        DashTable.focusedType(`abc${Key.Enter}`);
        DashTable.getCellById(1, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', 'N/A')
        );
    });

    it('can copy formatted cell and reformat based on destination cell rules', () => {
        DashTable.getCellById(2, 'eee').within(
            () => cy.get('.dash-cell-value').should('have.html', '3')
        );
        DashTable.clickCellById(2, 'eee');
        DashTable.focusedType(`${Key.Shift}${Key.ArrowDown}${Key.ArrowDown}`);
        DashTable.focusedType(`${Key.Meta}c`);

        DashTable.clickCellById(2, 'ddd');
        DashTable.focusedType(`${Key.Meta}v`);

        DashTable.clickCellById(2, 'eee');

        DashTable.getCellById(2, 'ddd').within(
            () => cy.get('.dash-cell-value').should('have.html', 'eq. $ 3.00')
        );
        DashTable.getCellById(3, 'ddd').within(
            () => cy.get('.dash-cell-value').should('have.html', 'eq. $ 0.00')
        );
        DashTable.getCellById(4, 'ddd').within(
            () => cy.get('.dash-cell-value').should('have.html', 'eq. $ 0.00')
        );
    });
});