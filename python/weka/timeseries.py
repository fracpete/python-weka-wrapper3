# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# timeseries.py
# Copyright (C) 2021 Fracpete (pythonwekawrapper at gmail dot com)

import javabridge
import logging
from weka.core.classes import JavaObject, OptionHandler, Date, Enum, new_instance
from weka.core.dataset import Instances, Instance
from weka.core.typeconv import jstring_list_to_string_list, jdouble_to_float
from weka.classifiers import Classifier, NumericPrediction
from weka.filters import Filter


# logging setup
logger = logging.getLogger("weka.timeseries")


class TestPart(JavaObject):
    """
    Inner class defining one boundary of an interval.
    """

    def __init__(self, jobject):
        """
        Initializes the TestPart object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.timeseries.core.CustomPeriodicTest.TestPart")
        super(TestPart, self).__init__(jobject=jobject)

    @property
    def is_upper(self):
        """
        Returns true if this is the upper bound.

        :return: true if upper bound
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isUpper", "()Z")

    @is_upper.setter
    def is_upper(self, upper):
        """
        Sets whether this is the upper bound.

        :param upper: true if upper bound
        :type upper: bool
        """
        javabridge.call(self.jobject, "setIsUpper", "(Z)V")

    def eval(self, date, other):
        """
        Evaluate the supplied date against this bound. Handles
        date fields that are cyclic (such as month, day of week etc.)
        so that intervals such as oct < date < mar evaluate correctly.

        :param date: the date to test
        :type date: Date
        :param other: the other bound
        :type other: TestPart
        :return: true if the supplied date is within this bound
        :rtype: bool
        """
        return javabridge.call(self.jobject, "eval", "(Ljava/util/Date;Lweka/classifiers/timeseries/core/CustomPeriodicTest$TestPart;)Z", date.jobject, other.jobject)

    def operator(self, s):
        """
        Sets the operator.

        :param s: the operator to use
        :type s: str
        """
        javabridge.call(self.jobject, "setOperator", "(Ljava/lang/String;)V", s)

    def year(self, s):
        """
        Sets the year.

        :param s: the year to use
        :type s: str
        """
        javabridge.call(self.jobject, "setYear", "(Ljava/lang/String;)V", s)

    def week_of_year(self, s):
        """
        Sets the week of the year.

        :param s: the woy to use
        :type s: str
        """
        javabridge.call(self.jobject, "setWeekOfYear", "(Ljava/lang/String;)V", s)

    def week_of_month(self, s):
        """
        Sets the week of the month.

        :param s: the wom to use
        :type s: str
        """
        javabridge.call(self.jobject, "setWeekOfMonth", "(Ljava/lang/String;)V", s)

    def day_of_year(self, s):
        """
        Sets the day of year.

        :param s: the doy to use
        :type s: str
        """
        javabridge.call(self.jobject, "setDayOfYear", "(Ljava/lang/String;)V", s)

    def day_of_month(self, s):
        """
        Sets the day of the month.

        :param s: the dom to use
        :type s: str
        """
        javabridge.call(self.jobject, "setDayOfMonth", "(Ljava/lang/String;)V", s)

    @property
    def month(self):
        """
        Returns the month string.

        :return: the month string
        :rtype: str
        """
        return javabridge.call(self.jobject, "getMonthString", "()Ljava/lang/String;")

    @month.setter
    def month(self, s):
        """
        Sets the month.

        :param s: the month to use
        :type s: str
        """
        javabridge.call(self.jobject, "setMonth", "(Ljava/lang/String;)V", s)

    def day_of_week(self, s):
        """
        Sets the day of the week.

        :param s: the dow to use
        :type s: str
        """
        javabridge.call(self.jobject, "setDayOfWeek", "(Ljava/lang/String;)V", s)

    def hour_of_day(self, s):
        """
        Sets the hour of the day.

        :param s: the hod to use
        :type s: str
        """
        javabridge.call(self.jobject, "setHourOfDay", "(Ljava/lang/String;)V", s)

    def minute_of_hour(self, s):
        """
        Sets the minute of the hour.

        :param s: the moh to use
        :type s: str
        """
        javabridge.call(self.jobject, "setMinuteOfHour", "(Ljava/lang/String;)V", s)

    def second(self, s):
        """
        Sets the second.

        :param s: the second to use
        :type s: str
        """
        javabridge.call(self.jobject, "setSecond", "(Ljava/lang/String;)V", s)

    def day(self):
        """
        Returns the day string.

        :return: the day string
        :rtype: str
        """
        return javabridge.call(self.jobject, "getDayString", "()Ljava/lang/String;")


class CustomPeriodicTest(JavaObject):
    """
    Class that evaluates a supplied date against user-specified
    date constant fields. Fields that can be tested against include
    year, month, week of year, week of month, day of year, day of month,
    day of week, hour of day, minute of hour and second. Wildcard "*"
    matches any value for a particular field. Each CustomPeriodicTest
    is made up of one or two test parts. If the first test part's operator
    is "=", then no second part is necessary. Otherwise the first test part
    may use > or >= operators and the second test part < or <= operators.
    Taken together, the two parts define an interval. An optional label
    may be associated with the interval.
    """

    def __init__(self, jobject=None, test=None):
        """
        Initializes the CustomPeriodicTest object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param test: the test string to use
        :type test: str
        """
        if jobject is None:
            if test is None:
                raise Exception("Either jobject or test string must be provided!")
            else:
                jobject = javabridge.make_instance("weka.classifiers.timeseries.core.CustomPeriodicTest", "(Ljava/lang/String;)V", test)
        self.enforce_type(jobject, "weka.classifiers.timeseries.core.CustomPeriodicTest")
        super(CustomPeriodicTest, self).__init__(jobject=jobject)

    def lower_test(self):
        """
        Returns the lower bound test.

        :return: the test
        :rtype: TestPart
        """
        obj = javabridge.call(self.jobject, "getLowerTest", "()Lweka/classifiers/timeseries/core/CustomPeriodicTest$TestPart;")
        return TestPart(jobject=obj)

    def upper_test(self):
        """
        Returns the upper bound test.

        :return: the test
        :rtype: TestPart
        """
        obj = javabridge.call(self.jobject, "getUpperTest", "()Lweka/classifiers/timeseries/core/CustomPeriodicTest$TestPart;")
        return TestPart(jobject=obj)

    @property
    def label(self):
        """
        Returns the label.

        :return: the label
        :rtype: str
        """
        return javabridge.call(self.jobject, "getLabel", "()Ljava/lang/String;")

    @label.setter
    def label(self, l):
        """
        Sets the label.

        :param l: the label to use
        :type l: str
        """
        javabridge.call(self.jobject, "setLabel", "(Ljava/lang/String;)V", l)

    def test(self, test):
        """
        Sets the test as string.

        :param test: the test to use
        :type test: str
        """
        javabridge.call(self.jobject, "setTest", "(Ljava/lang/String;)V", test)

    def evaluate(self, date):
        """
        Evaluate the supplied date with respect to this custom periodic test interval.

        :param date: the date to test
        :type date: Date
        :return: true if the date lies within the interval.
        :rtype: bool
        """
        return javabridge.call(self.jobject, "evaluate", "(Ljava/util/Date;)Z", date.jobject)


class Periodicity(Enum):
    """
    Defines periodicity.
    """

    def __init__(self, jobject=None, periodicity=None):
        """
        Initializes the Periodicity object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param periodicity: the string representation of the enum
        :type periodicity: str
        """
        super(Periodicity, self).__init__(jobject=jobject, enum="weka.filters.supervised.attribute.TSLagMaker$Periodicity", member=periodicity)


