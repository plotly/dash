from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

DATE_PICKER_DAY_SELECTOR = 'div[data-visible="true"] td.CalendarDay'


def choose_calendar_date(dd, comp_id, index=0, day="", outside_month=False):
    date = dd.find_element("#{} input".format(comp_id))
    date.click()
    WebDriverWait(dd.driver, 1).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, DATE_PICKER_DAY_SELECTOR))
    )

    def is_month_valid(elem):
        return (
            "__outside" in elem.get_attribute("class")
            if outside_month
            else "__outside" not in elem.get_attribute("class")
        )

    days = dd.find_elements(DATE_PICKER_DAY_SELECTOR)
    if day:
        filtered = [
            elem for elem in days if elem.text == day and is_month_valid(elem)
        ]
        if not filtered or len(filtered) > 1:
            raise Exception("cannot find matched day")
        matched = filtered[0]
    else:
        matched = days[index]

    matched.click()
    return date.get_attribute("value")


def click_date(dash_duo, component_selector, row, col):
    date_picker_selector = (
        ".CalendarMonthGrid_month__horizontal"
        ":not(.CalendarMonthGrid_month__hidden)"
    )
    dash_duo.find_element(
        " ".join(
            [
                component_selector,
                date_picker_selector,
                # nth-child is 1-based, but let's use 0-based
                "tr:nth-child({})".format(row + 1),
                "td:nth-child({})".format(col + 1),
            ]
        )
    ).click()
