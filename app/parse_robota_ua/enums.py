from app.services.enums import LangLevelType


scoring_lang_level_dict = {
    LangLevelType.ELEMENTARY.value: 1,
    LangLevelType.PRE_INTERMEDIATE.value: 2,
    LangLevelType.INTERMEDIATE.value: 3,
    LangLevelType.UPPER_INTERMEDIATE.value: 6,
    LangLevelType.ADVANCED.value: 4,
    LangLevelType.FLUENT.value: 5,
    LangLevelType.NATIVE.value: 7,
}