class PeriodicityHandler(JavaObject):
    """
    Helper class to manage time stamp manipulation with respect to various
    periodicities. Has a routine to remap the time stamp, which is useful for
    date time stamps. Since dates are just manipulated internally as the number
    of milliseconds elapsed since the epoch, and any global trend modelling in
    regression functions results in enormous coefficients for this variable -
    remapping to a more reasonable scale prevents this. It also makes it easier
    to handle the case where there are time periods that shouldn't be
    considered as a time unit increment, e.g. weekends and public holidays for
    financial trading data. These "holes" in the data can be accomodated by
    accumulating a negative offset for the remapped date when a particular
    data/time occurs in a user-specified "skip" list.
    """

    def __init__(self, jobject):
        """
        Initializes the CustomPeriodicTest object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.filters.supervised.attribute.TSLagMaker.PeriodicityHandler")
        super(PeriodicityHandler, self).__init__(jobject=jobject)

    @property
    def delta_time(self):
        """
        Returns the delta time.

        :return: the delta time
        :rtype: float
        """
        return javabridge.call(self.jobject, "deltaTime", "()D")

    @delta_time.setter
    def delta_time(self, value):
        """
        Sets the delta time.

        :param value: the delta time
        :type value: float
        """
        javabridge.call(self.jobject, "setDeltaTime", "(D)V")


class TSLagMaker(Filter):
    """
    A class for creating lagged versions of target variable(s) for use in time
    series forecasting. Uses the TimeseriesTranslate filter. Has options for
    creating averages of consecutive lagged variables (which can be useful for
    long lagged variables). Some polynomials of time are also created (if there
    is a time stamp), such as time^2 and time^3. Also creates cross products
    between time and the lagged and averaged lagged variables. If there is no
    date time stamp in the data then the user has the option of having an
    artificial time stamp created. Time stamps, real or otherwise, are used for
    modeling trends rather than using a differencing-based approach.

    Also has routines for dealing with a date timestamp - i.e. it can detect a
    monthly time period (because months are different lengths) and maps date time
    stamps to equal spaced time intervals. For example, in general, a date time
    stamp is remapped by subtracting the first observed value and adding this
    value divided by the constant delta (difference between consecutive steps) to
    the result. In the case of a detected monthly time period, the remapping
    involves subtracting the base year and then adding to this the number of the
    month within the current year plus twelve times the number of intervening
    years since the base year.

    Also has routines for adding new attributes derived from a date time stamp to
    the data - e.g. AM indicator, day of the week, month, quarter etc. In the
    case where there is no real date time stamp, the user may specify a nominal
    periodic variable (if one exists in the data). For example, month might be
    coded as a nominal value. In this case it can be specified as the primary
    periodic variable. The point is, that in all these cases (nominal periodic
    and date-derived periodics), we are able to determine what the value of these
    variables will be in future instances (as computed from the last known
    historic instance).
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes the TSLagMaker filter.

        :param jobject: the javaobject to use
        :type jobject: JB_Object
        :param options: the list of options to use
        :type options: list
        """
        super(TSLagMaker, self).__init__(jobject=jobject, classname="weka.filters.supervised.attribute.TSLagMaker", options=options)

    def clear_custom_periodics(self):
        """
        Clears the custom periodics.
        """
        javabridge.call(self.jobject, "clearCustomPeriodics", "()V")

    def add_custom_periodic(self, periodic):
        """
        Adds the custom periodic.

        :param periodic: the periodic to add
        :type periodic: str
        """
        javabridge.call(self.jobject, "addCustomPeriodic", "(Ljava/lang/String;)V", periodic)

    @property
    def fields_to_lag(self):
        """
        Returns the fields to lag as list.

        :return: the fields to lag
        :rtype: list
        """
        return jstring_list_to_string_list(javabridge.call(self.jobject, "getFieldsToLag", "()Ljava/util/List;"))

    @fields_to_lag.setter
    def fields_to_lag(self, fields):
        """
        Sets the fields to lag.

        :param fields: the list of fields to lag
        :type fields: list
        """
        javabridge.call(self.jobject, "setFieldsToLag", "(Ljava/util/List;)V", fields)

    @property
    def fields_to_lag_as_string(self):
        """
        Returns the fields to lag as string.

        :return: the fields to lag
        :rtype: str
        """
        return javabridge.call(self.jobject, "getFieldsToLagAsString", "()Ljava/lang/String;")

    @fields_to_lag_as_string.setter
    def fields_to_lag_as_string(self, fields):
        """
        Sets the fields to lag as string.

        :param fields: the fields to lag
        :type fields: str
        """
        javabridge.call(self.jobject, "setFieldsToLagAsString", "(Ljava/lang/String;)V", fields)

    @property
    def overlay_fields(self):
        """
        Returns the overlay fields as list.

        :return: the overlay fields
        :rtype: list
        """
        return jstring_list_to_string_list(javabridge.call(self.jobject, "getOverlayFields", "()Ljava/util/List;"))

    @overlay_fields.setter
    def overlay_fields(self, fields):
        """
        Sets the overlay fields.

        :param fields: the list of overlay fields
        :type fields: list
        """
        javabridge.call(self.jobject, "setOverlayFields", "(Ljava/util/List;)V", fields)

    @property
    def timestamp_field(self):
        """
        Returns the overlay fields as list.

        :return: the overlay fields
        :rtype: list
        """
        return javabridge.call(self.jobject, "getTimeStampField", "()Ljava/lang/String;")

    @timestamp_field.setter
    def timestamp_field(self, field):
        """
        Sets the timestamp field.

        :param field: the field with the timestamp
        :type field: str
        """
        javabridge.call(self.jobject, "setTimeStampField", "(Ljava/lang/String;)V", field)

    @property
    def remove_leading_instances_with_unknown_lag_values(self):
        """
        Returns whether to remove instances with unknown lag values.

        :return: true if to remove
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getRemoveLeadingInstancesWithUnknownLagValues", "()Z")

    @remove_leading_instances_with_unknown_lag_values.setter
    def remove_leading_instances_with_unknown_lag_values(self, remove):
        """
        Sets whether to remove instances with unknown lag values.

        :param remove: true if to remove
        :type remove: str
        """
        javabridge.call(self.jobject, "setRemoveLeadingInstancesWithUnknownLagValues", "(Z)V", remove)

    @property
    def adjust_for_trends(self):
        """
        Returns true if we are adjusting for trends via a real or artificial time stamp.

        :return: true if to adjust
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAdjustForTrends", "()Z")

    @adjust_for_trends.setter
    def adjust_for_trends(self, adjust):
        """
        Sets whether we are adjusting for trends via a real or artificial time stamp.

        :param adjust: true if to adjust
        :type adjust: str
        """
        javabridge.call(self.jobject, "setAdjustForTrends", "(Z)V", adjust)

    @property
    def include_timelag_products(self):
        """
        Returns whether to include products between time and the lagged variables.

        :return: true if to include
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getIncludeTimeLagProducts", "()Z")

    @include_timelag_products.setter
    def include_timelag_products(self, include):
        """
        Sets whether to include products between time and the lagged variables.

        :param include: true if to include
        :type include: str
        """
        javabridge.call(self.jobject, "setIncludeTimeLagProducts", "(Z)V", include)

    @property
    def include_powers_of_time(self):
        """
        Returns whether to include powers of time in the transformed data.

        :return: true if to include
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getIncludePowersOfTime", "()Z")

    @include_powers_of_time.setter
    def include_powers_of_time(self, include):
        """
        Sets whether to include powers of time in the transformed data.

        :param include: true if to include
        :type include: str
        """
        javabridge.call(self.jobject, "setIncludePowersOfTime", "(Z)V", include)

    @property
    def adjust_for_variance(self):
        """
        Returns true if we are adjusting for variance by taking the log of the target(s).

        :return: true if to adjust
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAdjustForVariance", "()Z")

    @adjust_for_variance.setter
    def adjust_for_variance(self, adjust):
        """
        Sets whether we are adjusting for variance by taking the log of the target(s).

        :param adjust: true if to adjust
        :type adjust: str
        """
        javabridge.call(self.jobject, "setAdjustForVariance", "(Z)V", adjust)

    @property
    def min_lag(self):
        """
        Returns the minimum lag to create.

        :return: the lag
        :rtype: int
        """
        return javabridge.call(self.jobject, "getMinLag", "()I")

    @min_lag.setter
    def min_lag(self, lag):
        """
        Sets the minimum lag to create.

        :param lag: the lag
        :type lag: int
        """
        javabridge.call(self.jobject, "setMinLag", "(I)V", lag)

    @property
    def max_lag(self):
        """
        Returns the maximum lag to create.

        :return: the lag
        :rtype: int
        """
        return javabridge.call(self.jobject, "getMaxLag", "()I")

    @max_lag.setter
    def max_lag(self, lag):
        """
        Sets the maximum lag to create.

        :param lag: the lag
        :type lag: int
        """
        javabridge.call(self.jobject, "setMaxLag", "(I)V", lag)

    @property
    def lag_range(self):
        """
        Returns the lag range to create.

        :return: the lag range
        :rtype: str
        """
        return javabridge.call(self.jobject, "getLagRange", "()Ljava/lang/String;")

    @lag_range.setter
    def lag_range(self, lag):
        """
        Sets the lag range to create.

        :param lag: the lag range
        :type lag: str
        """
        javabridge.call(self.jobject, "setLagRange", "(Ljava/lang/String;)V", lag)

    @property
    def average_consecutive_long_lags(self):
        """
        Returns true if consecutive long lagged variables are to be averaged.

        :return: true if to average
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAverageConsecutiveLongLags", "()Z")

    @average_consecutive_long_lags.setter
    def average_consecutive_long_lags(self, average):
        """
        Sets whether to average consecutive long lagged variables. Setting this to
        true creates new variables that are averages of long lags and the original
        lagged variables involved are removed.

        :param average: true if to average
        :type average: str
        """
        javabridge.call(self.jobject, "setAverageConsecutiveLongLags", "(Z)V", average)

    @property
    def average_lags_after(self):
        """
        Returns the point after which long lagged variables will be averaged.

        :return: the lag
        :rtype: int
        """
        return javabridge.call(self.jobject, "getAverageLagsAfter", "()I")

    @average_lags_after.setter
    def average_lags_after(self, lag):
        """
        Sets the point after which long lagged variables will be averaged.

        :param lag: the lag
        :type lag: int
        """
        javabridge.call(self.jobject, "setAverageLagsAfter", "(I)V", lag)

    @property
    def num_consecutive_long_lags_to_average(self):
        """
        Returns the number of consecutive long lagged variables to average.

        :return: the lag
        :rtype: int
        """
        return javabridge.call(self.jobject, "getNumConsecutiveLongLagsToAverage", "()I")

    @num_consecutive_long_lags_to_average.setter
    def num_consecutive_long_lags_to_average(self, num):
        """
        Sets the number of consecutive long lagged variables to average.

        :param num: the lag
        :type num: int
        """
        javabridge.call(self.jobject, "setNumConsecutiveLongLagsToAverage", "(I)V", num)

    @property
    def primary_periodic_field_name(self):
        """
        Returns the name of the primary periodic attribute or null if one hasn't been specified.

        :return: the name
        :rtype: str
        """
        return javabridge.call(self.jobject, "getPrimaryPeriodicFieldName", "()Ljava/lang/String;")

    @primary_periodic_field_name.setter
    def primary_periodic_field_name(self, lag):
        """
        Sets the name of the primary periodic attribute or null if one hasn't been specified.

        :param lag: the name
        :type lag: str
        """
        javabridge.call(self.jobject, "setPrimaryPeriodicFieldName", "(Ljava/lang/String;)V", lag)

    @property
    def add_am_indicator(self):
        """
        Returns whether to add an AM indicator.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAddAMIndicator", "()Z")

    @add_am_indicator.setter
    def add_am_indicator(self, add):
        """
        Sets whether to add an AM indicator.

        :param add: true if to add
        :type add: bool
        """
        javabridge.call(self.jobject, "setAddAMIndicator", "(Z)V", add)

    @property
    def add_day_of_week(self):
        """
        Returns whether to add day of week attribute.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAddDayOfWeek", "()Z")

    @add_day_of_week.setter
    def add_day_of_week(self, add):
        """
        Sets whether to add day of week attribute.

        :param add: true if to add
        :type add: bool
        """
        javabridge.call(self.jobject, "setAddDayOfWeek", "(Z)V", add)

    @property
    def add_day_of_month(self):
        """
        Returns whether to add day of month attribute.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAddDayOfMonth", "()Z")

    @add_day_of_month.setter
    def add_day_of_month(self, add):
        """
        Sets whether to add day of month attribute.

        :param add: true if to add
        :type add: bool
        """
        javabridge.call(self.jobject, "setAddDayOfMonth", "(Z)V", add)

    @property
    def add_num_days_in_month(self):
        """
        Returns whether to add # of days in month attribute.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAddNumDaysInMonth", "()Z")

    @add_num_days_in_month.setter
    def add_num_days_in_month(self, add):
        """
        Sets whether to add # of days in month attribute.

        :param add: true if to add
        :type add: bool
        """
        javabridge.call(self.jobject, "setAddNumDaysInMonth", "(Z)V", add)

    @property
    def add_weekend_indicator(self):
        """
        Returns whether to add a weekend indicator.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAddWeekendIndicator", "()Z")

    @add_weekend_indicator.setter
    def add_weekend_indicator(self, add):
        """
        Sets whether to add a weekend indicator.

        :param add: true if to add
        :type add: bool
        """
        javabridge.call(self.jobject, "setAddWeekendIndicator", "(Z)V", add)

    @property
    def add_month_of_year(self):
        """
        Returns whether to add month of year attribute.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAddMonthOfYear", "()Z")

    @add_month_of_year.setter
    def add_month_of_year(self, add):
        """
        Sets whether to add month of year attribute.

        :param add: true if to add
        :type add: bool
        """
        javabridge.call(self.jobject, "setAddMonthOfYear", "(Z)V", add)

    @property
    def add_quarter_of_year(self):
        """
        Returns whether to add quarter of year attribute.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getAddQuarterOfYear", "()Z")

    @add_quarter_of_year.setter
    def add_quarter_of_year(self, add):
        """
        Sets whether to add quarter of year attribute.

        :param add: true if to add
        :type add: bool
        """
        javabridge.call(self.jobject, "setAddQuarterOfYear", "(Z)V", add)

    @property
    def is_using_artificial_time_index(self):
        """
        Returns whether an artifical time index is used.

        :return: true if to add
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isUsingAnArtificialTimeIndex", "()Z")

    @property
    def artificial_time_start_value(self):
        """
        Returns the current value of the artificial time stamp. After training,
        after priming, and prior to forecasting, this will be equal to the number
        of training instances seen.

        :return: the start
        :rtype: float
        """
        return javabridge.call(self.jobject, "getArtificialTimeStartValue", "()D")

    @artificial_time_start_value.setter
    def artificial_time_start_value(self, start):
        """
        Sets the starting value for the artificial time stamp.

        :param start: the start
        :type start: float
        """
        javabridge.call(self.jobject, "setArtificialTimeStartValue", "(D)V", start)

    @property
    def current_timestamp_value(self):
        """
        Returns the current (i.e. most recent) time stamp value. Unlike an
        artificial time stamp, the value after training, after priming and before
        forecasting, will be equal to the time stamp of the most recent priming
        instance.

        :return: the timestamp value
        :rtype: float
        """
        return javabridge.call(self.jobject, "getCurrentTimeStampValue", "()D")

    def increment_artificial_time_value(self, increment):
        """
        Increment the artificial time value with the supplied increment value.

        :param increment: the increment
        :type increment: int
        """
        javabridge.call(self.jobject, "incrementArtificialTimeValue", "(I)V", increment)

    @property
    def delta_time(self):
        """
        Returns the difference between time values. This may be only approximate for
        periods based on dates. It is best to used date-based arithmetic in this
        case for incrementing/decrementing time stamps.

        :return: the delta
        :rtype: float
        """
        return javabridge.call(self.jobject, "getDeltaTime", "()D")

    @property
    def periodicity(self):
        """
        Returns the Periodicity representing the time stamp in use for this lag maker.
        If the lag maker is not adjusting for trends, or an artificial time stamp
        is being used, then null is returned.

        :return: the periodicity
        :rtype: Periodicity
        """
        return Periodicity(jobject=javabridge.call(self.jobject, "getPeriodicity", "()Lweka/filters/supervised/attribute/TSLagMaker$Periodicity;"))

    @periodicity.setter
    def periodicity(self, periodicity):
        """
        Sets the periodicity for the data. This is ignored if the lag maker is not
        adjusting for trends or is using an artificial time stamp. If not specified
        or set to Periodicity.UNKNOWN (the default) then heuristics will be used to
        try and automatically determine the periodicity.

        :param periodicity: the periodicity
        :type periodicity: Periodicity
        """
        javabridge.call(self.jobject, "setPeriodicity", "(Lweka/filters/supervised/attribute/TSLagMaker$Periodicity;)V", periodicity.jobject)

    @property
    def skip_entries(self):
        """
        Returns a list of time units to be 'skipped' - i.e. not considered as an
        increment. E.g financial markets don't trade on the weekend, so the
        difference between friday closing and the following monday closing is one
        time unit (and not three). Can accept strings such as "sat", "sunday",
        "jan", "august", or explicit dates (with optional formatting string) such
        as "2011-07-04@yyyy-MM-dd", or integers. Integers are interpreted with
        respect to the periodicity - e.g for daily data they are interpreted as day
        of the year; for hourly data, hour of the day; weekly data, week of the
        year.

        :return: the lag range
        :rtype: str
        """
        return javabridge.call(self.jobject, "getSkipEntries", "()Ljava/lang/String;")

    @skip_entries.setter
    def skip_entries(self, lag):
        """
        Sets the list of time units to be 'skipped' - i.e. not considered as an
        increment. E.g financial markets don't trade on the weekend, so the
        difference between friday closing and the following monday closing is one
        time unit (and not three). Can accept strings such as "sat", "sunday",
        "jan", "august", or explicit dates (with optional formatting string) such
        as "2011-07-04@yyyy-MM-dd", or integers. Integers are interpreted with
        respect to the periodicity - e.g for daily data they are interpreted as day
        of the year; for hourly data, hour of the day; weekly data, week of the
        year.

        :param lag: the lag range
        :type lag: str
        """
        javabridge.call(self.jobject, "setSkipEntries", "(Ljava/lang/String;)V", lag)

    def create_time_lag_cross_products(self, data):
        """
        Creates the cross-products.

        :param data: the data to create the cross-products for
        :type data: Instances
        :return: the cross-products
        :rtype: Instances
        """
        return Instances(javabridge.call(self.jobject, "createTimeLagCrossProducts", "(Lweka/core/Instances;)Lweka/core/Instances;", data.jobject))

    def transformed_data(self, data):
        """
        Returns the transformed data.

        :param data: the data to transform
        :type data: Instances
        :return: the transformed data
        :rtype: Instances
        """
        return Instances(javabridge.call(self.jobject, "getTransformedData", "(Lweka/core/Instances;)Lweka/core/Instances;", data.jobject))

    def clear_lag_histories(self):
        """
        Clears any history accumulated in the lag creating filters.
        """
        return javabridge.call(self.jobject, "clearLagHistories", "()V")


class TSForecaster(OptionHandler):
    """
    Wrapper class for timeseries forecasters.
    """

    def __init__(self, classname="weka.classifiers.timeseries.WekaForecaster", jobject=None, options=None):
        """
        Initializes the specified timeseries forecaster using either the classname or the supplied JB_Object.

        :param classname: the classname of the timeseries forecaster
        :type classname: str
        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = TSForecaster.new_instance(classname, options)
            if jobject is None:
                raise Exception(
                    "Failed to instantiate forecaster '%s' - is package 'timeseriesForecasting' installed and jvm started with package support?" % classname)
        self.enforce_type(jobject, "weka.classifiers.timeseries.TSForecaster")
        self._header = None
        super(TSForecaster, self).__init__(jobject=jobject, options=options)

    @property
    def base_model_has_serializer(self):
        """
        Check whether the base learner requires special serialization.

        :return: True if base learner requires special serialization, false otherwise
        :rtype: bool
        """
        return javabridge.call(self.jobject, "baseModelHasSerializer", "()Z")

    def save_base_model(self, fname):
        """
        Saves the base model under the given filename.

        :param fname: the file to save the base model under
        :type fname: str
        """
        javabridge.call(self.jobject, "saveBaseModel", "(Ljava/lang/String;)V", fname)

    def load_base_model(self, fname):
        """
        Loads the base model from the given filename.

        :param fname: the file to load the base model from
        :type fname: str
        """
        javabridge.call(self.jobject, "loadBaseModel", "(Ljava/lang/String;)V", fname)

    @property
    def uses_state(self):
        """
        Check whether the base learner requires operations regarding state.

        :return: True if base learner uses state-based predictions, false otherwise
        :rtype: bool
        """
        return javabridge.call(self.jobject, "usesState", "()Z")

    def clear_previous_state(self):
        """
        Reset model state.
        """
        javabridge.call(self.jobject, "clearPreviousState", "()V")

    @property
    def previous_state(self):
        """
        Returns the previous state.

        :return: the state as list of JB_Object objects
        :rtype: list
        """
        return list(javabridge.get_collection_wrapper(javabridge.call(self.jobject, "getPreviousState", "()Ljava/util/List;")))

    @previous_state.setter
    def previous_state(self, state):
        """
        Sets the previous state.

        :param state: the state to set
        :type state: list
        """
        l = javabridge.JClassWrapper('java.util.ArrayList')()
        for obj in state:
            l.add(obj)
        javabridge.call(self.jobject, "setPreviousState", "(Ljava/util/List;)V")

    def serialize_state(self, fname):
        """
        Serializes the state under the given filename.

        :param fname: the file to serialize the state under
        :type fname: str
        """
        javabridge.call(self.jobject, "serializeState", "(Ljava/lang/String;)V", fname)

    def load_serialized_state(self, fname):
        """
        Loads the serialized state from the given filename.

        :param fname: the file to deserialize the state from
        :type fname: str
        """
        javabridge.call(self.jobject, "loadSerializedState", "(Ljava/lang/String;)V", fname)

    @property
    def algorithm_name(self):
        """
        Returns the name of the algorithm.

        :return: the name
        :rtype: str
        """
        return javabridge.call(self.jobject, "getAlgorithmName", "()Ljava/lang/String;")

    def reset(self):
        """
        Resets the algorithm.
        """
        javabridge.call(self.jobject, "reset", "()V")

    @property
    def fields_to_forecast(self):
        """
        Returns the fields to forecast.

        :return: the fields
        :rtype: str
        """
        return javabridge.call(self.jobject, "getFieldsToForecast", "()Ljava/lang/String;")

    @fields_to_forecast.setter
    def fields_to_forecast(self, fields):
        """
        Sets the fields to forecast.

        :param fields: the comma-separated string or list of fields to forecast
        :type fields: str or list
        """
        if isinstance(fields, list):
            fields = ",".join(fields)
        javabridge.call(self.jobject, "setFieldsToForecast", "(Ljava/lang/String;)V", fields)

    @property
    def header(self):
        """
        Returns the header of the training data.

        :return: the structure of the training data, None if not available
        :rtype: Instances
        """
        return self._header

    def build_forecaster(self, data):
        """
        Builds the forecaster using the provided data.

        :param data: the data to train with
        :type data: Instances
        """
        self._header = data.copy_structure()
        javabridge.call(self.jobject, "buildForecaster", "(Lweka/core/Instances;[Ljava/io/PrintStream;)V", data.jobject, [])

    def prime_forecaster(self, data):
        """
        Primes the forecaster using the provided data.

        :param data: the data to prime with
        :type data: Instances
        """
        javabridge.call(self.jobject, "primeForecaster", "(Lweka/core/Instances;)V", data.jobject)

    def forecast(self, steps):
        """
        Produce a forecast for the target field(s).
        Assumes that the model has been built and/or primed so that a forecast can be generated.

        :param steps: number of forecasted values to produce for each target. E.g. a value of 5 would produce a prediction for t+1, t+2, ..., t+5.
        :type steps: int
        :return: a List of Lists (one for each step) of forecasted values for each target (NumericPrediction objects)
        :rtype: list
        """
        objs1 = javabridge.get_collection_wrapper(javabridge.call(self.jobject, "forecast", "(I[Ljava/io/PrintStream;)Ljava/util/List;", steps, []))
        list1 = []
        for obj1 in objs1:
            list2 = []
            objs2 = javabridge.get_collection_wrapper(obj1)
            for obj2 in objs2:
                list2.append(NumericPrediction(obj2))
            list1.append(list2)
        return list1

    def run_forecaster(self, forecaster, options):
        """
        Builds the forecaster using the provided data.
        """
        javabridge.call(self.jobject, "runForecaster", "(Lweka/classifiers/timeseries/TSForecaster;[Ljava/lang/String;)V", forecaster.jobject, options)


