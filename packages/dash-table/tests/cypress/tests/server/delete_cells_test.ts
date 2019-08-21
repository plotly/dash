import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

describe('delete cells', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8082');
    });

    describe('unsorted data', () => {
        it('can delete single cell', () => {
            DashTable.getCell(0, 1).click();
            DashTable.getCell(0, 1).within(() => cy.get('.dash-cell-value').should('not.have.value', ''));
            DOM.focused.type(`${Key.Backspace}${Key.ArrowDown}`);
            DashTable.getCell(0, 1).within(() => cy.get('.dash-cell-value').should('have.html', ''));
        });

        it('can delete multiple cells', () => {
            DashTable.getCell(0, 1).click();
            DOM.focused.type(`${Key.Shift}${Key.ArrowDown}${Key.ArrowRight}`);
            DOM.focused.type(`${Key.Backspace}`);
            DashTable.getCell(0, 0).click();

            for (let row = 0; row <= 1; ++row) {
                for (let column = 1; column <= 2; ++column) {
                    DashTable.getCell(row, column).within(() => cy.get('.dash-cell-value').should('have.html', ''));
                }
            }
        });
    });

    describe('sorted data', () => {
        beforeEach(() => {
            cy.get('tr th.column-0 .column-header--sort').last().click();
        });

        it('can delete single cell', () => {
            DashTable.getCell(0, 1).click();
            DashTable.getCell(0, 1).within(() => cy.get('.dash-cell-value').should('not.have.value', ''));
            DOM.focused.type(`${Key.Backspace}${Key.ArrowDown}`);
            DashTable.getCell(0, 1).within(() => cy.get('.dash-cell-value').should('have.html', ''));
        });

        it('can delete multiple cells', () => {
            DashTable.getCell(0, 1).click();
            DOM.focused.type(`${Key.Shift}${Key.ArrowDown}${Key.ArrowRight}`);
            DOM.focused.type(`${Key.Backspace}`);
            DashTable.getCell(0, 0).click();

            for (let row = 0; row <= 1; ++row) {
                for (let column = 1; column <= 2; ++column) {
                    DashTable.getCell(row, column).within(() => cy.get('.dash-cell-value').should('have.html', ''));
                }
            }
        });
    });
});
