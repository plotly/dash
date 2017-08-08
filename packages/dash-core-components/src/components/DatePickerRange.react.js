import React, {Component, PropTypes} from 'react';
import { DateRangePicker } from 'react-dates';
import moment from 'moment';

/**
 * DatePickerRange is a tailor made component designed for selecting
 * timespan across multiple days off of a calendar.
 *
 * The DatePicker integrates well with the Python datetime module with the
 * startDate and endDate being returned in a string format suitable for
 * creating datetime objects.
 *
 * This component is based off of Airbnb's react-dates react component
 * which can be found here: https://github.com/airbnb/react-dates
 */
export default class DatePickerRange extends Component {
    constructor(props) {
      super(props);
      this.props.startDate = this.props.start_date;
      this.props.endDate = this.props.end_date;
      this.props.initialVisibleMonth = this.props.initial_visible_month;
      this.props.minDateRange = this.props.min_date_range;
      this.props.maxDateRange = this.props.max_date_range;
      const momentProps = this.convertPropsToMoment(props);
      this.state = {
        focusedInput: props.autoFocusEndDate ? momentProps.startDate : momentProps.endDate,
        startDate: momentProps.startDate,
        endDate: momentProps.endDate,
        initialVisibleMonth: momentProps.initialVisibleMonth,
        minDateRange: momentProps.min,
        maxDateRange: momentProps.max,
        initialStartDate: this.props.start_date,
        initialEndDate: this.props.end_date,
        firstInitialVisibleMonth: this.props.initial_visible_month,
        initialMinDateRange: this.props.min_date_range,
        initialMaxDateRange: this.props.max_date_range
      };
    }

    convertPropsToMoment(props) {
      let startDate, endDate=null;
      let initialVisibleMonth = moment(props.startDate);
      if (typeof props.startDate !== 'undefined') {
        startDate = moment(props.startDate);
      }
      if (typeof props.endDate != 'undefined') {
        endDate = moment(props.endDate);
      }
      if (typeof props.initialVisibleMonth != 'undefined') {
        initialVisibleMonth = moment(props.initialVisibleMonth);
      }
      let min, max;
      if (typeof props.minDateRange !== 'undefined' &&
          typeof props.maxDateRange !== 'undefined') {
        min = moment(props.minDateRange);
        max = moment(props.maxDateRange);
      }
      try {
        if (startDate.isAfter(endDate)) {
          endDate = null;
        }
      } catch (TypeError) {
        // Continue regardless of error
      }

      return {startDate, endDate, initialVisibleMonth, min, max}
    }

    componentWillReceiveProps(newProps) {
      let propObj = {
        startDate: newProps.start_date,
        endDate: newProps.end_date,
        initialVisibleMonth: newProps.initial_visible_month,
        minDateRange: newProps.min_date_range,
        maxDateRange: newProps.max_date_range
      }
      const momentProps = this.convertPropsToMoment(propObj);
      if (this.state.initialStartDate != newProps.start_date) {
        this.setState({
          initialStartDate: newProps.start_date,
          startDate: momentProps.startDate
        });
      }
      if (this.state.initialEndDate != newProps.end_date) {
        this.setState({
          initialEndDate: newProps.end_date,
          endDate: momentProps.endDate
        });
      }
      if (this.state.firstInitialVisibleMonth != newProps.initial_visible_month){
        this.setState({
          firstInitialVisibleMonth: newProps.initial_visible_month,
          initialVisibleMonth: momentProps.initialVisibleMonth
        })
      }
      if (this.state.initialMinDateRange != newProps.min_date_range){
        this.setState({
          initialMinDateRange: newProps.min_date_range,
          minDateRange: momentProps.minDateRange
        })
      }
      if (this.state.initialMaxDateRange != newProps.max_date_range){
        this.setState({
          initialMaxDateRange: newProps.max_date_range,
          maxDateRange: momentProps.maxDateRange
        })
      }
    }

