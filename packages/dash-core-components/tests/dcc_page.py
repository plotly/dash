import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class DashCoreComponentsMixin(object):
    def select_calendar_date(
        self, comp_id, index=0, day="", date_range="", outside_month=False
    ):
        if date_range:
            if date_range.lower() not in {"start", "end"}:
                logger.error(
                    "data_range is provided with an invalid value %s\n"
                    "the accepted value is start or end",
                    date_range,
                )
                return
            date = self.find_element(
                '#{} input[aria-label="{} Date"]'.format(
                    comp_id, date_range.capitalize()
                )
            )
        else:
            date = self.find_element("#{} input".format(comp_id))
        date.click()
        WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, self.date_picker_day_locator)
            )
        )

        def is_month_valid(elem):
            return (
                "__outside" in elem.get_attribute("class")
                if outside_month
                else "__outside" not in elem.get_attribute("class")
            )

        days = self.find_elements(self.date_picker_day_locator)
        if day:
            filtered = [
                elem
                for elem in days
                if elem.text == day and is_month_valid(elem)
            ]
            if not filtered or len(filtered) > 1:
                logger.error(
                    "cannot find the matched day with index=%s, day=%s",
                    index,
                    day,
                )
            matched = filtered[0]
        else:
            matched = days[index]

        matched.click()
        return date.get_attribute("value")

    @property
    def date_picker_day_locator(self):
        return 'div[data-visible="true"] td.CalendarDay'
