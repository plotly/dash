import {DashRenderer} from './DashRenderer';
import ReactDOM from 'react-dom';
import AppProvider from './AppProvider.react';
import { useState } from 'react';



// make DashRenderer globally available
window.DashRenderer = DashRenderer;


// hooks and config for the dash applications
const hooks = { request_pre: null, request_post: null};
const config = {
    "url_base_pathname": null,
    "requests_pathname_prefix": "/",
    "ui": false,
    "props_check": false,
    "show_undo_redo": false
};

const config2 = {
    "url_base_pathname": null,
    "requests_pathname_prefix": "/second",
    "ui": false,
    "props_check": false,
    "show_undo_redo": false
};


const AppComponent = () => {
    const [app, setApp] = useState('app1');


    return (<>
        { app === 'app1' && <AppProvider hooks={hooks} dashConfig={config}  /> }
        { app === 'app2' && <AppProvider hooks={hooks} dashConfig={config2} /> }
        <button onClick={() => { console.log('clicked'); setApp(app === 'app1' ? 'app2' : 'app1' ) }}> Switch </button>
        </>);
};


ReactDOM.render(
    <>
        <AppComponent/>
    </>
     ,
    document.getElementById('react-entry-point')
);


export { AppProvider }
