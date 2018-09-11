import DashTable from 'cypress/DashTable';
import DOM from 'cypress/DOM';
import Key from 'cypress/Key';

describe('copy paste', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8082');
    });

    it('can do BE roundtrip on cell modification', () => {
        DashTable.getCell(0, 0).click();
        DOM.focused.type(`1${Key.Enter}`);

        DashTable
            .getCell(0, 0)
            .within(() => cy.get('.cell-value').should('have.html', '10'))
            .then(() => {
                DashTable.getCell(0, 1)
                    .within(() => cy.get('.cell-value').should('have.html', 'MODIFIED'));
            });
    });

    // Commenting this test as Cypress team is having issues with the copy/paste scenario
    // LINK: https://github.com/cypress-io/cypress/issues/2386
    describe('BE roundtrip on copy-paste', () => {
        it('with unsorted, unfiltered data', () => {
            DashTable.getCell(0, 0).click();
            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(1, 0).click();
            DOM.focused.type(`${Key.Meta}v`);

            DashTable
                .getCell(1, 1)
                .within(() => cy.get('.cell-value').should('have.html', 'MODIFIED'));
            DashTable
                .getCell(1, 0)
                .within(() => cy.get('.cell-value').should('have.value', '0'));

            DashTable.getCell(1, 1).click();
            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(2, 1).click();
            DOM.focused.type(`${Key.Meta}v`);

            DashTable
                .getCell(2, 1)
                .within(() => cy.get('.cell-value').should('have.value', 'MODIFIED'));
        });

        it('BE rountrip with sorted, unfiltered data', () => {
            cy.get('tr th.column-0 .filter').click();

            DashTable.getCell(0, 0).click();
            DashTable.getCell(0, 0).within(() => cy.get('.cell-value').should('have.value', '249'));

            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(1, 0).click();
            DOM.focused.type(`${Key.Meta}v`);

            DashTable
                .getCell(1, 1)
                .within(() => cy.get('.cell-value').should('have.html', 'MODIFIED'));
            DashTable
                .getCell(1, 0)
                .within(() => cy.get('.cell-value').should('have.value', '249'));

            DashTable.getCell(1, 1).click();
            DOM.focused.type(`${Key.Meta}c`);

            DashTable.getCell(2, 1).click();
            DOM.focused.type(`${Key.Meta}v`);

            DashTable
                .getCell(2, 1)
                .within(() => cy.get('.cell-value').should('have.value', 'MODIFIED'));
        });
    });
});
