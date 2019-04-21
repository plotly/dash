import Tabs from '../../src/components/Tabs.react.js';
import Tab from '../../src/components/Tab.react.js';
import React, {cloneElement} from 'react';
import {mount, render} from 'enzyme';
import DashRendererMock from './mocks/DashRendererMock.react.js';

test('Tabs render', () => {
    const tabs = render(
        <DashRendererMock>
            <Tabs>
                <Tab label="test-tab" />
            </Tabs>
        </DashRendererMock>
    );

    expect(tabs.html()).toBeDefined();
});

describe('All props can be set properly', () => {
    const defaultProps = {
        id: 'test-tabs',
        value: 'tab-one',
        vertical: true,
        mobile_breakpoint: 600,
        colors: {
            border: 'red',
            primary: 'white',
            background: 'blue',
        },
    };
    const app = mount(
        <DashRendererMock>
            <Tabs {...defaultProps}>
                <Tab value="tab-one" />
            </Tabs>
        </DashRendererMock>
    );
    test('props.id =>', () => {
        expect(app.find(Tabs).props().id).toEqual(defaultProps.id);
    });
    test('props.value =>', () => {
        expect(app.find(Tabs).props().value).toEqual(defaultProps.value);
    });
    test('props.vertical =>', () => {
        expect(app.find(Tabs).props().vertical).toEqual(defaultProps.vertical);
    });
    test('props.mobile_breakpoint =>', () => {
        expect(app.find(Tabs).props().mobile_breakpoint).toEqual(
            defaultProps.mobile_breakpoint
        );
    });
    test('props.colors=>', () => {
        expect(app.find(Tabs).props().colors).toEqual(defaultProps.colors);
    });
});

