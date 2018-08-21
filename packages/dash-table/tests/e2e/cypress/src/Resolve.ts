export default function resolve<T>(chain: Cypress.Chainable<T>) {
    return new Cypress.Promise<T>(r => r(chain as any));
}