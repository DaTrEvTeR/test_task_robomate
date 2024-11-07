from enum import Enum


class CustomEnum(Enum):
    """A custom Enum class that can be a parent of any Enum class and return
    the member name in uppercase format with spaces instead of underscores"""

    def __str__(self):
        return self.name.capitalize().replace("_", " ")


class ScheduleType(CustomEnum):
    ANY = 0
    FULLTIME = 1
    PARTIAL = 2
    REMOTE = 3
    INTERNSHIP = 4
    PROJECT = 5
    SEASONAL = 6


class PeriodType(CustomEnum):
    TODAY = 1
    THREE_DAYS = 2
    WEEK = 3
    MONTH = 4
    THREE_MONTH = 7
    YEAR = 5
    ALL = 6


class ExperienceType(CustomEnum):
    ANY = 6
    NO_EXPERIENCE = 0
    UP_TO_1_YEAR = 1
    FROM_1_TO_2 = 2
    FROM_2_TO_5 = 3
    FROM_5_TO_10 = 4
    MORE_THAN_10 = 5


class LangNameType(CustomEnum):
    ENGLISH = 1
    GERMAN = 2
    FRENCH = 3
    SPANISH = 4
    ITALIAN = 5
    AZERBAIJANI = 101
    ALBANIAN = 102
    ARABIC = 103
    ARMENIAN = 104
    AFRIKANER = 105
    BASHKIR = 106
    BELARUSIAN = 107
    BULGARIAN = 108
    HUNGARIAN = 109
    VIETNAMESE = 110
    DUTCH = 111
    GREEK = 112
    GEORGIAN = 113
    DANISH = 114
    HEBREW = 115
    INDONESIAN = 116
    KAZAKH = 117
    KIRGHIZ = 118
    CHINESE = 119
    KOMI = 120
    KOREAN = 121
    KURD = 122
    LETTISH = 123
    LITHUANIAN = 124
    MACEDONIAN = 125
    MOLDAVIAN = 126
    MONGOLIAN = 127
    NORWEGIAN = 128
    PERSIAN = 129
    POLISH = 130
    PORTUGUESE = 131
    ROMANIAN = 132
    RUSSIAN = 133
    SANSKRIT = 134
    SERBIAN = 135
    SLOVAK = 136
    SLOVENIAN = 137
    SWAHILI = 138
    TAJIK = 139
    THAI = 140
    TATAR = 141
    TELUGU = 156
    TURKISH = 142
    TURKMEN = 143
    UZBEK = 144
    UKRAINIAN = 145
    URDU = 146
    FINNISH = 147
    HINDI = 148
    CROATIAN = 149
    CHECHEN = 150
    CZECH = 151
    CHUVASH = 152
    SWEDISH = 153
    ESTONIAN = 154
    JAPANESE = 155


class LangLevelType(CustomEnum):
    ELEMENTARY = 1
    LOWER_INTERMEDIATE = 2
    INTERMEDIATE = 3
    UPPER_INTERMEDIATE = 6
    ADVANCED = 4
    FLUENT = 5
    NATIVE = 7


class CityType(CustomEnum):
    ALL_UKRAINE = 0
    KYIV = 1
    LVIV = 2
    ODESA = 3
    DNIPRO = 4
    VINNYTSIA = 5
    ZAPORIZHIA = 9
    IVANO_FRANKIVSK = 10
    KROPYVNYTSKYI = 11
    LUTSK = 14
    MYKOLAIV = 15
    POLTAVA = 17
    RIVNE = 18
    SUMY = 19
    TERNOPIL = 20
    KHARKIV = 21
    KHERSON = 22
    KHMELNYTSKYI = 23
    CHERKASY = 24
    CHERNIHIV = 25
    CHERNIVTSI = 26
    UZHHOROD = 28
    OTHER = 34


class EducationType(CustomEnum):
    ANY = 0
    HIGHER = 1
    INCOMPLETE_HIGHER = 2
    VOCATIONAL = 3
    SECONDARY = 4
    MBA = 5


# WorkUa enums
WorkUaSalary = {
    0: 0,
    1: 1,
    10000: 2,
    15000: 3,
    20000: 4,
    30000: 5,
    40000: 6,
    50000: 7,
    100000: 8,
}