class TSLagUser(JavaObject):
    """
    Wrapper class for TSLagUser objects.
    """

    def __init__(self, jobject):
        """
        Wraps the TSLagUser object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.timeseries.core.TSLagUser")
        super(TSLagUser, self).__init__(jobject=jobject)

    @property
    def tslag_maker(self):
        """
        Returns the base forecaster.

        :return: the base forecaster
        :rtype: Classifier
        """
        return TSLagMaker(jobject=javabridge.call(self.jobject, "getTSLagMaker", "()Lweka/filters/supervised/attribute/TSLagMaker;"))

    @tslag_maker.setter
    def tslag_maker(self, tslag_maker):
        """
        Sets the base forecaster.

        :param tslag_maker: the lag maker to use
        :type tslag_maker: TSLagMaker
        """
        javabridge.call(self.jobject, "setTSLagMaker", "(Lweka/filters/supervised/attribute/TSLagMaker;)V", tslag_maker.jobject)


class ConfidenceIntervalForecaster(JavaObject):
    """
    Wrapper class for ConfidenceIntervalForecaster objects.
    """

    def __init__(self, jobject):
        """
        Wraps a ConfidenceIntervalForecaster object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.timeseries.core.ConfidenceIntervalForecaster")
        super(ConfidenceIntervalForecaster, self).__init__(jobject=jobject)

    @property
    def calculate_conf_intervals_for_forecasts(self):
        """
        Returns the number of steps for which confidence intervals will be computed.

        :return: the steps
        :rtype: int
        """
        return javabridge.call(self.jobject, "getCalculateConfIntervalsForForecasts", "()I")

    @calculate_conf_intervals_for_forecasts.setter
    def calculate_conf_intervals_for_forecasts(self, steps):
        """
        Sets the number of steps for which confidence intervals will be computed.

        :param steps: the steps
        :type steps: int
        """
        javabridge.call(self.jobject, "setCalculateConfIntervalsForForecasts", "(I)V", steps)

    @property
    def is_producing_confidence_intervals(self):
        """
        Returns true if this forecaster is computing confidence limits for some or
        all of its future forecasts (i.e. getCalculateConfIntervalsForForecasts() >
        0).

        :return: true if confidence intervals are produced
        :rtype: bool
        """
        return javabridge.call(self.jobject, "isProducingConfidenceIntervals", "()I")

    @property
    def confidence_level(self):
        """
        Returns the confidence level in use for computing confidence intervals.

        :return: the level
        :rtype: float
        """
        return javabridge.call(self.jobject, "getOverlayFields", "()Ljava/lang/String;")

    @confidence_level.setter
    def confidence_level(self, level):
        """
        Sets the confidence level in use for computing confidence intervals.

        :param level: the level
        :type level: float
        """
        javabridge.call(self.jobject, "setOverlayFields", "(Ljava/lang/String;)V", level)


