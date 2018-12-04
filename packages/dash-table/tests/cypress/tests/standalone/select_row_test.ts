import DashTable from 'cypress/DashTable';

import { AppMode } from 'demo/AppMode';

Object.values(AppMode).forEach(mode => {
    describe(`select row, mode=${mode}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${mode}`);
            DashTable.toggleScroll(false);
        });

        describe('fe pagination & sort', () => {
            it('can select row', () => {
                DashTable.getSelect(0).within(() => cy.get('input').click());
                DashTable.getSelect(0).within(() => cy.get('input').should('be.checked'));
            });

            it('can select row when sorted', () => {
                cy.get('tr th.column-0 .sort').last().click({ force: true });
                DashTable.getSelect(0).within(() => cy.get('input').click());
                DashTable.getSelect(0).within(() => cy.get('input').should('be.checked'));
            });

            it('select, sort, new row is not selected', () => {
                DashTable.getSelect(0).within(() => cy.get('input').click());
                DashTable.getSelect(0).within(() => cy.get('input').should('be.checked'));
                cy.get('tr th.column-0 .sort').last().click({ force: true }).click({ force: true });
                DashTable.getSelect(0).within(() => cy.get('input').should('not.be.checked'));
            });
        });
    });
});