import DashTable from 'cypress/DashTable';
import Key from 'cypress/Key';
import { AppMode, AppFlavor } from 'demo/AppMode';

describe('markdown cells', () => {
    describe('sorting', () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Markdown}`);
        });

        it('headers', () => {
            // raw value: {row number % 6} pound symbols followed by "row {row number}"
            // displayed value: "row {row number}"
            cy.get('tr th.column-0:not(.phantom-cell) .column-header--sort').click({ force: true });

            // rows 1, 10, 100, 1000 all have 4 pound symbols
            // row 1001 has 5 pound symbols and row 1002 has 0 pound symbols;
            // first cell should have displayed value "1002"
            DashTable.getCellById(0, 'markdown-headers').within(() => cy.get('.dash-cell-value > p').should('have.html', 'row 1002'));

            cy.get('tr th.column-0:not(.phantom-cell) .column-header--sort').last().click({ force: true });
            // rows 999, 998, 997, 996 have, respectively, 3, 2, 1, and 0 pound symbols;
            // first cell should have displayed value "##### row 995"
            DashTable.getCellById(0, 'markdown-headers').within(() => cy.get('.dash-cell-value > h5').should('have.html', 'row 995'));
        });

        it('emphasized text', () => {
            // raw value: "*{row number}*" for odd row numbers and "_{row number}_" for even row numbers
            // displayed value: "{row number}"
            cy.get('tr th.column-1:not(.phantom-cell) .column-header--sort').click({ force: true });

            // "*" < "_"; first cell should start with "*", i.e., be in an odd-numbered row
            DashTable.getCellById(0, 'markdown-italics').within(() => cy.get('.dash-cell-value > p > em').should('have.html', '1'));

            cy.get('tr th.column-1:not(.phantom-cell) .column-header--sort').click({ force: true });
            // first cell should start with "_", i.e., be in an even-numbered row
            DashTable.getCellById(0, 'markdown-italics').within(() => cy.get('.dash-cell-value > p > em').should('have.html', '998'));
        });

        it('links', () => {
            // raw value: "[Learn about {row number}](http://en.wikipedia.org/wiki/{row number})"
            // displayed value: "Learn about {row number}"
            cy.get('tr th.column-2:not(.phantom-cell) .column-header--sort').click({ force: true });

            // "]" > "0"; first cell should have row number 1000
            DashTable.getCellById(0, 'markdown-links').within(() => cy.get('.dash-cell-value > p > a').should('have.html', 'Learn about 1000'));
            DashTable.getCellById(0, 'markdown-links').within(() => cy.get('.dash-cell-value > p > a').should('have.attr', 'href', 'http://en.wikipedia.org/wiki/1000'));

            // "]" > "9"; first cell should have row number 9
            cy.get('tr th.column-2:not(.phantom-cell) .column-header--sort').click({ force: true });
            DashTable.getCellById(0, 'markdown-links').within(() => cy.get('.dash-cell-value > p > a').should('have.html', 'Learn about 9'));
            DashTable.getCellById(0, 'markdown-links').within(() => cy.get('.dash-cell-value > p > a').should('have.attr', 'href', 'http://en.wikipedia.org/wiki/9'));
        });

        it('images', () => {
            // raw value: "![{plotly logo}](image alt text {row number})"
            cy.get('tr th.column-8:not(.phantom-cell) .column-header--sort').click({ force: true });

            DashTable.getCellById(0, 'markdown-images').within(() => cy.get('.dash-cell-value > p > img').should('have.attr', 'alt', 'image 1 alt text'));

            cy.get('tr th.column-8:not(.phantom-cell) .column-header--sort').click({ force: true });
            DashTable.getCellById(0, 'markdown-images').within(() => cy.get('.dash-cell-value > p > img').should('have.attr', 'alt', 'image 999 alt text'))
        });

        it('tables', () => {
            // raw value: "
            // Current | Next
            // --- | ---
            // {row number} | {row number + 1}"
            // displayed value: html table with the above entries

            cy.get('tr th.column-4:not(.phantom-cell) .column-header--sort').click({ force: true });

            DashTable.getCellById(0, 'markdown-tables').within(() => cy.get('.dash-cell-value > table > tbody > tr > td').first().should('have.html', '1'));

            cy.get('tr th.column-4:not(.phantom-cell) .column-header--sort').click({ force: true });
            DashTable.getCellById(0, 'markdown-tables').within(() => cy.get('.dash-cell-value > table > tbody > tr > td').first().should('have.html', '999'));
        });
    });

    describe('filtering', () => {
        beforeEach(() => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Markdown}&flavor=${AppFlavor.FilterNative}`);
        });

        it('general', () => {
            DashTable.getFilterById('markdown-headers').click();

            DashTable.focusedType(`row 5`);
            DashTable.getFilterById('markdown-italics').click();

            DashTable.getCellById(0, 'markdown-headers').within(() => cy.get('.dash-cell-value h5').should('have.html', 'row 5'));
            // results should be 5, 51, ..., 59, 500, ..., 599
            cy.get('.dash-spreadsheet .cell-1-1 table tbody tr td.dash-cell.column-0:not(.phantom-cell)').should('have.length', 111);

            DashTable.focusedType(`7`);
            DashTable.getFilterById('markdown-code-blocks').click();

            DashTable.getCellById(0, 'markdown-italics').within(() => cy.get('.dash-cell-value p em').should('have.html', '57'));
            // results should be 57, 507, ..., 567 571, ..., 579, 587, ..., 597
            cy.get('.dash-spreadsheet .cell-1-1 table tbody tr td.dash-cell.column-0:not(.phantom-cell)').should('have.length', 20);

            DashTable.focusedType(`58`);
            DashTable.getFilterById('markdown-quotes').click();

            DashTable.getCellById(0, 'markdown-links').within(() => cy.get('.dash-cell-value p a').should('have.html', 'Learn about 587'));
        });

        describe('links', () => {
            it('by link text', () => {
                DashTable.getFilterById('markdown-links').click();
                DashTable.focusedType(`Learn about 1234`);
                DashTable.focusedType(`${Key.Enter}`);

                cy.get('.dash-spreadsheet .cell-1-1 table tbody tr td.dash-cell.column-2:not(.phantom-cell)').should('have.length', 1);
                DashTable.getCellById(0, 'markdown-links').within(() => cy.get('.dash-cell-value > p > a').should('have.attr', 'href', 'http://en.wikipedia.org/wiki/1234'));
            });

            it('by link value', () => {
                DashTable.getFilterById('markdown-links').click();
                DashTable.focusedType(`/wiki/4321`);
                DashTable.focusedType(`${Key.Enter}`);
                cy.get('.dash-spreadsheet .cell-1-1 table tbody tr td.dash-cell.column-2:not(.phantom-cell)').should('have.length', 1);
                DashTable.getCellById(0, 'markdown-links').within(() => cy.get('.dash-cell-value > p > a').should('have.html', 'Learn about 4321'));

            });
        });

        it('images by alt text', () => {
            DashTable.getFilterById('markdown-images').click();
            DashTable.focusedType(`314`);
            DashTable.focusedType(`${Key.Enter}`);

            cy.get('.dash-spreadsheet .cell-1-1 table tbody tr td.dash-cell.column-8:not(.phantom-cell)').should('have.length', 15);
            DashTable.getCellById(0, 'markdown-images').within(() => cy.get('.dash-cell-value > p > img').should('have.attr', 'alt', 'image 314 alt text'));
        });
    });

    describe('clicking links', () => {
        it('correctly redirects', () => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Markdown}`);
            // change href, since Cypress raises error when navigating away from localhost
            DashTable.getCellById(10, 'markdown-links').within(() => cy.get('.dash-cell-value > p > a').invoke('attr', 'href', '#testlinkclick').click().click());
            cy.url().should('include', `#testlinkclick`);
        });
    });

    describe('loading highlightjs', () => {
        it('loads highlight.js and does not attach hljs to window', () => {
            cy.visit(`http://localhost:8080?mode=${AppMode.Markdown}`);
            // wait for highlight.js to highlight code
            DashTable.getCellById(0, 'markdown-code-blocks').within(() => cy.get('code.language-python span.hljs-title'));
            cy.window().should('not.have.property', 'hljs');
        });
        it('uses window.hljs if defined', () => {
            // define custom hljs object that always returns 'hljs override', and attach it to the window
            cy.on('window:before:load', win => {
                win.hljs = {
                    getLanguage: (lang) => false, // force auto-highlight
                    highlightAuto: (str) => { return { value: 'hljs override' } }
                };
            });
            cy.visit(`http://localhost:8080?mode=${AppMode.Markdown}`);
            DashTable.getCellById(0, 'markdown-code-blocks').within(() => cy.get('code.language-python').should('have.html', 'hljs override'));
        });
    });
});
