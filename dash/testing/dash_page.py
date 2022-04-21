from bs4 import BeautifulSoup


class DashPageMixin:
    def _get_dash_dom_by_attribute(self, attr):
        return BeautifulSoup(
            self.find_element(self.dash_entry_locator).get_attribute(attr), "lxml"
        )

    @property
    def devtools_error_count_locator(self):
        return ".test-devtools-error-count"

    @property
    def dash_entry_locator(self):
        return "#react-entry-point"

    @property
    def dash_outerhtml_dom(self):
        return self._get_dash_dom_by_attribute("outerHTML")

    @property
    def dash_innerhtml_dom(self):
        return self._get_dash_dom_by_attribute("innerHTML")

    @property
    def redux_state_paths(self):
        return self.driver.execute_script(
            """
            var p = window.store.getState().paths;
            return {strs: p.strs, objs: p.objs}
            """
        )

    @property
    def redux_state_rqs(self):
        return self.driver.execute_script(
            """

            // Check for legacy `pendingCallbacks` store prop (compatibility for Dash matrix testing)
            var pendingCallbacks = window.store.getState().pendingCallbacks;
            if (pendingCallbacks) {
                return pendingCallbacks.map(function(cb) {
                    var out = {};
                    for (var key in cb) {
                        if (typeof cb[key] !== 'function') { out[key] = cb[key]; }
                    }
                    return out;
                });
            }

            // Otherwise, use the new `callbacks` store prop
            var callbacksState =  Object.assign({}, window.store.getState().callbacks);
            delete callbacksState.stored;
            delete callbacksState.completed;

            return Array.prototype.concat.apply([], Object.values(callbacksState));
            """
        )

    @property
    def redux_state_is_loading(self):
        return self.driver.execute_script(
            """
            return window.store.getState().isLoading;
            """
        )

    @property
    def window_store(self):
        return self.driver.execute_script("return window.store")

    def _wait_for_callbacks(self):
        return (not self.window_store) or self.redux_state_rqs == []

    def get_local_storage(self, store_id="local"):
        return self.driver.execute_script(
            f"return JSON.parse(window.localStorage.getItem('{store_id}'));"
        )

    def get_session_storage(self, session_id="session"):
        return self.driver.execute_script(
            f"return JSON.parse(window.sessionStorage.getItem('{session_id}'));"
        )

    def clear_local_storage(self):
        self.driver.execute_script("window.localStorage.clear()")

    def clear_session_storage(self):
        self.driver.execute_script("window.sessionStorage.clear()")

    def clear_storage(self):
        self.clear_local_storage()
        self.clear_session_storage()
