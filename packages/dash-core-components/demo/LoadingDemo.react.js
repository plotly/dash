import React from 'react';

import {Loading, Tabs, Tab} from '../src';

const LoadingDemo = () => {
    const loading_state = {
        is_loading: true,
        prop_name: 'layout',
        component_name: 'Demo',
    };
    return (
        <Tabs>
            <Tab value='tab-1' label='All Spinners (custom colors, no fullscreen)'>
                <div>
                    <Loading loading_state={loading_state} type="default" color="gold" />
                    <Loading loading_state={loading_state} type="circle" color="cyan"/>
                    <Loading loading_state={loading_state} type="dot" color="hotpink"/>
                    <Loading loading_state={loading_state} type="cube" color="greenyellow"/>
                    <Loading loading_state={loading_state} type="graph" />
                </div>
            </Tab>
            <Tab value='tab-2' label='All Spinners (no fullscreen, debug)'>
                <div>
                    <Loading loading_state={loading_state} debug={true} type="default" />
                    <Loading loading_state={loading_state} debug={true} type="circle" />
                    <Loading loading_state={loading_state} debug={true} type="dot" />
                    <Loading loading_state={loading_state} debug={true} type="cube" />
                    <Loading loading_state={loading_state} debug={true} type="graph" />
                </div>
            </Tab>
            <Tab value='tab-3' label='Fullscreen Default spinner'>
                <Loading loading_state={loading_state} type="default" fullscreen={true} />
            </Tab>
            <Tab value='tab-4' label='Fullscreen Circle spinner'>
                <Loading loading_state={loading_state} type="circle" fullscreen={true} />
            </Tab>
            <Tab value='tab-5' label='Fullscreen Dot spinner'>
                <Loading loading_state={loading_state} type="dot" fullscreen={true} />
            </Tab>
            <Tab value='tab-6' label='Fullscreen Graph spinner'>
                <Loading loading_state={loading_state} type="graph" fullscreen={true} />
            </Tab>
            <Tab value='tab-7' label='Fullscreen Cube spinner'>
                <Loading loading_state={loading_state} type="cube" fullscreen={true} />
            </Tab>
        </Tabs>
    );
};

export default LoadingDemo;
