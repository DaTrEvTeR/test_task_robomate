from app.services.resume_python_object import ResumeModel
from app.services.resume_filter import ResumeFilter
from app.services.enums import EducationType


class ResumeEvaluator:
    def __init__(self, resume: ResumeModel, resume_filter: ResumeFilter):
        self.resume = resume
        self.resume_filter = resume_filter
        self.score = 0

    def _evaluate_main_skills(self):
        exp_descs = "; ".join(
            [ex.description.lower() for ex in self.resume.experiences]
        )
        for skill in self.resume_filter.main_skills:
            skill_lower = skill.lower()
            if skill_lower in self.resume.skills.lower():
                self.score += 4
            if skill_lower in exp_descs:
                self.score += 6

    def _evaluate_education(self):
        if self.resume.education == EducationType.HIGHER.value:
            self.score += 10
        elif self.resume.education == EducationType.VOCATIONAL.value:
            self.score += 5

    def _evaluate_languages(self):
        language_score = 0
        for lang_id, required_level in self.resume_filter.languages.items():
            actual_level = self.resume.languages.get(lang_id)
            if actual_level and actual_level >= required_level:
                language_score += min(actual_level - required_level, 5)
        self.score += min(language_score, 10)

    def _evaluate_keywords(self):
        exp_descs = "; ".join(ex.description.lower() for ex in self.resume.experiences)
        keyword_matches = sum(1 for skill in self.resume.skills if skill in exp_descs)
        self.score += min(keyword_matches * 2, 15)

    def _evaluate_experience(self):
        total_experience_years = sum(ex.period for ex in self.resume.experiences)
        experience_score = total_experience_years // 0.5
        self.score += min(experience_score * 2, 35)
