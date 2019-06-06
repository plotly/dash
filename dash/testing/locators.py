# pylint: disable=too-few-public-methods
class DashLocatorsMixin(object):
    @property
    def devtools_error_count_locator(self):
        return ".test-devtools-error-count"

    @property
    def dash_entry_locator(self):
        return "#react-entry-point"
