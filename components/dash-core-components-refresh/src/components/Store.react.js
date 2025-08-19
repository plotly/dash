import {equals, isNil} from 'ramda';
import React from 'react';
import PropTypes from 'prop-types';

/**
 * Abstraction for the memory storage_type to work the same way as local/session
 *
 * Each memory Store component get it's own MemStore.
 */
class MemStore {
    constructor() {
        this._data = {};
        this._modified = -1;
    }

    getItem(key) {
        return this._data[key];
    }

    setItem(key, value) {
        this._data[key] = value;
        this.setModified(key);
    }

    removeItem(key) {
        delete this._data[key];
        this.setModified(key);
    }

    // noinspection JSUnusedLocalSymbols
    setModified(_) {
        this._modified = Date.now();
    }

    // noinspection JSUnusedLocalSymbols
    getModified(_) {
        return this._modified;
    }
}

/**
 * Abstraction for local/session storage_type.
 *
 * Single instances for localStorage, sessionStorage
 */
class WebStore {
    constructor(storage) {
        this._storage = storage;
    }

    getItem(key) {
        try {
            return JSON.parse(this._storage.getItem(key));
        } catch (e) {
            // in case we somehow got a non-JSON value in storage,
            // just ignore it.
            return null;
        }
    }

    setItem(key, value) {
        this._storage.setItem(key, JSON.stringify(value));
        this.setModified(key);
    }

    removeItem(key) {
        this._storage.removeItem(key);
        this._storage.removeItem(`${key}-timestamp`);
    }

    setModified(key) {
        this._storage.setItem(`${key}-timestamp`, Date.now());
    }

    getModified(key) {
        return (
            Number.parseInt(this._storage.getItem(`${key}-timestamp`), 10) || -1
        );
    }
}

/**
 * Easily keep data on the client side with this component.
 * The data is not inserted in the DOM.
 * Data can be in memory, localStorage or sessionStorage.
 * The data will be kept with the id as key.
 */
export default class Store extends React.Component {
    constructor(props) {
        super(props);

        if (props.storage_type === 'local') {
            this._backstore = new WebStore(window.localStorage);
        } else if (props.storage_type === 'session') {
            this._backstore = new WebStore(window.sessionStorage);
        } else if (props.storage_type === 'memory') {
            this._backstore = new MemStore();
        }

        this.onStorageChange = this.onStorageChange.bind(this);
    }

    onStorageChange(e) {
        const {id, setProps} = this.props;
        if (e.key === id && setProps && e.newValue !== e.oldValue) {
            setProps({
                data: JSON.parse(e.newValue),
                modified_timestamp: this._backstore.getModified(id),
            });
        }
    }

    UNSAFE_componentWillMount() {
        const {setProps, id, data, storage_type} = this.props;
        if (storage_type !== 'memory') {
            window.addEventListener('storage', this.onStorageChange);
        }

        const old = this._backstore.getItem(id);
        if (isNil(old) && !isNil(data)) {
            // Initial data mount
            this._backstore.setItem(id, data);
            setProps({
                modified_timestamp: this._backstore.getModified(id),
            });
            return;
        }

        if (!equals(old, data)) {
            setProps({
                data: old,
                modified_timestamp: this._backstore.getModified(id),
            });
        }
    }

    componentWillUnmount() {
        if (this.props.storage_type !== 'memory') {
            window.removeEventListener('storage', this.onStorageChange);
        }
    }

    componentDidUpdate() {
        const {data, id, clear_data, setProps} = this.props;
        if (clear_data) {
            this._backstore.removeItem(id);
            setProps({
                clear_data: false,
                data: null,
                modified_timestamp: this._backstore.getModified(id),
            });
            return;
        }
        const old = this._backstore.getItem(id);
        // Only set the data if it's not the same data.
        // If the new data is undefined, we got here by overwriting the entire
        // component with a new copy that has no `data` specified - so pull back
        // out the old value.
        // Note: this still allows you to set data to null
        if (!equals(data, old)) {
            if (data === undefined) {
                setProps({data: old});
            } else {
                this._backstore.setItem(id, data);
                setProps({
                    modified_timestamp: this._backstore.getModified(id),
                });
            }
        }
    }

    render() {
        return null;
    }
}

Store.defaultProps = {
    storage_type: 'memory',
    clear_data: false,
    modified_timestamp: -1,
};

Store.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string.isRequired,

    /**
     * The type of the web storage.
     *
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    storage_type: PropTypes.oneOf(['local', 'session', 'memory']),

    /**
     * The stored data for the id.
     */
    data: PropTypes.oneOfType([
        PropTypes.object,
        PropTypes.array,
        PropTypes.number,
        PropTypes.string,
        PropTypes.bool,
    ]),

    /**
     * Set to true to remove the data contained in `data_key`.
     */
    clear_data: PropTypes.bool,

    /**
     * The last time the storage was modified.
     */
    modified_timestamp: PropTypes.number,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,
};
