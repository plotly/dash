declare namespace Cypress {
    interface Chainable {
        tab(shift?: Boolean, ctrl?: Boolean): Cypress.Chainable<JQuery<HTMLElement>>;
    }
}