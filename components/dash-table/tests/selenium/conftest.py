import platform
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

CMD = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL


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
        return self.get().find_element(By.CSS_SELECTOR, ".dash-cell-value")

    def click(self):
        return self.get().click()

    def double_click(self):
        ac = ActionChains(self.mixin.driver)
        ac.move_to_element(self._get_cell_value())
        ac.pause(1)  # sometimes experiencing incorrect behavior on scroll otherwise
        ac.double_click()
        return ac.perform()

    def exists(self):
        self.mixin._wait_for_table(self.id, self.state)

        return (
            len(
                self.mixin.find_elements(
                    '#{} {} tbody td.dash-cell.column-{}[data-dash-row="{}"]:not(.phantom-cell)'.format(
                        self.id, self.state, self.col, self.row
                    )
                )
            )
            == 1
            if isinstance(self.col, int)
            else len(
                self.mixin.find_elements(
                    '#{} {} tbody td.dash-cell[data-dash-column="{}"][data-dash-row="{}"]:not(.phantom-cell)'.format(
                        self.id, self.state, self.col, self.row
                    )
                )
            )
            == 1
        )

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

    def find_inside(self, selector):
        return self.get().find_element(By.CSS_SELECTOR, selector)

    def find_all_inside(self, selector):
        return self.get().find_elements(By.CSS_SELECTOR, selector)

    def is_dropdown(self):
        el = self.get().find_elements(By.CSS_SELECTOR, ".Select-arrow")

        return len(el) == 1

    def is_input(self):
        el = self.get().find_elements(By.CSS_SELECTOR, ".dash-cell-value")

        return len(el) == 1 and el[0].get_attribute("type") is not None

    def get_text(self):
        el = self._get_cell_value()

        value = el.get_attribute("value")
        return (
            value
            if value is not None and value != ""
            else el.get_attribute("innerHTML")
        )

    def move_to(self):
        ac = ActionChains(self.mixin.driver)
        ac.move_to_element(self._get_cell_value())
        return ac.perform()

    def is_active(self):
        input = self.get().find_element(By.CSS_SELECTOR, "input")

        return "focused" in input.get_attribute("class").split(" ")

    def is_selected(self):
        cell = self.get()

        return "cell--selected" in cell.get_attribute("class").split(" ")

    def is_focused(self):
        cell = self.get()

        return "focused" in cell.get_attribute("class").split(" ")

    def is_value_focused(self):
        el = self._get_cell_value()

        return "focused" in el.get_attribute("class").split(" ")

    def open_dropdown(self):
        cell = self.get()

        cell.find_element(By.CSS_SELECTOR, ".Select-arrow").click()


class DataTableColumnFacade(object):
    @preconditions(_validate_id, _validate_mixin, _validate_col, _validate_state)
    def __init__(self, id, mixin, col, state=_ANY):
        self.id = id
        self.mixin = mixin
        self.col = col
        self.state = state

    @preconditions(_validate_row)
    def get(self, row=0):
        self.mixin._wait_for_table(self.id, self.state)

        return (
            self.mixin.find_element(
                "#{} {} tbody tr:nth-of-type({}) th.dash-header.column-{}:not(.phantom-cell)".format(
                    self.id, self.state, row + 1, self.col
                )
            )
            if isinstance(self.col, int)
            else self.mixin.find_element(
                '#{} {} tbody tr:nth-of-type({}) th.dash-header[data-dash-column="{}"]:not(.phantom-cell)'.format(
                    self.id, self.state, row + 1, self.col
                )
            )
        )

    def find_inside(self, row, selector):
        return self.get(row).find_element(By.CSS_SELECTOR, selector)

    def find_all_inside(self, row, selector):
        return self.get(row).find_elements(By.CSS_SELECTOR, selector)

    def exists(self, row=0):
        self.mixin._wait_for_table(self.id, self.state)

        els = (
            self.mixin.find_elements(
                "#{} {} tbody tr:nth-of-type({}) th.dash-header.column-{}:not(.phantom-cell)".format(
                    self.id, self.state, row + 1, self.col
                )
            )
            if isinstance(self.col, int)
            else self.mixin.find_elements(
                '#{} {} tbody tr:nth-of-type({}) th.dash-header[data-dash-column="{}"]:not(.phantom-cell)'.format(
                    self.id, self.state, row + 1, self.col
                )
            )
        )

        return len(els) != 0

    @preconditions(_validate_row)
    def clear(self, row=0):
        self.find_inside(row, ".column-header--clear").click()

    @preconditions(_validate_row)
    def delete(self, row=0):
        self.find_inside(row, ".column-header--delete").click()

    @preconditions(_validate_row)
    def edit(self, row=0):
        self.find_inside(row, ".column-header--edit").click()

    @preconditions(_validate_row)
    def get_text(self, row=0):
        el = self.find_inside(row, "span.column-header-name")

        return el.get_attribute("innerHTML") if el is not None else None

    @preconditions(_validate_row)
    def hide(self, row=0):
        self.find_inside(row, ".column-header--hide").click()

    @preconditions(_validate_row)
    def is_selected(self, row=0):
        return self.find_inside(row, ".column-header--select input").is_selected()

    @preconditions(_validate_row)
    def move_to(self, row=0):
        ac = ActionChains(self.mixin.driver)
        ac.move_to_element(self.get(row))
        return ac.perform()

    @preconditions(_validate_row)
    def select(self, row=0):
        self.find_inside(row, ".column-header--select input").click()

    @preconditions(_validate_row)
    def sort(self, row=0):
        self.find_inside(row, ".column-header--sort").click()

    def filter(self):
        return (
            self.mixin.find_element(
                "#{} {} tbody tr th.dash-filter.column-{}:not(.phantom-cell)".format(
                    self.id, self.state, self.col
                )
            )
            if isinstance(self.col, int)
            else self.mixin.find_element(
                '#{} {} tbody tr th.dash-filter[data-dash-column="{}"]:not(.phantom-cell)'.format(
                    self.id, self.state, self.col
                )
            )
        )

    def filter_clear(self):
        self.filter().find_element(By.CSS_SELECTOR, "input").click()
        ac = ActionChains(self.mixin.driver)
        ac.key_down(CMD)
        ac.send_keys("a")
        ac.key_up(CMD)
        ac.send_keys(Keys.DELETE)
        ac.perform()

    def filter_click(self):
        self.filter().click()

    def filter_invalid(self):
        return "invalid" in self.filter().get_attribute("class").split(" ")

    def filter_value(self, value=None):
        if value is None:
            return (
                self.filter()
                .find_element(By.CSS_SELECTOR, "input")
                .get_attribute("value")
            )
        elif value == "":
            self.filter_clear()
        else:
            self.filter_clear()
            self.mixin.driver.switch_to.active_element.send_keys(value + Keys.ENTER)

    def filter_placeholder(self):
        return (
            self.filter()
            .find_element(By.CSS_SELECTOR, "input")
            .get_attribute("placeholder")
        )


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
            .find_element(By.CSS_SELECTOR, "input")
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


