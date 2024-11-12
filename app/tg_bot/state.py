from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    filt = State()

    speciality = State()
    main_skills = State()
    location = State()
    education = State()
    age = State()
    salary = State()
    schedule = State()
    languages = State()
    period = State()
    experience = State()
    photo = State()
    keywords = State()
