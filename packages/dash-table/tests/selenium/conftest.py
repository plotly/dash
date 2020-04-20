import pytest

from dash.testing.browser import Browser
from preconditions import preconditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

_validate_col = lambda col: (isinstance(col, str) and len(col) > 0) or (
    isinstance(col, int) and col >= 0
)
_validate_col_id = lambda col_id: isinstance(col_id, str) and len(col_id) > 0
_validate_id = lambda id: isinstance(id, str) and len(id) > 0
_validate_key = lambda key: isinstance(key, str) and len(key) == 1
_validate_keys = lambda keys: isinstance(keys, str) and len(keys) > 0
_validate_mixin = lambda mixin: isinstance(mixin, DataTableMixin)
_validate_row = lambda row: isinstance(row, int) and row >= 0
_validate_selector = lambda selector: isinstance(selector, str) and len(selector) > 0
_validate_state = lambda state: state in [_READY, _LOADING, _ANY]
_validate_target = lambda target: isinstance(target, DataTableFacade)

_READY = ".dash-spreadsheet:not(.dash-loading)"
_LOADING = ".dash-spreadsheet.dash-loading"
_ANY = ".dash-spreadsheet"
_TIMEOUT = 10


class HoldKeyContext:
    @preconditions(_validate_mixin, _validate_key)
    def __init__(self, mixin, key):
        self.mixin = mixin
        self.key = key

    def __enter__(self):
        ActionChains(self.mixin.driver).key_down(self.key).perform()

    def __exit__(self, type, value, traceback):
        ActionChains(self.mixin.driver).key_up(self.key).perform()


class DataTableCellFacade(object):
    @preconditions(
        _validate_id, _validate_mixin, _validate_row, _validate_col, _validate_state
    )
    def __init__(self, id, mixin, row, col, state=_ANY):
        self.id = id
        self.mixin = mixin
        self.row = row
        self.col = col
        self.state = state

    def _get_cell_value(self):
        return self.get().find_element_by_css_selector(".dash-cell-value")

    def click(self):
        return self.get().click()

    def double_click(self):
        ac = ActionChains(self.mixin.driver)
        ac.move_to_element(self._get_cell_value())
        ac.pause(1)  # sometimes experiencing incorrect behavior on scroll otherwise
        ac.double_click()
        return ac.perform()

    def get(self):
        self.mixin._wait_for_table(self.id, self.state)

        return (
            self.mixin.find_element(
                '#{} {} tbody td.dash-cell.column-{}[data-dash-row="{}"]:not(.phantom-cell)'.format(
                    self.id, self.state, self.col, self.row
                )
            )
            if isinstance(self.col, int)
            else self.mixin.find_element(
                '#{} {} tbody td.dash-cell[data-dash-column="{}"][data-dash-row="{}"]:not(.phantom-cell)'.format(
                    self.id, self.state, self.col, self.row
                )
            )
        )

    def get_text(self):
        el = self._get_cell_value()

        value = el.get_attribute("value")
        return (
            value
            if value is not None and value != ""
            else el.get_attribute("innerHTML")
        )

    def is_active(self):
        input = self.get().find_element_by_css_selector("input")

        return "focused" in input.get_attribute("class").split(" ")

    def is_selected(self):
        cell = self.get()

        return "cell--selected" in cell.get_attribute("class").split(" ")

    def is_focused(self):
        cell = self.get()

        return "focused" in cell.get_attribute("class").split(" ")

    def open_dropdown(self):
        cell = self.get()

        cell.find_element_by_css_selector(".Select-arrow").click()


class DataTableColumnFacade(object):
    @preconditions(_validate_id, _validate_mixin, _validate_col_id, _validate_state)
    def __init__(self, id, mixin, col_id, state=_ANY):
        self.id = id
        self.mixin = mixin
        self.col_id = col_id
        self.state = state

    @preconditions(_validate_row)
    def get(self, row=0):
        self.mixin._wait_for_table(self.id, self.state)

        return self.mixin.find_elements(
            '#{} {} tbody tr th.dash-header[data-dash-column="{}"]:not(.phantom-cell)'.format(
                self.id, self.state, self.col_id
            )
        )[row]

    @preconditions(_validate_row)
    def hide(self, row=0):
        self.get(row).find_element_by_css_selector(".column-header--hide").click()

    @preconditions(_validate_row)
    def sort(self, row=0):
        self.get(row).find_element_by_css_selector(".column-header--sort").click()

    def filter(self):
        return self.mixin.find_element(
            '#{} {} tbody tr th.dash-filter[data-dash-column="{}"]:not(.phantom-cell)'.format(
                self.id, self.state, self.col_id
            )
        ).click()