class DataTableTooltipFacade(object):
    @preconditions(_validate_id, _validate_mixin)
    def __init__(self, id, mixin):
        self.id = id
        self.mixin = mixin

    def _get_tooltip(self):
        return self.mixin.find_element(".dash-tooltip")

    def get(self):
        return self._get_tooltip()

    def find_inside(self, selector):
        return self.get().find_element(By.CSS_SELECTOR, selector)

    def find_all_inside(self, selector):
        return self.get().find_elements(By.CSS_SELECTOR, selector)

    def exists(self):
        self.mixin._wait_for_table(self.id)

        tooltip = self._get_tooltip()

        return tooltip is not None and tooltip.is_displayed()

    def missing(self):
        self.mixin._wait_for_table(self.id)

        return len(self.mixin.find_elements(".dash-tooltip")) == 0

    def get_text(self):
        return self.find_inside(".dash-table-tooltip").get_attribute("innerHTML")


class DataTableToggleColumnsFacade(object):
    @preconditions(_validate_id, _validate_mixin)
    def __init__(self, id, mixin):
        self.id = id
        self.mixin = mixin

    def open(self):
        if not self.is_opened():
            self.mixin.find_element("#{} .show-hide".format(self.id)).click()

    def close(self):
        if self.is_opened():
            self.mixin.find_element("#{} .show-hide".format(self.id)).click()

    def get_hidden(self):
        els = self.mixin.find_elements("#table .show-hide-menu input")

        return list(filter(lambda el: not el.is_selected(), els))

    def get_hidden_values(self):
        return [el.get_attribute("value") for el in self.get_hidden()]

    def get_visible(self):
        els = self.mixin.find_elements("#table .show-hide-menu input")

        return list(filter(lambda el: el.is_selected(), els))

    def get_visible_values(self):
        return [el.get_attribute("value") for el in self.get_visible()]

    def is_opened(self):
        return len(self.mixin.find_elements("#{} .show-hide-menu".format(self.id))) != 0


class DataTableFacade(object):
    @preconditions(_validate_id, _validate_mixin)
    def __init__(self, id, mixin):
        self.id = id
        self.mixin = mixin

        self.paging = DataTablePagingFacade(id, mixin)
        self.tooltip = DataTableTooltipFacade(id, mixin)

    @preconditions(_validate_row, _validate_col, _validate_state)
    def cell(self, row, col, state=_ANY):
        return DataTableCellFacade(self.id, self.mixin, row, col, state)

    @preconditions(_validate_col, _validate_state)
    def column(self, col, state=_ANY):
        return DataTableColumnFacade(self.id, self.mixin, col, state)

    @preconditions(_validate_row, _validate_state)
    def row(self, row, state=_ANY):
        return DataTableRowFacade(self.id, self.mixin, row, state)

    @preconditions(_validate_state)
    def toggle_columns(self, state=_ANY):
        return DataTableToggleColumnsFacade(self.id, self.mixin)

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

    def get_table_ids(self):
        return self.driver.execute_script(
            """
            return Array.from(
                document.querySelectorAll('.dash-spreadsheet-container')
            ).map(
                e => e.parentElement.getAttribute('id')
            )
        """
        )

    def copy(self):
        with self.hold(CMD):
            self.send_keys("c")

    def paste(self):
        with self.hold(CMD):
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

    def get_log_errors(self):
        return list(filter(lambda i: i.get("level") != "WARNING", self.get_logs()))

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
        download_path=tmpdir.mkdir("dt-download").strpath,
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    ) as dc:
        yield dc
