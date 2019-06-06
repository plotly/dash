class DashPageMixin(object):
    @property
    def devtools_error_count_locator(self):
        return ".test-devtools-error-count"

    @property
    def dash_entry_locator(self):
        return "#react-entry-point"

    @property
    def redux_state_paths(self):
        return self.driver.execute_script(
            "return window.store.getState().paths"
        )

    @property
    def redux_state_rqs(self):
        return self.driver.execute_script(
            "return window.store.getState().requestQueue"
        )
