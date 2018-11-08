import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';

describe('select row', () => {
    describe('be pagination & sort', () => {
        beforeEach(() => cy.visit('http://localhost:8081'));

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
            cy.get('tr th.column-0 .sort').last().click({ force: true });
            DashTable.getSelect(0).within(() => cy.get('input').should('not.be.checked'));
        });
    });

    describe('fe pagination & sort', () => {
        beforeEach(() => cy.visit('http://localhost:8083'));

        it('derived selected rows are correct, no sort / filter', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(1).within(() => cy.get('input').click());

            cy.get('#derived_viewport_selected_rows_container').should($container => {
                expect($container.first()[0].innerText).to.be.oneOf([`[0, 1]`, `[1, 0]`]);
            });

            cy.get('#derived_virtual_selected_rows_container').should($container => {
                expect($container.first()[0].innerText).to.be.oneOf([`[0, 1]`, `[1, 0]`]);
            });
        });

        it('derived selected rows are correct, with filter', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(1).within(() => cy.get('input').click());
            DashTable.getSelect(2).within(() => cy.get('input').click());

            cy.get('tr th.column-0.dash-filter input').type(`is even${Key.Enter}`);

            cy.get('#derived_viewport_selected_rows_container').should($container => {
                expect($container.first()[0].innerText).to.be.oneOf([`[0, 1]`, `[1, 0]`]);
            });

            cy.get('#derived_virtual_selected_rows_container').should($container => {
                expect($container.first()[0].innerText).to.be.oneOf([`[0, 1]`, `[1, 0]`]);
            });
        });

        it('derived selected rows are correct, with filter & sort', () => {
            DashTable.getSelect(0).within(() => cy.get('input').click());
            DashTable.getSelect(1).within(() => cy.get('input').click());

            cy.get('tr th.column-0.dash-filter input').type(`is even${Key.Enter}`);
            cy.get('tr th.column-0 .sort').last().click({ force: true });
            cy.get('tr th.column-0 .sort').last().click({ force: true });

            DashTable.getSelect(0).within(() => cy.get('input').click());

            cy.get('#derived_viewport_selected_rows_container').should($container => {
                expect($container.first()[0].innerText).to.equal(`[0]`);
            });

            cy.get('#derived_virtual_selected_rows_container').should($container => {
                expect($container.first()[0].innerText).to.be.oneOf([`[0, 499]`, `[499, 0]`]);
            });
        });
    });
});