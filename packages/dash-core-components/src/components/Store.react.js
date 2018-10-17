import R from 'ramda';
import React from 'react';
import PropTypes from 'prop-types';

function dataCheck(data, old) {
    // Assuming data and old are of the same type.
    if (R.isNil(old) || R.isNil(data)) {
        return true;
    }
    const type = R.type(data);
    if (type === 'Array') {
        if (data.length !== old.length) {
            return true;
        }
        for (let i = 0; i < data.length; i++) {
            if (dataCheck(data[i], old[i])) {
                return true;
            }
        }
    } else if (R.contains(type, ['String', 'Number'])) {
        return old !== data;
    } else if (type === 'Object') {
        return R.any(([k, v]) => dataCheck(v, old[k]))(Object.entries(data));
    }
    return false;
}

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

class WebStore {
    constructor(storage) {
        this._storage = storage;
    }

    getItem(key) {
        return JSON.parse(this._storage.getItem(key));
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

const _localStore = new WebStore(window.localStorage);
const _sessionStore = new WebStore(window.sessionStorage);

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
            this._backstore = _localStore;
        } else if (props.storage_type === 'session') {
            this._backstore = _sessionStore;
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

    componentWillMount() {
        const {setProps, id, data, storage_type} = this.props;
        if (storage_type !== 'memory') {
            window.addEventListener('storage', this.onStorageChange);
        }

        const old = this._backstore.getItem(id);
        if (R.isNil(old) && data) {
            // Initial data mount
            this._backstore.setItem(id, data);
            if (setProps) {
                setProps({
                    modified_timestamp: this._backstore.getModified(id),
                });
            }
            return;
        }

        if (setProps && dataCheck(old, data)) {
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
            if (setProps) {
                setProps({
                    clear_data: false,
                    data: null,
                    modified_timestamp: this._backstore.getModified(id),
                });
            }
        } else if (data) {
            const old = this._backstore.getItem(id);
            // Only set the data if it's not the same data.
            if (dataCheck(data, old)) {
                this._backstore.setItem(id, data);
                if (setProps) {
                    setProps({
                        modified_timestamp: this._backstore.getModified(id),
                    });
                }
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
     * The key of the storage.
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