class DataTableRowFacade(object):
    @preconditions(_validate_id, _validate_mixin, _validate_row, _validate_state)
    def __init__(self, id, mixin, row, state=_ANY):
        self.id = id
        self.mixin = mixin
        self.row = row
        self.state = state

    def delete(self):
        return self.mixin.find_elements(
            "#{} {} tbody tr td.dash-delete-cell:not(.phantom-cell)".format(
                self.id, self.state
            )
        )[self.row].click()

    def select(self):
        return self.mixin.find_elements(
            "#{} {} tbody tr td.dash-select-cell:not(.phantom-cell)".format(
                self.id, self.state
            )
        )[self.row].click()

    def is_selected(self):
        return (
            self.mixin.find_elements(
                "#{} {} tbody tr td.dash-select-cell:not(.phantom-cell)".format(
                    self.id, self.state
                )
            )[self.row]
            .find_element_by_css_selector("input")
            .is_selected()
        )


class DataTablePagingActionFacade(object):
    @preconditions(_validate_id, _validate_mixin, _validate_selector)
    def __init__(self, id, mixin, selector):
        self.id = id
        self.mixin = mixin
        self.selector = selector

    def click(self):
        self.mixin._wait_for_table(self.id)

        return self.mixin.find_element("#{} {}".format(self.id, self.selector)).click()

    def exists(self):
        self.mixin._wait_for_table(self.id)

        el = self.mixin.find_element("#{} {}".format(self.id, self.selector))

        return el is not None and el.is_enabled()


class DataTablePagingCurrentFacade(object):
    @preconditions(_validate_id, _validate_mixin)
    def __init__(self, id, mixin):
        self.id = id
        self.mixin = mixin

    def click(self):
        self.mixin._wait_for_table(self.id)

        return self.mixin.find_element("#{} input.current-page".format(self.id)).click()

    def get_value(self):
        self.mixin._wait_for_table(self.id)

        return self.mixin.find_element(
            "#{} input.current-page".format(self.id)
        ).get_attribute("placeholder")


class DataTablePagingFacade(object):
    @preconditions(_validate_id, _validate_mixin)
    def __init__(self, id, mixin):
        self.id = id
        self.mixin = mixin

        self.current = DataTablePagingCurrentFacade(self.id, self.mixin)
        self.first = DataTablePagingActionFacade(
            self.id, self.mixin, "button.first-page"
        )
        self.last = DataTablePagingActionFacade(self.id, self.mixin, "button.last-page")
        self.next = DataTablePagingActionFacade(self.id, self.mixin, "button.next-page")
        self.previous = DataTablePagingActionFacade(
            self.id, self.mixin, "button.previous-page"
        )

    def exists(self):
        self.mixin._wait_for_table(self.id)

        return len(self.mixin.find_elements(".previous-next-container")) != 0


class DataTableFacade(object):
    @preconditions(_validate_id, _validate_mixin)
    def __init__(self, id, mixin):
        self.id = id
        self.mixin = mixin

        self.paging = DataTablePagingFacade(id, mixin)

    @preconditions(_validate_row, _validate_col, _validate_state)
    def cell(self, row, col, state=_ANY):
        return DataTableCellFacade(self.id, self.mixin, row, col, state)

    @preconditions(_validate_col_id, _validate_state)
    def column(self, col_id, state=_ANY):
        return DataTableColumnFacade(self.id, self.mixin, col_id, state)

    @preconditions(_validate_row, _validate_state)
    def row(self, row, state=_ANY):
        return DataTableRowFacade(self.id, self.mixin, row, state)

    def is_ready(self):
        return self.mixin._wait_for_table(self.id, _READY)

    def is_loading(self):
        return self.mixin._wait_for_table(self.id, _LOADING)


class DataTableMixin(object):
    @preconditions(_validate_id, _validate_state)
    def _wait_for_table(self, id, state=_ANY):
        return WebDriverWait(self.driver, _TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#{} {}".format(id, state))
            )
        )

    @preconditions(_validate_id)
    def table(self, id):
        return DataTableFacade(id, self)

    def copy(self):
        with self.hold(Keys.CONTROL):
            self.send_keys("c")

    def paste(self):
        with self.hold(Keys.CONTROL):
            self.send_keys("v")

    @preconditions(_validate_key)
    def hold(self, key):
        return HoldKeyContext(self, key)

    def get_selected_text(self):
        return self.driver.execute_script("return window.getSelection().toString()")

    @preconditions(_validate_keys)
    def send_keys(self, keys):
        self.driver.switch_to.active_element.send_keys(keys)


class DataTableComposite(Browser, DataTableMixin):
    def __init__(self, server, **kwargs):
        super(DataTableComposite, self).__init__(**kwargs)
        self.server = server

        self.READY = _READY
        self.LOADING = _LOADING
        self.ANY = _ANY

    def start_server(self, app, **kwargs):
        """start the local server with app"""

        # start server with app and pass Dash arguments
        self.server(app, **kwargs)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url


@pytest.fixture
def test(request, dash_thread_server, tmpdir):
    with DataTableComposite(
        dash_thread_server,
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        percy_run=False,
    ) as dc:
        yield dc
