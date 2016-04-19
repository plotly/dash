'use strict';

import {EventEmitter} from 'events';
import assign from 'object-assign';

const CHANGE_EVENT = 'change';

var BaseStore = assign({}, EventEmitter.prototype, {

    emitChange: function() {
        var args = [CHANGE_EVENT].concat(Array.prototype.slice.call(arguments));
        // Finish the dispatch before emitting the change.
        process.nextTick(() => this.emit.apply(this, args));
    },

    addChangeListener: function (callback) {
        this.on(CHANGE_EVENT, callback);
    },

    removeChangeListener: function (callback) {
        this.removeListener(CHANGE_EVENT, callback);
    },

    extend: function(obj){
        return assign({}, BaseStore, obj);
    }
});

module.exports = BaseStore;