describe('Tabs parses inline styles if they are set', () => {
    const testColor = 'hotpink';
    const testStyle = {
        backgroundColor: testColor,
    };
    const mockSetProps = jest.fn(value => value);
    const tabs = render(
        <Tabs
            id="tabs"
            style={testStyle}
            parent_style={testStyle}
            setProps={mockSetProps}
        >
            <Tab label="test-tab" />
        </Tabs>
    );

    test('props.style =>', () => {
        expect(tabs.find('#tabs').prop('style')['background-color']).toEqual(
            testColor
        );
    });
    test('props.parent_style =>', () => {
        expect(tabs.prop('style')['background-color']).toEqual(testColor);
    });
});
describe('Tabs correctly appends classes', () => {
    const testClass = 'tabs-test';
    const testContentClass = 'tabs-test-content';
    const testParentClass = 'tabs-test-parent';
    let tabs;
    beforeEach(() => {
        tabs = render(
            <Tabs
                id="tabs"
                className={testClass}
                content_className={testContentClass}
                parent_className={testParentClass}
                value="tab-1"
            >
                <Tab value="tab-1" label="test-tab" />
            </Tabs>
        );
    });
    // jsx-24123 className's that get appended by styled-jsx are
    // removed here by using the styled-jsx/babel-test plugin in .babelrc
    test('props.className =>', () => {
        expect(tabs.find('#tabs').prop('class')).toEqual(
            'tab-container ' + testClass
        );
    });
    test('props.content_className =>', () => {
        expect(tabs.find('.tab-content').prop('class')).toEqual(
            'tab-content ' + testContentClass
        );
    });
    test('props.parent_className=>', () => {
        expect(tabs.prop('class')).toEqual('tab-parent ' + testParentClass);
    });
});
describe('Tabs render content correctly', () => {
    test('Tabs render Tab.children in content div', () => {
        const tabs = render(
            <DashRendererMock>
                <Tabs id="tabs" value="tab-1">
                    <Tab id="tab-1" value="tab-1" label="Tab 1">
                        <div>Tab 1 child</div>
                    </Tab>
                    <Tab id="tab-2" value="tab-2" label="Tab 2">
                        <div>Tab 2 child</div>
                    </Tab>
                </Tabs>
            </DashRendererMock>
        );
        const renderedContent = tabs.find('.tab-content').html();
        expect(renderedContent).toEqual('<div>Tab 1 child</div>');
    });
    test('Tabs render correct Tab.children as selected in Tabs.props.value in content div', () => {
        const tabs = render(
            <DashRendererMock>
                <Tabs id="tabs" value="tab-2">
                    <Tab id="tab-1" value="tab-1" label="Tab 1">
                        <div>Tab 1 child</div>
                    </Tab>
                    <Tab id="tab-2" value="tab-2" label="Tab 2">
                        <div>Tab 2 child</div>
                    </Tab>
                </Tabs>
            </DashRendererMock>
        );
        const renderedContent = tabs.find('.tab-content').html();
        expect(renderedContent).toEqual('<div>Tab 2 child</div>');
    });
    test('Tabs render Tab.children in content div, even if no Tabs.props.value is given', () => {
        const tabs = render(
            <DashRendererMock>
                <Tabs id="tabs">
                    <Tab id="tab-1" value="tab-1" label="Tab 1">
                        <div>Tab 1 child</div>
                    </Tab>
                    <Tab id="tab-2" value="tab-2" label="Tab 2">
                        <div>Tab 2 child</div>
                    </Tab>
                </Tabs>
            </DashRendererMock>
        );
        const renderedContent = tabs.find('.tab-content').html();
        expect(renderedContent).toEqual('<div>Tab 1 child</div>');
    });
    test('Tabs render Tab.children in content div, even if no Tabs.props.value is given, and Tab components have empty values', () => {
        const tabs = render(
            <DashRendererMock>
                <Tabs>
                    <Tab>
                        <div>Tab 1 child</div>
                    </Tab>
                    <Tab>
                        <div>Tab 2 child</div>
                    </Tab>
                </Tabs>
            </DashRendererMock>
        );
        const renderedContent = tabs.find('.tab-content').html();
        expect(renderedContent).toEqual('<div>Tab 1 child</div>');
    });
});
describe('Tabs handle Tab selection logic', () => {
    let tabs;
    beforeEach(() => {
        tabs = mount(
            <DashRendererMock>
                <Tabs id="tabs" value="tab-1">
                    <Tab id="tab-1" value="tab-1" label="Tab 1">
                        <div>Tab 1 child</div>
                    </Tab>
                    <Tab id="tab-2" value="tab-2" label="Tab 2">
                        <div>Tab 2 child</div>
                    </Tab>
                </Tabs>
            </DashRendererMock>
        );
    });
    test('Tab can be clicked and will display its content', () => {
        tabs.find('[value="tab-2"]').simulate('click');
        const renderedContent = tabs.find(Tab).html();
        expect(renderedContent).toEqual('<div>Tab 2 child</div>');
    });
});
describe('Tabs can be used 2 ways', () => {
    test('With Dash callbacks, using setProps()', () => {
        const mockSetProps = jest.fn(value => value);
        const tabs = mount(
            <Tabs id="tabs" setProps={mockSetProps}>
                <Tab value="custom-tab-1" id="tab-1" label="Tab 1">
                    <div>Tab 1 child</div>
                </Tab>
                <Tab value="custom-tab-2" id="tab-2" label="Tab 2">
                    <div>Tab 2 child</div>
                </Tab>
            </Tabs>
        );

        expect(mockSetProps).toBeCalledTimes(1);
        tabs.find('[value="custom-tab-2"]').simulate('click');
        expect(mockSetProps).toBeCalledTimes(2);
        expect(mockSetProps.mock.results[1].value.value).toEqual(
            'custom-tab-2'
        );

        tabs.find('[value="custom-tab-1"]').simulate('click');
        expect(mockSetProps).toBeCalledTimes(3);
        expect(mockSetProps.mock.results[2].value.value).toEqual(
            'custom-tab-1'
        );
    });
});
describe('Tabs can have null children', () => {
    test('Try to create a Tabs with null children', () => {
        mount(
            <DashRendererMock>
                <Tabs id="tabs" />
            </DashRendererMock>
        );
    });
});
