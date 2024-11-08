from app.helpers.enums import LangLevelType, LangNameType, ExperienceType

work_salary_dict = {
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
work_exp_dict = {
    ExperienceType.ANY.value: 2,
    ExperienceType.NO_EXPERIENCE.value: 0,
    ExperienceType.UP_TO_1_YEAR.value: 1,
    ExperienceType.FROM_1_TO_2.value: 164,
    ExperienceType.FROM_2_TO_5.value: 165,
    ExperienceType.FROM_5_TO_10.value: 166,
    ExperienceType.MORE_THAN_10.value: 166,
}

work_lang_level_dict = {
    LangLevelType.ELEMENTARY.value: 83,
    LangLevelType.LOWER_INTERMEDIATE.value: 83,
    LangLevelType.INTERMEDIATE.value: 84,
    LangLevelType.UPPER_INTERMEDIATE.value: 22835,
    LangLevelType.ADVANCED.value: 85,
    LangLevelType.FLUENT.value: 22836,
    LangLevelType.NATIVE.value: 22836,
}

work_lang_dict = {
    LangNameType.ENGLISH.value: 1,
    LangNameType.GERMAN.value: 2,
    LangNameType.SPANISH.value: 4,
    LangNameType.FRENCH.value: 5,
    LangNameType.ITALIAN.value: 18,
    LangNameType.RUSSIAN.value: 32,
    LangNameType.UKRAINIAN.value: 41,
}
