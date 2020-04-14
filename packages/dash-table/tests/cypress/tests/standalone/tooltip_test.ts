import DashTable from 'cypress/DashTable';

import { AppMode, AppFlavor } from 'demo/AppMode';

describe(`tooltips, mode=${AppMode.Tooltips}`, () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.Tooltips}`);
        DashTable.toggleScroll(false);
    });

    it('displays html', () => {
        DashTable.getCellById(0, 'bbb-readonly').trigger('mouseover', { force: true });
        cy.get('.dash-table-tooltip').should('not.be.visible');
        cy.wait(0);
        cy.get('.dash-table-tooltip').should('be.visible');
        cy.get('.dash-table-tooltip').within(t => expect(t[0].innerHTML).to.not.be.undefined);
        cy.get('.dash-table-tooltip').within(t => expect(!!t[0].children && !!t[0].children.length).to.be.true);
        cy.wait(1500);
        cy.get('.dash-table-tooltip').should('not.be.visible');
    });

    it('displays text', () => {
        DashTable.getCellById(6, 'ccc').trigger('mouseover', { force: true });
        cy.get('.dash-table-tooltip').should('not.be.visible');
        cy.wait(0);
        cy.get('.dash-table-tooltip').should('be.visible');
        cy.get('.dash-table-tooltip').within(t => expect(t[0].innerText).to.equal('There is death in the hane'));
        cy.get('.dash-table-tooltip').within(t => expect(!!t[0].children && !!t[0].children.length).to.be.false);
        cy.wait(1500);
        cy.get('.dash-table-tooltip').should('not.be.visible');
    });
});

describe(`tooltips, mode=${AppMode.Tooltips},flavor=${[AppFlavor.FixedColumnPlus1, AppFlavor.FixedRowPlus1].join(';')}`, () => {
    beforeEach(() => {
        cy.visit(`http://localhost:8080?mode=${AppMode.Tooltips}&flavor=${[AppFlavor.FixedColumnPlus1, AppFlavor.FixedRowPlus1].join(';')}`);
    });

    it('displays in fixed column', () => {
        DashTable.getCellById(6, 'rows').trigger('mouseover');
        cy.get('.dash-table-tooltip').should('not.be.visible');
        cy.wait(0);
        cy.get('.dash-table-tooltip').should('be.visible');
        cy.get('.dash-table-tooltip').then(t => {
            expect(t[0].innerText).to.equal('Learn the eyestealing tesuji');
            expect(!!t[0].children && !!t[0].children.length).to.equal(false);

            const bounds = t[0].getBoundingClientRect();

            DashTable.getCellById(6, 'rows').then(table => {
                const cellBounds = table[0].getBoundingClientRect();

                expect(bounds.top).to.be.greaterThan(cellBounds.top + cellBounds.height);
            });
        });
        cy.wait(1500);
        cy.get('.dash-table-tooltip').should('not.be.visible');
    });

    it('displays in fixed row', () => {
        DashTable.getCellById(0, 'ddd').trigger('mouseover');
        cy.get('.dash-table-tooltip').should('not.be.visible');
        cy.wait(0);
        cy.get('.dash-table-tooltip').should('be.visible');
        cy.get('.dash-table-tooltip').then(t => {
            expect(t[0].innerText).to.equal('Hane, Cut, Placement\n\n');

            const bounds = t[0].getBoundingClientRect();

            DashTable.getCellById(0, 'ddd').then(table => {
                const cellBounds = table[0].getBoundingClientRect();

                expect(bounds.top).to.be.greaterThan(cellBounds.top + cellBounds.height);
            });
        });
        cy.wait(1500);
        cy.get('.dash-table-tooltip').should('not.be.visible');
    });

    it('displays in fixed row & column', () => {
        DashTable.getCellById(0, 'rows').trigger('mouseover');
        cy.get('.dash-table-tooltip').should('not.be.visible');
        cy.wait(0);
        cy.get('.dash-table-tooltip').should('be.visible');
        cy.get('.dash-table-tooltip').then(t => {
            expect(t[0].innerText).to.equal('Learn the eyestealing tesuji');
            expect(!!t[0].children && !!t[0].children.length).to.equal(false);

            const bounds = t[0].getBoundingClientRect();

            DashTable.getCellById(0, 'rows').then(table => {
                const cellBounds = table[0].getBoundingClientRect();

                expect(bounds.top).to.be.greaterThan(cellBounds.top + cellBounds.height);
            });
        });
        cy.wait(1500);
        cy.get('.dash-table-tooltip').should('not.be.visible');
    });
});