from selenium.webdriver.common.action_chains import ActionChains


def click_date(dash_duo, component_selector, row, col):
    date_picker_selector = (
        ".CalendarMonthGrid_month__horizontal"
        ":not(.CalendarMonthGrid_month__hidden)"
    )
    dash_duo.find_element(
        " ".join([
            component_selector,
            date_picker_selector,
            # nth-child is 1-based, but let's use 0-based
            "tr:nth-child({})".format(row + 1),
            "td:nth-child({})".format(col + 1)
        ])
    ).click()


def click_at_coord_fractions(dash_duo, el, fx, fy):
    width = el.size['width']
    height = el.size['height']
    (
        ActionChains(dash_duo.driver)
        .move_to_element_with_offset(el, width * fx, height * fy)
        .click()
        .perform()
    )
