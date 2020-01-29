from bulb.utils.log import bulb_logger
import datetime


class BULBQError(Exception):
    pass


class Qstr(str):
    """
    :param complex_query: A simple query is when the search is done on the self instance properties (example:
                          "user__name='John'". And a complex query is when the search is focused on the instances
                          related (with a relationship) to the self instance (example: user__friends__name="John", we
                          search all the friends with name="John")
    """

    def __or__(self, other):
        self_statement = Qstr(self)

        if isinstance(other, Qstr):
            return Qstr(self_statement + " OR " + other)

        elif isinstance(other, Q):
            other_statement = other.filter

            if not other.complex_query:
                return Qstr(self_statement + " OR " + other_statement)

        else:
            bulb_logger.error('BULBQError("Q queries must contains only Q instances.")')
            raise BULBQError("Q queries must contains only Q instances.")

    def __and__(self, other):
        self_statement = Qstr(self)

        if isinstance(other, Qstr):
            return Qstr(self_statement + " AND " + other)

        elif isinstance(other, Q):
            other_statement = other.filter
            return Qstr(self_statement + " AND " + other_statement)

        else:
            bulb_logger.error('BULBQError("Q queries must contains only Q instances.")')
            raise BULBQError("Q queries must contains only Q instances.")


class Q:
    def __init__(self, complex_query=False):
        self.complex_query = complex_query

    def __new__(cls, **kwargs):
        instance = super().__new__(cls)
        instance.filter = kwargs
        instance.build_filter()
        return instance.filter

    def __or__(self, other):
        self_statement = Qstr(self.filter)

        if isinstance(other, Qstr):
            return Qstr(self_statement + " OR " + other)

        elif isinstance(other, Q):
            other_statement = other.filter
            return Qstr(self_statement + " OR " + other_statement)

        else:
            bulb_logger.error('BULBQError("Q queries must contains only Q instances.")')
            raise BULBQError("Q queries must contains only Q instances.")

    def __and__(self, other):
        self_statement = Qstr(self.filter)

        if isinstance(other, Qstr):
            return Qstr(self_statement + " AND " + other)

        elif isinstance(other, Q):
            other_statement = other.filter
            return Qstr(self_statement + " AND " + other_statement)

        else:
            bulb_logger.error('BULBQError("Q queries must contains only Q instances.")')
            raise BULBQError("Q queries must contains only Q instances.")

    def build_filter(self):
        for property_name, property_value in self.filter.items():
            filter_list = property_name.split("__")

            if len(filter_list) == 2:
                parameter_name = filter_list[0]
                action = filter_list[1]

                # Structure filters.
                if action == "startswith":
                    self.filter = Qstr(f"n.{parameter_name} STARTS WITH '{property_value}'")

                elif action == "endswith":
                    self.filter = Qstr(f"n.{parameter_name} ENDS WITH '{property_value}'")

                elif action == "contains":
                    self.filter = Qstr(f"n.{parameter_name} CONTAINS '{property_value}'")

                elif action == "regex":
                    self.filter = Qstr(f"n.{parameter_name} =~ '{property_value}'")

                elif action == "exact":
                    if isinstance(property_value, bool) or isinstance(property_value, int) or isinstance(property_value, list):
                        self.filter = Qstr(f"n.{parameter_name} = {property_value}")

                    elif isinstance(property_value, datetime.datetime):
                        self.filter = Qstr(f"n.{parameter_name} = datetime('{property_value}')")

                    elif isinstance(property_value, datetime.date):
                        self.filter = Qstr(f"n.{parameter_name} = date('{property_value}')")

                    elif isinstance(property_value, datetime.time):
                        self.filter = Qstr(f"n.{parameter_name} = time('{property_value}')")

                    elif isinstance(property_value, str):
                        self.filter = Qstr(f"n.{parameter_name} = '{property_value}'")

                    else:
                        self.filter = Qstr(f"n.{parameter_name} = '{property_value}'")

                # Case insensitive structure filters.
                elif action == "istartswith":
                    self.filter = Qstr(f"n.{parameter_name} =~ '(?i){property_value}(.*)'")

                elif action == "iendswith":
                    self.filter = Qstr(f"n.{parameter_name} =~ '(?i)(.*){property_value}'")

                elif action == "icontains":
                    self.filter = Qstr(f"n.{parameter_name} =~ '(?i)(.*){property_value}(.*)'")

                elif action == "iregex":
                    self.filter = Qstr(f"n.{parameter_name} =~ '(?i){property_value}'")

                elif action == "iexact":
                    if isinstance(property_value, bool) or isinstance(property_value, int) or isinstance(property_value, list):
                        self.filter = Qstr(f"n.{parameter_name} = {property_value}")

                    elif isinstance(property_value, datetime.datetime):
                        self.filter = Qstr(f"n.{parameter_name} = datetime('{property_value}')")

                    elif isinstance(property_value, datetime.date):
                        self.filter = Qstr(f"n.{parameter_name} = date('{property_value}')")

                    elif isinstance(property_value, datetime.time):
                        self.filter = Qstr(f"n.{parameter_name} = time('{property_value}')")

                    elif isinstance(property_value, str):
                        self.filter = Qstr(f"n.{parameter_name} =~ '(?i){property_value}'")

                    else:
                        self.filter = Qstr(f"n.{parameter_name} =~ '(?i){property_value}'")

                # Quantity and datetime filters.
                elif action == "lt":
                    if isinstance(property_value, int):
                        self.filter = Qstr(f"n.{parameter_name} < {property_value}")

                    elif isinstance(property_value, datetime.datetime):
                        self.filter = Qstr(f"n.{parameter_name} < datetime('{property_value}')")

                    elif isinstance(property_value, datetime.date):
                        self.filter = Qstr(f"n.{parameter_name} < date('{property_value}')")

                    elif isinstance(property_value, datetime.time):
                        self.filter = Qstr(f"n.{parameter_name} < time('{property_value}')")

                elif action == "gt":
                    if isinstance(property_value, int):
                        self.filter = Qstr(f"n.{parameter_name} > {property_value}")

                    elif isinstance(property_value, datetime.datetime):
                        self.filter = Qstr(f"n.{parameter_name} > datetime('{property_value}')")

                    elif isinstance(property_value, datetime.date):
                        self.filter = Qstr(f"n.{parameter_name} > date('{property_value}')")

                    elif isinstance(property_value, datetime.time):
                        self.filter = Qstr(f"n.{parameter_name} > time('{property_value}')")

                elif action == "lte":
                    if isinstance(property_value, int):
                        self.filter = Qstr(f"n.{parameter_name} <= {property_value}")

                    elif isinstance(property_value, datetime.datetime):
                        self.filter = Qstr(f"n.{parameter_name} <= datetime('{property_value}')")

                    elif isinstance(property_value, datetime.date):
                        self.filter = Qstr(f"n.{parameter_name} <= date('{property_value}')")

                    elif isinstance(property_value, datetime.time):
                        self.filter = Qstr(f"n.{parameter_name} <= time('{property_value}')")

                elif action == "gte":
                    if isinstance(property_value, int):
                        self.filter = Qstr(f"n.{parameter_name} >= {property_value}")

                    elif isinstance(property_value, datetime.datetime):
                        self.filter = Qstr(f"n.{parameter_name} >= datetime('{property_value}')")

                    elif isinstance(property_value, datetime.date):
                        self.filter = Qstr(f"n.{parameter_name} >= date('{property_value}')")

                    elif isinstance(property_value, datetime.time):
                        self.filter = Qstr(f"n.{parameter_name} >= time('{property_value}')")

                # Year.
                elif action == "year" or action == "year_exact":
                    self.filter = Qstr(f"date(n.{parameter_name}).year = {property_value}")

                elif action == "year_lt":
                    self.filter = Qstr(f"date(n.{parameter_name}).year < {property_value}")

                elif action == "year_gt":
                    self.filter = Qstr(f"date(n.{parameter_name}).year > {property_value}")

                elif action == "year_lte":
                    self.filter = Qstr(f"date(n.{parameter_name}).year <= {property_value}")

                elif action == "year_gte":
                    self.filter = Qstr(f"date(n.{parameter_name}).year >= {property_value}")

                # Month.
                elif action == "month" or action == "month_exact":
                    self.filter = Qstr(f"date(n.{parameter_name}).month = {property_value}")

                elif action == "month_lt":
                    self.filter = Qstr(f"date(n.{parameter_name}).month < {property_value}")

                elif action == "month_gt":
                    self.filter = Qstr(f"date(n.{parameter_name}).month > {property_value}")

                elif action == "month_lte":
                    self.filter = Qstr(f"date(n.{parameter_name}).month <= {property_value}")

                elif action == "month_gte":
                    self.filter = Qstr(f"date(n.{parameter_name}).month >= {property_value}")

                # Day.
                elif action == "day" or action == "day_exact":
                    self.filter = Qstr(f"date(n.{parameter_name}).day = {property_value}")

                elif action == "day_lt":
                    self.filter = Qstr(f"date(n.{parameter_name}).day < {property_value}")

                elif action == "day_gt":
                    self.filter = Qstr(f"date(n.{parameter_name}).day > {property_value}")

                elif action == "day_lte":
                    self.filter = Qstr(f"date(n.{parameter_name}).day <= {property_value}")

                elif action == "day_gte":
                    self.filter = Qstr(f"date(n.{parameter_name}).day >= {property_value}")

                # Hour.
                elif action == "hour" or action == "hour_exact":
                    self.filter = Qstr(f"time(n.{parameter_name}).hour = {property_value}")

                elif action == "hour_lt":
                    self.filter = Qstr(f"time(n.{parameter_name}).hour < {property_value}")

                elif action == "hour_gt":
                    self.filter = Qstr(f"time(n.{parameter_name}).hour > {property_value}")

                elif action == "hour_lte":
                    self.filter = Qstr(f"time(n.{parameter_name}).hour <= {property_value}")

                elif action == "hour_gte":
                    self.filter = Qstr(f"time(n.{parameter_name}).hour >= {property_value}")

                # Minute.
                elif action == "minute" or action == "minute_exact":
                    self.filter = Qstr(f"time(n.{parameter_name}).minute = {property_value}")

                elif action == "minute_lt":
                    self.filter = Qstr(f"time(n.{parameter_name}).minute < {property_value}")

                elif action == "minute_gt":
                    self.filter = Qstr(f"time(n.{parameter_name}).minute > {property_value}")

                elif action == "minute_lte":
                    self.filter = Qstr(f"time(n.{parameter_name}).minute <= {property_value}")

                elif action == "minute_gte":
                    self.filter = Qstr(f"time(n.{parameter_name}).minute >= {property_value}")

                # Second.
                elif action == "second" or action == "second_exact":
                    self.filter = Qstr(f"time(n.{parameter_name}).second = {property_value}")

                elif action == "second_lt":
                    self.filter = Qstr(f"time(n.{parameter_name}).second < {property_value}")

                elif action == "second_gt":
                    self.filter = Qstr(f"time(n.{parameter_name}).second > {property_value}")

                elif action == "second_lte":
                    self.filter = Qstr(f"time(n.{parameter_name}).second <= {property_value}")

                elif action == "second_gte":
                    self.filter = Qstr(f"time(n.{parameter_name}).second >= {property_value}")

            else:
                bulb_logger.error(
                    'BULBQError("Q queries must respect the syntax : \'param__action=property_value\'")')
                raise BULBQError("Q queries must respect the syntax : 'param__action=property_value'")
