'use strict';

import {AppStore} from '../stores/AppStore';

/**
 * @param  {Store} Store
 * @return {Object} A react mixin with necessary methods to assemble a Store and a component
 */
module.exports = {

    /**
     * Listen to the Store for Change Events.
     * Change Events in the store will now trigger our _onChange Handler.
     */
    componentDidMount: function() {
        AppStore.addChangeListener(this._onChange);
    },

    /**
     * Clean up our listener from the Store when component unmounts.
     */
    componentWillUnmount: function() {
        AppStore.removeChangeListener(this._onChange);
    }
};
