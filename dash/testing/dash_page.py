from typing import Any, Optional, Protocol, cast, runtime_checkable

from bs4 import BeautifulSoup

# directive needed because protocol classes are so brief
# pylint: disable=too-few-public-methods


@runtime_checkable
class WebElement(Protocol):
    """Protocol for WebElement-like objects with get_attribute."""

    def get_attribute(self, name: str) -> str:
        ...


@runtime_checkable
class WebDriver(Protocol):
    """Protocol for WebDriver-like objects with execute_script."""

    def execute_script(self, script: str, *args: Any) -> Any:
        ...


class DashPageMixin:
    """Mixin class for Dash page with DOM access methods.

    This mixin is intended to be used with a class that provides:
    1. A 'driver' attribute with execute_script method
    2. A 'find_element' method that returns elements with get_attribute method

    The mixin provides properties like dash_entry_locator and methods to
    interact with the Dash application's DOM and state.
    """

    driver: WebDriver  # Expected to be provided by the parent class

    def find_element(self, locator: str) -> WebElement:
        """Find an element by locator.

        This is expected to be implemented by the parent class.
        """
        raise NotImplementedError(
            "find_element must be implemented by the parent class"
        )

    @property
    def dash_entry_locator(self) -> str:
        """CSS selector for Dash app entry point."""
        return "#react-entry-point"

    @property
    def devtools_error_count_locator(self) -> str:
        """CSS selector for devtools error count."""
        return ".test-devtools-error-count"

    def _get_dash_dom_by_attribute(self, attr: str) -> BeautifulSoup:
        """Get BeautifulSoup representation of element's attribute."""
        element = self.find_element(self.dash_entry_locator)
        return BeautifulSoup(element.get_attribute(attr), "lxml")

    @property
    def dash_outerhtml_dom(self) -> BeautifulSoup:
        """Get BeautifulSoup representation of outerHTML."""
        return self._get_dash_dom_by_attribute("outerHTML")

    @property
    def dash_innerhtml_dom(self) -> BeautifulSoup:
        """Get BeautifulSoup representation of innerHTML."""
        return self._get_dash_dom_by_attribute("innerHTML")

    @property
    def redux_state_paths(self) -> dict[str, Any]:
        """Get Redux state paths."""
        return cast(
            dict[str, Any],
            self.driver.execute_script(
                """
            var p = window.store.getState().paths;
            return {strs: p.strs, objs: p.objs}
            """
            ),
        )

    @property
    def redux_state_rqs(self) -> list[dict[str, Any]]:
        """Get Redux state request queue."""
        return cast(
            list[dict[str, Any]],
            self.driver.execute_script(
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
            ),
        )

    @property
    def redux_state_is_loading(self) -> bool:
        """Check if Redux state is loading."""
        return cast(
            bool,
            self.driver.execute_script(
                """
            return window.store.getState().isLoading;
            """
            ),
        )

    @property
    def window_store(self) -> Optional[Any]:
        """Get window.store object."""
        return self.driver.execute_script("return window.store")

    def _wait_for_callbacks(self) -> bool:
        """Check if callbacks are complete."""
        # Access properties directly
        window_store = self.window_store
        redux_state_rqs = self.redux_state_rqs
        return (not window_store) or (redux_state_rqs == [])

    def get_local_storage(self, store_id: str = "local") -> Optional[dict[str, Any]]:
        """Get item from localStorage."""
        return cast(
            Optional[dict[str, Any]],
            self.driver.execute_script(
                f"return JSON.parse(window.localStorage.getItem('{store_id}'));"
            ),
        )

    def get_session_storage(
        self, session_id: str = "session"
    ) -> Optional[dict[str, Any]]:
        """Get item from sessionStorage."""
        return cast(
            Optional[dict[str, Any]],
            self.driver.execute_script(
                f"return JSON.parse(window.sessionStorage.getItem('{session_id}'));"
            ),
        )

    def clear_local_storage(self) -> None:
        """Clear localStorage."""
        self.driver.execute_script("window.localStorage.clear()")

    def clear_session_storage(self) -> None:
        """Clear sessionStorage."""
        self.driver.execute_script("window.sessionStorage.clear()")

    def clear_storage(self) -> None:
        """Clear both localStorage and sessionStorage."""
        self.clear_local_storage()
        self.clear_session_storage()
