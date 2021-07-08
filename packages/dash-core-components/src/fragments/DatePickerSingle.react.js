import 'react-dates/initialize';

import {SingleDatePicker} from 'react-dates';
import moment from 'moment';
import React, {Component} from 'react';

import {propTypes, defaultProps} from '../components/DatePickerSingle.react';
import convertToMoment from '../utils/convertToMoment';

export default class DatePickerSingle extends Component {
    constructor() {
        super();
        this.isOutsideRange = this.isOutsideRange.bind(this);
        this.onDateChange = this.onDateChange.bind(this);
        this.state = {focused: false};
    }

    isOutsideRange(date) {
        const {max_date_allowed, min_date_allowed, disabled_days} =
            convertToMoment(this.props, [
                'max_date_allowed',
                'min_date_allowed',
                'disabled_days',
            ]);

        return (
            (min_date_allowed && date.isBefore(min_date_allowed)) ||
            (max_date_allowed && date.isAfter(max_date_allowed)) ||
            (disabled_days && disabled_days.some(d => date.isSame(d, 'day')))
        );
    }

    onDateChange(date) {
        const {setProps} = this.props;
        const payload = {date: date ? date.format('YYYY-MM-DD') : null};
        setProps(payload);
    }

    render() {
        const {focused} = this.state;

        const {
            calendar_orientation,
            clearable,
            day_size,
            disabled,
            display_format,
            first_day_of_week,
            is_RTL,
            month_format,
            number_of_months_shown,
            placeholder,
            reopen_calendar_on_clear,
            show_outside_days,
            stay_open_on_select,
            with_full_screen_portal,
            with_portal,
            loading_state,
            id,
            style,
            className,
        } = this.props;

        const {date, initial_visible_month} = convertToMoment(this.props, [
            'date',
            'initial_visible_month',
        ]);

        const verticalFlag = calendar_orientation !== 'vertical';

        const DatePickerWrapperStyles = {
            position: 'relative',
            display: 'inline-block',
            ...style,
        };

        // the height in px of the top part of the calendar (that holds
        // the name of the month)
        const baselineHeight = 145;

        return (
            <div
                id={id}
                style={DatePickerWrapperStyles}
                className={className}
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
            >
                <SingleDatePicker
                    date={date}
                    onDateChange={this.onDateChange}
                    focused={focused}
                    onFocusChange={({focused}) => this.setState({focused})}
                    initialVisibleMonth={() =>
                        date || initial_visible_month || moment()
                    }
                    isOutsideRange={this.isOutsideRange}
                    numberOfMonths={number_of_months_shown}
                    withPortal={with_portal && verticalFlag}
                    withFullScreenPortal={
                        with_full_screen_portal && verticalFlag
                    }
                    firstDayOfWeek={first_day_of_week}
                    enableOutsideDays={show_outside_days}
                    monthFormat={month_format}
                    displayFormat={display_format}
                    placeholder={placeholder}
                    showClearDate={clearable}
                    disabled={disabled}
                    keepOpenOnDateSelect={stay_open_on_select}
                    reopenPickerOnClearDate={reopen_calendar_on_clear}
                    isRTL={is_RTL}
                    orientation={calendar_orientation}
                    daySize={day_size}
                    verticalHeight={baselineHeight + day_size * 6 + 'px'}
                />
            </div>
        );
    }
}

DatePickerSingle.propTypes = propTypes;
DatePickerSingle.defaultProps = defaultProps;