class OverlayForecaster(JavaObject):
    """
    Wrapper class for OverlayForecaster objects.
    """

    def __init__(self, jobject):
        """
        Wraps a OverlayForecaster object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.timeseries.core.OverlayForecaster")
        super(OverlayForecaster, self).__init__(jobject=jobject)

    @property
    def overlay_fields(self):
        """
        Returns the overlay fields as string.

        :return: the overlay fields
        :rtype: str
        """
        return javabridge.call(self.jobject, "getOverlayFields", "()Ljava/lang/String;")

    @overlay_fields.setter
    def overlay_fields(self, fields):
        """
        Sets the overlay fields as string.

        :param fields: the overlay fields
        :type fields: str
        """
        javabridge.call(self.jobject, "setOverlayFields", "(Ljava/lang/String;)V", fields)

    @property
    def is_using_overlay_data(self):
        """
        Returns true if overlay data has been used to train this forecaster, and
        thus is expected to be supplied for future time steps when making a
        forecast.

        :return:
        """
        return javabridge.call(self.jobject, "isUsingOverlayData", "()Z")

    def forecast_with_overlays(self, steps, overlays):
        """
        Produce a forecast for the target field(s). Assumes that the model has been built
        and/or primed so that a forecast can be generated. Also assumes that
        the forecaster has been told which attributes are to be considered
        "overlay" attributes in the data. Overlay data is data that the
        forecaster will be provided with when making a forecast into the future - i.e.
        it will be given the values of these attributes for future instances. The
        overlay data provided to this method should have the same structure as
        the original data used to train the forecaster - i.e. all original fields
        should be present, including the targets and time stamp field (if supplied).
        The values of targets will of course be missing ('?') since we want to forecast
        those. The time stamp values (if a time stamp is in use) may be provided, in which
        case the forecaster will use the time stamp values in the overlay instances. If
        the time stamp values are missing, then date arithmetic (for date time stamps) will
        be used to advance the time value beyond the last seen training value;
        similarly, for artificial time stamps or non-date time stamps, the computed
        time delta will be used to increment beyond the last seen training value.

        The number of instances in the overlay data should typically match the number
        of steps that have been requested for forecasting. If these differ, then
        overlay.numInstances() will be the number of steps forecasted.

        :param steps: number of forecasted values to produce for each target. E.g. a value of 5 would produce a prediction for t+1, t+2, ..., t+5.
        :type steps: int
        :param overlays: the overlay data to use
        :type overlays: Instances
        :return: a List of Lists (one for each step) of forecasted values for each target (NumericPrediction objects)
        :rtype: list
        """
        objs1 = javabridge.get_collection_wrapper(javabridge.call(self.jobject, "forecast", "(Lweka/core/Instances;I[Ljava/io/PrintStream;)Ljava/util/List;", steps, overlays.jobject, []))
        list1 = []
        for obj1 in objs1:
            list2 = []
            objs2 = javabridge.get_collection_wrapper(obj1)
            for obj2 in objs2:
                list2.append(NumericPrediction(obj2))
            list1.append(list2)
        return list1


class IncrementallyPrimeable(JavaObject):
    """
    Wrapper class for IncrementallyPrimeable objects.
    """

    def __init__(self, jobject):
        """
        Wraps a IncrementallyPrimeable object.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        """
        self.enforce_type(jobject, "weka.classifiers.timeseries.core.IncrementallyPrimeable")
        super(IncrementallyPrimeable, self).__init__(jobject=jobject)

    def prime_forecaster_incremental(self, inst):
        """
        Primes the forecaster using the provided data.

        :param inst: the instance to prime with
        :type inst: Instance
        """
        javabridge.call(self.jobject, "primeForecasterIncremental", "(Lweka/core/Instance;)V", inst.jobject)


class WekaForecaster(TSForecaster, TSLagUser, ConfidenceIntervalForecaster, OverlayForecaster, IncrementallyPrimeable):
    """
    Wrapper class for Weka timeseries forecasters.
    """

    def __init__(self, jobject=None, options=None):
        """
        Initializes a Weka timeseries forecaster.

        :param jobject: the JB_Object to use
        :type jobject: JB_Object
        :param options: the list of commandline options to set
        :type options: list
        """
        if jobject is None:
            jobject = new_instance("weka.classifiers.timeseries.WekaForecaster")
        super(WekaForecaster, self).__init__(jobject=jobject, options=options)

    def clear_custom_periodics(self):
        """
        Clears the custom periodics.
        """
        javabridge.call(self.jobject, "clearCustomPeriodics", "()V")

    def add_custom_periodic(self, periodic):
        """
        Adds the custom periodic.

        :param periodic: the periodic to add
        :type periodic: str
        """
        javabridge.call(self.jobject, "addCustomPeriodic", "(Ljava/lang/String;)V", periodic)

    @property
    def base_forecaster(self):
        """
        Returns the base forecaster.

        :return: the base forecaster
        :rtype: Classifier
        """
        return Classifier(jobject=javabridge.call(self.jobject, "getBaseForecaster", "()Lweka/classifiers/Classifier;"))

    @base_forecaster.setter
    def base_forecaster(self, base_forecaster):
        """
        Sets the base forecaster.

        :param base_forecaster: the base forecaster to use
        :type base_forecaster: Classifier
        """
        javabridge.call(self.jobject, "setBaseForecaster", "(Lweka/classifiers/Classifier;)V", base_forecaster.jobject)


class TSEvalModule(JavaObject):
    """
    Wrapper for TSEvalModule objects.
    """

    def __init__(self, jobject):
        """
        Initializes the evaluation module.

        :param jobject: the object to initialize with
        :type jobject: JB_Object
        """
        super(TSEvalModule, self).__init__(jobject)

    def reset(self):
        """
        Resets the module.
        """
        javabridge.call(self.jobject, "reset", "()V")

    @property
    def eval_name(self):
        """
        Returns the name.
        """
        return javabridge.call(self.jobject, "getEvalName", "()Ljava/lang/String;")

    @property
    def description(self):
        """
        Returns the description.
        """
        return javabridge.call(self.jobject, "getDescription", "()Ljava/lang/String;")

    @property
    def definition(self):
        """
        Returns the description.
        """
        return javabridge.call(self.jobject, "getDefinition", "()Ljava/lang/String;")

    def evaluate_for_instance(self, pred, inst):
        """
        Evaluate the given forecast(s) with respect to the given test instance. Targets with missing values are ignored.

        :param pred: the numeric prediction
        :type pred: NumericPrediction
        :param inst: the instance
        :type inst: Instance
        """
        javabridge.call(self.jobject, "evaluateForInstance", "(Ljava/util/List;Lweka/core/Instance;)V", pred.jobject, inst.jobject)

    def calculate_measure(self):
        """
        Calculate the measure that this module represents.

        :return: the value of the measure for this module for each of the target(s).
        :rtype: ndarray
        """
        result = javabridge.call(self.jobject, "calculateMeasure", "()[D")
        return javabridge.get_env().get_double_array_elements(result)

    @property
    def summary(self):
        """
        Returns the description.
        """
        return javabridge.call(self.jobject, "toSummaryString", "()Ljava/lang/String;")

    @property
    def target_fields(self):
        """
        Returns the list of target fields.

        :return: the list of target fields
        :rtype: list
        """
        return jstring_list_to_string_list(javabridge.call(self.jobject, "getTargetFields", "()Ljava/util/List;"))

    @target_fields.setter
    def target_fields(self, fields):
        """
        Sets the list of target fields.

        :param fields: the list of target fields
        :type fields: list
        """
        javabridge.call(self.jobject, "setTargetFields", "(Ljava/util/List;)V", fields)

    def __str__(self):
        """
        Returns the name.
        """
        return self.eval_name

    @classmethod
    def module_list(cls):
        """
        Returns list of available modules.

        :return: the list of modules (TSEvalModule objects)
        :rtype: list
        """
        result = []
        objs = javabridge.get_collection_wrapper(javabridge.static_call(
            "Lweka/classifiers/timeseries/eval/TSEvalModuleHelper;", "getModuleList",
            "()Ljava/util/List;"))
        for obj in objs:
            result.append(TSEvalModule(obj))
        return result

    @classmethod
    def module(cls, name):
        """
        Returns the module with the specified name.

        :param name: the name of the module to return
        :type name: str
        :return: the TSEvalModule object
        :rtype: TSEvalModule
        """
        return TSEvalModule(javabridge.static_call(
            "Lweka/classifiers/timeseries/eval/TSEvalModuleHelper;", "getModule",
            "(Ljava/lang/String;)Ljava/lang/Object;", name))


class ErrorModule(TSEvalModule):
    """
    Wrapper for ErrorModule objects.
    """

    def __init__(self, jobject):
        """
        Initializes the error module.

        :param jobject: the object to initialize with
        :type jobject: JB_Object
        """
        super(ErrorModule, self).__init__(jobject)

    def counts_for_targets(self):
        """
        Returns the number of predicted, actual pairs for each target. Only
        entries that are non-missing for both actual and predicted contribute
        to the overall count.

        :return: the number of predicted, actual pairs for each target.
        :rtype: ndarray
        """
        result = javabridge.call(self.jobject, "countsForTargets", "()[D")
        return javabridge.get_env().get_double_array_elements(result)

    def errors_for_target(self, target):
        """
        Returns the list of the errors for the supplied target.

        :param target: the target to get the errors for
        :type target: str
        :return: the errors
        :rtype: list
        """
        result = []
        objs = javabridge.get_collection_wrapper(javabridge.call(self.jobject, "getErrorsForTarget", "(Ljava/lang/String;)Ljava/util/List;", target))
        for obj in objs:
            result.append(jdouble_to_float(obj))
        return result

    def predictions_for_target(self, target):
        """
        Returns the list of predictions for the target.

        :param target: the target to get the predictions for
        :type target: str
        :return: list of NumericPrediction
        :rtype: list
        """
        result = []
        objs = javabridge.get_collection_wrapper(javabridge.call(self.jobject, "getPredictionsForTarget", "(Ljava/lang/String;)Ljava/util/List;", target))
        for obj in objs:
            result.append(NumericPrediction(obj))
        return result

    def predictions_for_all_targets(self):
        """
        Returns the list of predictions for all targets.

        :return: list of list of NumericPrediction
        :rtype: list
        """
        result1 = []
        objs1 = javabridge.get_collection_wrapper(javabridge.call(self.jobject, "getPredictionsForAllTargets", "()Ljava/util/List;"))
        for obj1 in objs1:
            objs2 = javabridge.get_collection_wrapper(obj1)
            result2 = []
            for obj2 in objs2:
                result2.append(NumericPrediction(obj2))
            result1.append(result2)
        return result1


class TSEvaluation(JavaObject):
    """
    Evaluation class for timeseries forecasters.
    """

    def __init__(self, train, test_split_size=0.3, test=None):
        """
        Initializes a TSEvaluation object.

        :param train: the training data to use
        :type train: Instances
        :param test_split_size: the number or percentage of instances to hold out from the end of the training data to be test data.
        :type test_split_size: float
        :param test: the explicit test set to use, overrides the split size
        :type test: Instances
        """
        if test is None:
            jobject = javabridge.static_call(
                "Lweka/classifiers/timeseries/eval/TSEvaluationHelper;", "newInstance",
                "(Lweka/core/Instances;D)Ljava/lang/Object;",
                train.jobject, test_split_size)
        else:
            jobject = javabridge.static_call(
                "Lweka/classifiers/timeseries/eval/TSEvaluationHelper;", "newInstance",
                "(Lweka/core/Instances;Lweka/core/Instances;)Ljava/lang/Object;",
                train.jobject, test.jobject)
        super(TSEvaluation, self).__init__(jobject)

        # set up variables
        self._horizon = None
        self._rebuild_model_after_each_test_forecast_step = None

        # initialize with values from Java class
        self.horizon = 1
        self.rebuild_model_after_each_test_forecast_step = False

    @property
    def training_data(self):
        """
        Returns the training data.

        :return: the training data, None if none available
        :rtype: Instances
        """
        data = javabridge.call(self.jobject, "getTrainingData", "()Lweka/core/Instances;")
        if data is None:
            return None
        else:
            return Instances(data)

    @training_data.setter
    def training_data(self, data):
        """
        Sets the training data.

        :param data: the training data
        :type data: Instances
        """
        javabridge.call(self.jobject, "setTrainingData", "(Lweka/core/Instances;)V", data.jobject)

    @property
    def test_data(self):
        """
        Returns the test data.

        :return: the test data, None if none available
        :rtype: Instances
        """
        data = javabridge.call(self.jobject, "getTestData", "()Lweka/core/Instances;")
        if data is None:
            return None
        else:
            return Instances(data)

    @test_data.setter
    def test_data(self, data):
        """
        Sets the test data.

        :param data: the test data
        :type data: Instances
        """
        javabridge.call(self.jobject, "setTestData", "(Lweka/core/Instances;)V", data.jobject)

    @property
    def evaluate_on_training_data(self):
        """
        Returns whether to evaluate on the training data.

        :return: whether to evaluate
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getEvaluateOnTrainingData", "()Z")

    @evaluate_on_training_data.setter
    def evaluate_on_training_data(self, evaluate):
        """
        Sets whether whether to evaluate on to training data.

        :param evaluate: whether to evaluate
        :type evaluate: bool
        """
        javabridge.call(self.jobject, "setEvaluateOnTrainingData", "(Z)V", evaluate)

    @property
    def evaluate_on_test_data(self):
        """
        Returns whether to evaluate on the test data.

        :return: whether to evaluate
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getEvaluateOnTestData", "()Z")

    @evaluate_on_test_data.setter
    def evaluate_on_test_data(self, evaluate):
        """
        Sets whether whether to evaluate on to test data.

        :param evaluate: whether to evaluate
        :type evaluate: bool
        """
        javabridge.call(self.jobject, "setEvaluateOnTestData", "(Z)V", evaluate)

    @property
    def horizon(self):
        """
        Returns the number of steps to predict into the future.

        :return: the number of steps
        :rtype: int
        """
        return self._horizon

    @horizon.setter
    def horizon(self, steps):
        """
        Sets the number of steps to predict into the future.

        :param steps: the number of steps
        :type steps: int
        """
        javabridge.call(self.jobject, "setHorizon", "(I)V", steps)
        self._horizon = steps

    @property
    def prime_window_size(self):
        """
        Returns the size of the priming window, ie the number of historical instances to present before making a forecast.

        :return: the size
        :rtype: int
        """
        return javabridge.call(self.jobject, "getPrimeWindowSize", "()I")

    @prime_window_size.setter
    def prime_window_size(self, size):
        """
        Sets the size of the priming window, ie the number of historical instances to present before making a forecast.

        :param size: the size
        :type size: int
        """
        javabridge.call(self.jobject, "setPrimeWindowSize", "(I)V", size)

    @property
    def prime_for_test_data_with_test_data(self):
        """
        Returns whether evaluation for test data should begin by priming with the first
        x test data instances and then forecasting from step x + 1. This is the
        only option if there is no training data and a model has been deserialized
        from disk. If we have training data, and it occurs immediately before the
        test data in time, then we can prime with the last x instances from the
        training data.

        :return: whether to prime
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getPrimeForTestDataWithTestData", "()Z")

    @prime_for_test_data_with_test_data.setter
    def prime_for_test_data_with_test_data(self, prime):
        """
        Sets whether evaluation for test data should begin by priming with the first
        x test data instances and then forecasting from step x + 1. This is the
        only option if there is no training data and a model has been deserialized
        from disk. If we have training data, and it occurs immediately before the
        test data in time, then we can prime with the last x instances from the
        training data.

        :param prime: whether to prime
        :type prime: bool
        """
        javabridge.call(self.jobject, "setPrimeForTestDataWithTestData", "(Z)V", prime)

    @property
    def rebuild_model_after_each_test_forecast_step(self):
        """
        Returns whether the forecasting model should be rebuilt after each forecasting
        step on the test data using both the training data and test data up to the
        current instance.

        :return: whether to rebuild
        :rtype: bool
        """
        return self._rebuild_model_after_each_test_forecast_step

    @rebuild_model_after_each_test_forecast_step.setter
    def rebuild_model_after_each_test_forecast_step(self, rebuild):
        """
        Sets whether the forecasting model should be rebuilt after each forecasting
        step on the test data using both the training data and test data up to the
        current instance.

        :param rebuild: whether to rebuild
        :return: bool
        """
        javabridge.call(self.jobject, "setRebuildModelAfterEachTestForecastStep", "(Z)V", rebuild)
        self._rebuild_model_after_each_test_forecast_step = rebuild

    @property
    def forecast_future(self):
        """
        Returns whether we should generate a future forecast beyond the end of the
        training and/or test data.

        :return: whether to prime
        :rtype: bool
        """
        return javabridge.call(self.jobject, "getForecastFuture", "()Z")

    @forecast_future.setter
    def forecast_future(self, prime):
        """
        Sets whether we should generate a future forecast beyond the end of the
        training and/or test data.

        :param prime: whether to prime
        :type prime: bool
        """
        javabridge.call(self.jobject, "setForecastFuture", "(Z)V", prime)

    @property
    def evaluation_modules(self):
        """
        Returns the list of evaluation modules in use.

        :return: list of TSEvalModule object
        :rtype: list
        """
        result = []
        objs = javabridge.get_collection_wrapper(javabridge.call(self.jobject, "getEvaluationModules", "()Ljava/util/List;"))
        for obj in objs:
            result.append(TSEvalModule(obj))
        return result

    @evaluation_modules.setter
    def evaluation_modules(self, modules):
        """
        Sets the evaluation modules to use (comma-separated list or list of TSEvalModule/str objects).

        :param modules: the evaluation modules (str or list)
        :type modules: str
        """
        if isinstance(modules, list):
            modules = [str(module) for module in modules]
            modules.remove("Error")  # requires manual removal
            modules = ",".join(modules)
        javabridge.call(self.jobject, "setEvaluationModules", "(Ljava/lang/String;)V", modules)

    def __str__(self):
        """
        Prints a simple summary of the evaluation setup.

        :return: the summary
        :rtype: str
        """
        eval_modules = [x.eval_name for x in self.evaluation_modules]

        result = "=== Evaluation setup ===\n\n"
        if self.training_data is not None:
            result += "Relation: " + self.training_data.relationname + "\n" \
                      + "# Training instances: " + str(self.training_data.num_instances) + "\n"
        if self.test_data is not None:
            result +="# Test instances: " + str(self.test_data.num_instances) + "\n"
        result += "Evaluate on training data: " + str(self.evaluate_on_training_data) + "\n" \
                  + "Evaluate on test data: " + str(self.evaluate_on_test_data) + "\n" \
                  + "Horizon: " + str(self.horizon) + "\n" \
                  + "Prime window size: " + str(self.prime_window_size) + "\n" \
                  + "Prime for test data with test data: " + str(self.prime_for_test_data_with_test_data) + "\n" \
                  + "Rebuild model after each test forecast step: " + str(self.rebuild_model_after_each_test_forecast_step) + "\n" \
                  + "Forecast future: " + str(self.forecast_future) + "\n" \
                  + "Evaluation modules: " + ", ".join(eval_modules) + "\n" \
                  + "\n"
        return result

    def evaluate(self, forecaster, build_model=True):
        """
        Evaluates the forecaster.

        :param forecaster: the forecaster to evaluate
        :type forecaster: TSForecaster
        :param build_model: whether to build the model as well
        :type build_model: bool
        """
        javabridge.call(
            self.jobject, "evaluateForecaster",
            "(Lweka/classifiers/timeseries/TSForecaster;Z[Ljava/io/PrintStream;)V",
            forecaster.jobject, build_model, [])

    def predictions_for_training_data(self, step_number):
        """
        Predictions for all targets for the specified step number on the training data.

        :param step_number: number of the step into the future to return predictions for
        :type step_number: int
        """
        return ErrorModule(javabridge.call(
            self.jobject, "getPredictionsForTrainingData",
            "(I)Lweka/classifiers/timeseries/eval/ErrorModule;",
            step_number))

    def predictions_for_test_data(self, step_number):
        """
        Predictions for all targets for the specified step number on the test data.

        :param step_number: number of the step into the future to return predictions for
        :type step_number: int
        """
        return ErrorModule(javabridge.call(
            self.jobject, "getPredictionsForTestData",
            "(I)Lweka/classifiers/timeseries/eval/ErrorModule;",
            step_number))

    def print_future_forecast_on_training_data(self, forecaster):
        """
        Print the forecasted values (for all targets) beyond the end of the training data.

        :param forecaster: the forecaster to use
        :type forecaster: TSForecaster
        :return: the forecasted values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printFutureTrainingForecast",
            "(Lweka/classifiers/timeseries/TSForecaster;)Ljava/lang/String;", forecaster.jobject)

    def print_future_forecast_on_test_data(self, forecaster):
        """
        Print the forecasted values (for all targets) beyond the end of the test data.

        :param forecaster: the forecaster to use
        :type forecaster: TSForecaster
        :return: the forecasted values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printFutureTestForecast",
            "(Lweka/classifiers/timeseries/TSForecaster;)Ljava/lang/String;", forecaster.jobject)

    def print_predictions_for_training_data(self, title, target_name, step_ahead, instance_number_offset=0):
        """
        Print the predictions for a given target at a given step-ahead level on the training data.

        :param title: the title for the output
        :type title: str
        :param target_name: the name of the target to print predictions for
        :type target_name: str
        :param step_ahead: the step-ahead level - e.g. 3 would print the 3-step-ahead predictions
        :type step_ahead: int
        :param instance_number_offset: the offset from the start of the training data from which to print actual and predicted values
        :type instance_number_offset: int
        :return: the predicted/actual values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printPredictionsForTrainingData",
            "(Ljava/lang/String;Ljava/lang/String;II)Ljava/lang/String;", title, target_name, step_ahead, instance_number_offset)

    def print_predictions_for_test_data(self, title, target_name, step_ahead, instance_number_offset=0):
        """
        Print the predictions for a given target at a given step-ahead level on the test data.

        :param title: the title for the output
        :type title: str
        :param target_name: the name of the target to print predictions for
        :type target_name: str
        :param step_ahead: the step-ahead level - e.g. 3 would print the 3-step-ahead predictions
        :type step_ahead: int
        :param instance_number_offset: the offset from the start of the test data from which to print actual and predicted values
        :type instance_number_offset: int
        :return: the predicted/actual values
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "printPredictionsForTestData",
            "(Ljava/lang/String;Ljava/lang/String;II)Ljava/lang/String;", title, target_name, step_ahead, instance_number_offset)

    def summary(self):
        """
        Generates a summary.

        :return: the summary
        :rtype: str
        """
        return javabridge.call(
            self.jobject, "toSummaryString", "()Ljava/lang/String;")

    @classmethod
    def evaluate_forecaster(cls, forecaster, args):
        """
        Evaluates the forecaster with the given options.

        :param forecaster: the forecaster instance to use
        :type forecaster: TSForecaster
        :param args: the command-line arguments to use
        :type args: list
        """
        javabridge.static_call(
            "Lweka/classifiers/timeseries/eval/TSEvaluation;", "evaluateForecaster",
            "(Lweka/classifiers/timeseries/TSForecaster;[Ljava/lang/String;)Ljava/lang/String;",
            forecaster.jobject, args)
