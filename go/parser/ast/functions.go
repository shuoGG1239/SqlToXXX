package ast1

// TimeUnitType is the type for time and timestamp units.
type TimeUnitType int

const (
	// TimeUnitInvalid is a placeholder for an invalid time or timestamp unit
	TimeUnitInvalid TimeUnitType = iota
	// TimeUnitMicrosecond is the time or timestamp unit MICROSECOND.
	TimeUnitMicrosecond
	// TimeUnitSecond is the time or timestamp unit SECOND.
	TimeUnitSecond
	// TimeUnitMinute is the time or timestamp unit MINUTE.
	TimeUnitMinute
	// TimeUnitHour is the time or timestamp unit HOUR.
	TimeUnitHour
	// TimeUnitDay is the time or timestamp unit DAY.
	TimeUnitDay
	// TimeUnitWeek is the time or timestamp unit WEEK.
	TimeUnitWeek
	// TimeUnitMonth is the time or timestamp unit MONTH.
	TimeUnitMonth
	// TimeUnitQuarter is the time or timestamp unit QUARTER.
	TimeUnitQuarter
	// TimeUnitYear is the time or timestamp unit YEAR.
	TimeUnitYear
	// TimeUnitSecondMicrosecond is the time unit SECOND_MICROSECOND.
	TimeUnitSecondMicrosecond
	// TimeUnitMinuteMicrosecond is the time unit MINUTE_MICROSECOND.
	TimeUnitMinuteMicrosecond
	// TimeUnitMinuteSecond is the time unit MINUTE_SECOND.
	TimeUnitMinuteSecond
	// TimeUnitHourMicrosecond is the time unit HOUR_MICROSECOND.
	TimeUnitHourMicrosecond
	// TimeUnitHourSecond is the time unit HOUR_SECOND.
	TimeUnitHourSecond
	// TimeUnitHourMinute is the time unit HOUR_MINUTE.
	TimeUnitHourMinute
	// TimeUnitDayMicrosecond is the time unit DAY_MICROSECOND.
	TimeUnitDayMicrosecond
	// TimeUnitDaySecond is the time unit DAY_SECOND.
	TimeUnitDaySecond
	// TimeUnitDayMinute is the time unit DAY_MINUTE.
	TimeUnitDayMinute
	// TimeUnitDayHour is the time unit DAY_HOUR.
	TimeUnitDayHour
	// TimeUnitYearMonth is the time unit YEAR_MONTH.
	TimeUnitYearMonth
)

// String implements fmt.Stringer interface.
func (unit TimeUnitType) String() string {
	switch unit {
	case TimeUnitMicrosecond:
		return "MICROSECOND"
	case TimeUnitSecond:
		return "SECOND"
	case TimeUnitMinute:
		return "MINUTE"
	case TimeUnitHour:
		return "HOUR"
	case TimeUnitDay:
		return "DAY"
	case TimeUnitWeek:
		return "WEEK"
	case TimeUnitMonth:
		return "MONTH"
	case TimeUnitQuarter:
		return "QUARTER"
	case TimeUnitYear:
		return "YEAR"
	case TimeUnitSecondMicrosecond:
		return "SECOND_MICROSECOND"
	case TimeUnitMinuteMicrosecond:
		return "MINUTE_MICROSECOND"
	case TimeUnitMinuteSecond:
		return "MINUTE_SECOND"
	case TimeUnitHourMicrosecond:
		return "HOUR_MICROSECOND"
	case TimeUnitHourSecond:
		return "HOUR_SECOND"
	case TimeUnitHourMinute:
		return "HOUR_MINUTE"
	case TimeUnitDayMicrosecond:
		return "DAY_MICROSECOND"
	case TimeUnitDaySecond:
		return "DAY_SECOND"
	case TimeUnitDayMinute:
		return "DAY_MINUTE"
	case TimeUnitDayHour:
		return "DAY_HOUR"
	case TimeUnitYearMonth:
		return "YEAR_MONTH"
	default:
		return ""
	}
}
