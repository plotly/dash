import DashTable from 'cypress/DashTable';

describe('dash_test', () => {
    beforeEach(() => {
        cy.visit('http://localhost:8081');
    });

    it('can get cell', () => {
        DashTable.getCell(0, 0).click();
        DashTable.getCellInput(0, 0).should('have.value', '0');

        cy.get('button.next-page').click();
        DashTable.getCellInput(0, 0).should('have.value', '250');
    });
});
