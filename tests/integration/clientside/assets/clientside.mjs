import {display} from "./clientsideModule.mjs";

window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside_module = Object.assign({}, window.dash_clientside.clientside_module, {
	display
});
