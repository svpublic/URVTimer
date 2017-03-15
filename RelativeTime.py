class RelativeTime:
    """Класс для работы со временем"""

    WEEK = "week"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"
    SECOND = "second"

    SEC_IN_MIN = 60
    SEC_IN_HR = 3600
    SEC_IN_DAY = 86400
    SEC_IN_WK = 604800
    MIN_IN_HR = 60
    MIN_IN_DAY = 1140
    MIN_IN_WK = 10080
    HR_IN_DAY = 24
    HR_IN_WK = 168
    DAYS_IN_WK = 7

    def __init__(self, weeks=0, days=0, hours=0, minutes=0, seconds=0, total_seconds=0):
        self.total_seconds = total_seconds
        if total_seconds == 0:
            self.total_seconds = (
                weeks * self.SEC_IN_WK +
                days * self.SEC_IN_DAY +
                hours * self.SEC_IN_HR +
                minutes * self.SEC_IN_MIN +
                seconds
            )

        self.weeks, residue = divmod(abs(self.total_seconds), self.SEC_IN_WK)
        self.days, residue = divmod(residue, self.SEC_IN_DAY)
        self.hours, residue = divmod(residue, self.SEC_IN_HR)
        self.minutes, self.seconds = divmod(residue, self.SEC_IN_MIN)

        if self.total_seconds < 0:
            self.weeks *= -1
            self.days *= -1
            self.hours *= -1
            self.minutes *= -1
            self.seconds *= -1

    def convert(self, max_unit):
        if max_unit == self.WEEK:
            return [self.weeks, self.days, self.hours, self.minutes, self.seconds]
        elif max_unit == self.DAY:
            return [(self.days + self.weeks*self.DAYS_IN_WK), self.hours, self.minutes, self.seconds]
        elif max_unit == self.HOUR:
            return [(self.hours + self.weeks*self.HR_IN_WK + self.days*self.HR_IN_DAY), self.minutes, self.seconds]
        elif max_unit == self.MINUTE:
            return [(self.minutes + self.weeks*self.MIN_IN_WK + self.days*self.MIN_IN_DAY + self.hours*self.MIN_IN_HR), self.seconds]
        elif max_unit == self.SECOND:
            return [self.total_seconds]

    def __add__(self, other):
        result = self.total_seconds + other.total_seconds
        return RelativeTime(total_seconds=result)

    def __sub__(self, other):
        result = self.total_seconds - other.total_seconds
        return RelativeTime(total_seconds=result)

    def format(self, template):
        if template == "hh:mm":
            time = self.convert(self.HOUR)
            return "{0}:{1}".format(self.two_digit(time[0]), self.two_digit(time[1]))
        else:
            time = self.convert(self.WEEK)
            return "{0}w:{1}d:{2}h:{3}m:{4}s".format(time[0], time[1], time[2], time[3], time[4])

    @staticmethod
    def two_digit(value):
        return "{:02}".format(value)
