import DashTable from 'cypress/DashTable';
import { AppMode, AppFlavor } from 'demo/AppMode';

describe(`edit, mode=${AppMode.Typed}`, () => {
    describe(`edit headers, mode=${AppMode.Typed}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Typed}`);
            DashTable.toggleScroll(false);
        });

        it('changing the column 0 header should not change any column 0 headers below it', () => {
            cy.window().then((win: any) => {
                cy.stub(win, 'prompt').returns('Hello');
            });
            cy.get('.dash-header.column-0:not(.phantom-cell) .column-header--edit').eq(0).click();
            cy.get('.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', `Hello`);
            cy.get('table > tbody > tr:nth-child(2) > th.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', `rows`);
        });

        it('changing the column 1 header should not change any other headers', () => {
            cy.window().then((win: any) => {
                cy.stub(win, 'prompt').returns('Aloha');
            });
            cy.get('.dash-header.column-1:not(.phantom-cell) .column-header--edit').eq(0).click();
            cy.get('.dash-header.column-1:not(.phantom-cell) > div > span:last-child').should('have.html', `Aloha`);
            cy.get('.dash-header.column-2:not(.phantom-cell) > div > span:last-child').should('have.html', `City`);
        });
    });

    describe(`edit headers, mode=${AppMode.Default},flavor=${AppFlavor.Merged}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Default}&flavor=${AppFlavor.Merged}`);
            DashTable.toggleScroll(false);
        });
        it('changing the column 0 header should not change any column 0 headers below it', () => {
            cy.window().then((win: any) => {
                cy.stub(win, 'prompt').returns('Otter');
            });
            cy.get('.dash-header.column-0:not(.phantom-cell) .column-header--edit').eq(0).click();
            cy.get('.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', `Otter`);
            cy.get('table > tbody > tr:nth-child(2) > th.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', `rows`);
        });
        it('changing the column 1 header should not change any other headers', () => {
            cy.window().then((win: any) => {
                cy.stub(win, 'prompt').returns('Aloha');
            });
            cy.get('.dash-header.column-1:not(.phantom-cell) .column-header--edit').eq(0).click();
            cy.get('.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', `rows`);
            cy.get('.dash-header.column-1:not(.phantom-cell) > div > span:last-child').should('have.html', `Aloha`);
            cy.get('.dash-header.column-6:not(.phantom-cell) > div > span:last-child').should('have.html', ``);
        });
    });

    describe(`edit headers while some columns are hidden`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Actionable}&flavor=${AppFlavor.Merged}`);
            DashTable.toggleScroll(false);
        })
        it('preserves hidden columns unchanged when editing visible names', () => {
            cy.window().then((win: any) => {
                cy.stub(win, 'prompt').returns('Chill');
            });
            // hide 3 columns - one at the start of a merged set, one in the middle, one not in the set
            cy.get('.column-8:not(.phantom-cell) .column-header--hide').click({force: true});
            cy.get('.column-6:not(.phantom-cell) .column-header--hide').click({force: true});
            cy.get('.column-1:not(.phantom-cell) .column-header--hide').click({force: true});
            // edit the merged name
            cy.get('.dash-header.column-5:not(.phantom-cell) .column-header--edit').eq(1).click({force: true});
            // re-show the hidden columns
            cy.get('.show-hide').click();
            cy.get('.show-hide-menu-item input').eq(1).click();
            cy.get('.show-hide-menu-item input').eq(6).click();
            cy.get('.show-hide-menu-item input').eq(8).click();
            // all columns still exist
            cy.get('.dash-header.column-9:not(.phantom-cell) .column-header-name').should('have.html', 'Temperature-RO');
            // the columns that were hidden when the merged name was changed
            // still changed name - so they're still all merged
            cy.get('.dash-header.column-6[colspan="4"]:not(.phantom-cell) .column-header-name').eq(1).should('have.html', 'Chill');
        });
    });

    describe('edit headers, canceled edit', () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.SingleHeaders}`);
            DashTable.toggleScroll(false);
        });
        it('preserves column name if edit is canceled', () => {
            cy.window().then((win: any) => {
                // user presses cancel -> prompt returns null
                cy.stub(win, 'prompt').returns(null);
            });
            cy.get('.dash-header.column-0:not(.phantom-cell) .column-header--edit').eq(0).click();
            cy.get('.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', 'rows');
        });
    });

    describe(`edit headers, mode=${AppMode.SingleHeaders}`, () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.SingleHeaders}`);
            DashTable.toggleScroll(false);
        });
        it('allows changing single-row column 0 header', () => {
            cy.window().then((win: any) => {
                cy.stub(win, 'prompt').returns('Russia');
            });
            cy.get('.dash-header.column-0:not(.phantom-cell) .column-header--edit').eq(0).click();
            cy.get('.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', 'Russia');
        });
        it('changing the column 1 header should not change any other headers', () => {
            cy.window().then((win: any) => {
                cy.stub(win, 'prompt').returns('Alaska');
            });
            cy.get('.dash-header.column-1:not(.phantom-cell) .column-header--edit').eq(0).click();
            cy.get('.dash-header.column-0:not(.phantom-cell) > div > span:last-child').should('have.html', 'rows');
            cy.get('.dash-header.column-1:not(.phantom-cell) > div > span:last-child').should('have.html', 'Alaska');
        });
    });
});
