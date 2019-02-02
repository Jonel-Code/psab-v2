import enum


class YearEnum(enum.Enum):
    first = 'first year'
    second = 'second year'
    third = 'third year'
    fourth = 'fourth year'

    @staticmethod
    def to_list():
        return [e.value for e in YearEnum]


class SemesterEnum(enum.Enum):
    first = 'first semester'
    second = 'second semester'
    summer = 'summer year'

    @staticmethod
    def to_list():
        return [e.value for e in SemesterEnum]
