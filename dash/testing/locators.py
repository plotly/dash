class DashLocatorsMixin(object):
    def dev_tools_error_counts(self):
        return int(
            self.driver.find_element_by_css_selector(
                ".test-devtools-error-count"
            ).text
        )
