import registry from '../src/registry';

describe('registry', () => {

    afterEach(() => {
        delete window.TestNamespace;
    });

    describe('resolving nested components', () => {
        beforeEach(() => {
            window.TestNamespace = {
                TestComponent: {
                    NestedComponent: 'test',
                },
            };
        });

        test('referencing nested components', () => {
            const component = {
                type: 'TestComponent.NestedComponent',
                namespace: 'TestNamespace',
            };
            const actual = registry.resolve(component);
            expect(actual).toEqual('test');
        });
    });

    describe('resolving standard components', () => {
        beforeEach(() => {
            window.TestNamespace = {
                TestComponent: 'test',
            };
        });

        test('referencing nested components', () => {
            const component = {
                type: 'TestComponent',
                namespace: 'TestNamespace',
            };
            const actual = registry.resolve(component);
            expect(actual).toEqual('test');
        });
    });
});