    render() {
        const {setProps, fireEvent} = this.props
        return (
          <DateRangePicker
            startDate={ this.state.startDate }
            startDatePlaceholderText={ this.props.start_date_placeholder_text }
            endDate={ this.state.endDate }
            endDatePlaceholderText={ this.props.end_date_placeholder_text }
            onDatesChange={({ startDate, endDate }) => {
              this.setState({ startDate, endDate });
              if (startDate != null) {
                const startDateStr = startDate.format('YYYY-MM-DD');
                if (setProps) {
                  setProps({
                    startDate: startDateStr
                  });
                }
                if (fireEvent) {
                  fireEvent('change');
                }
              }
              this.props.start_date = startDate;
              if (endDate != null) {
                const endDateStr = endDate.format('YYYY-MM-DD');
                if (setProps) {
                  setProps({
                    endDate: endDateStr
                  });
                }
                if (fireEvent) {
                  fireEvent('change');
                }
              }
            }}
            focusedInput={ this.state.focusedInput }
            onFocusChange={focusedInput => this.setState({ focusedInput })}
            isOutsideRange={date =>
              date < this.state.minDateRange || date >= this.state.maxDateRange
            }
            showClearDates={ this.props.clearable }
            disabled={ this.props.disabled }
            keepOpenOnDateSelect={ this.props.stay_open_on_select }
            reopenPickerOnClearDates={ this.props.reopen_calendar_on_clear }
            initialVisibleMonth={() => {
              if (this.state.startDate != null) {
                return this.state.startDate
              } else {
                return this.state.initialVisibleMonth
              }
            }}
            numberOfMonths={ this.props.number_of_months_shown }
            withPortal={ this.props.with_portal }
            withFullScreenPortal={ this.props.with_full_screen_portal }
            firstDayOfWeek={ this.props.first_day_of_week }
            minimumNights={ this.props.minimum_nights }
            enableOutsideDays={ this.props.show_outside_days }
            monthFormat={ this.props.month_format }
            displayFormat={ this.props.display_format }
          />
        );
    }
}

DatePickerRange.propTypes = {
    id: PropTypes.string,

    /**
     * Specifies the starting date for the component, best practice is to pass
     * value via datetime object
     */
    start_date: PropTypes.string,

    /**
     * Specifies the ending date for the component, best practice is to pass
     * value via datetime object
     */
    end_date: PropTypes.string,

    /**
     * Specifies the lowest selectable date for the component,
     * best practice is to pass value via datetime object
     */
    min_date_range: PropTypes.string,

    /**
     * Specifies the highest selectable date for the component,
     * best practice is to pass value via datetime object
     */
    max_date_range: PropTypes.string,

    /**
     * Specifies the date that is initially presented when the user
     * opens the calendar, best practice is to pass value via datetime
     * object
     */
    initial_visible_month: PropTypes.string,

    /**
     * Text that will be displayed in the first input
     * box of the date picker when no date is selected - replaces 'Start Date'
     */
    start_date_placeholder_text: PropTypes.string,

    /**
     * Text that will be displayed in the second input
     * box of the date picker when no date is selected - replaces 'End Date'
     */
    end_date_placeholder_text: PropTypes.string,

    /**
     * If True, the calendar will automatically open when cleared
     */
    reopen_calendar_on_clear: PropTypes.bool,

    /**
     * Number of calendar months that are shown when calendar is opened
     */
    number_of_months_shown: PropTypes.number,

    /**
     * If True, calendar will open in a screen overlay portal
     */
    with_portal: PropTypes.bool,

    /**
     * If True, calendar will open in a full screen overlay portal, will
     * take precedent over 'withPortal' if both are set to true
     */
    with_full_screen_portal: PropTypes.bool,

    /**
     * Specifies what day is the first day of the week, values must be
     * from [0, ..., 6]
     */
    first_day_of_week: PropTypes.oneOf([0, 1, 2, 3, 4, 5, 6]),

    /**
     * Specifies a minimum number of nights that must be selected between
     * the startDate and the endDate
     */
    minimum_nights: PropTypes.number,

    /**
     * If True the calendar will not close when the user has selected a value
     * and will wait until the user clicks off the calendar
     */
    stay_open_on_select: PropTypes.bool,

    /**
     * If True the calendar will display days that rollover into
     * the next month
     */
    show_outside_days: PropTypes.bool,

    /**
     * Specifies the format that the month will be displayed in the calendar,
     * valid formats are variations of "MM YY"
     */
    month_format: PropTypes.string,

    /**
     * Specifies the format that the selected dates will be displayed
     * valid formats are variations of "MM YY DD"
     */
    display_format: PropTypes.string,

    /**
     * If True, no dates can be selected.
     */
    disabled: PropTypes.bool,

    /**
     * If True, there will be a button that allows for clearing the dates
     */
    clearable: PropTypes.bool,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    dashEvents: PropTypes.oneOf(['change'])
};

DatePickerRange.defaultProps = {
    with_portal: false,
    with_full_screen_portal: false,
    first_day_of_week: 0,
    number_of_months_shown: 1,
    stay_open_on_select: false,
    reopen_calendar_on_clear: false,
    clearable: false,
    disabled: false
};
