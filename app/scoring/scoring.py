from app.services.resume_python_object import ResumeModel
from app.services.resume_filter import ResumeFilter
from app.services.enums import EducationType


class ResumeEvaluator:
    """A class to evaluate the relevance of a resume based on specified criteria.
    The evaluation score is calculated using main skills, education level, language proficiency,
    keywords presence, and work experience.

    Attributes:
        resume (ResumeModel): The resume being evaluated.
        resume_filter (ResumeFilter): The filter criteria used to evaluate the resume.
        score (int): The total score assigned to the resume based on relevance."""

    def __init__(self, resume: ResumeModel, resume_filter: ResumeFilter):
        self.resume = resume
        self.resume_filter = resume_filter
        self.score = 0

    def evaluate(self) -> int:
        """Calculates the total score for the resume by evaluating it across different criteria.

        Returns:
            int: The total relevance score"""
        self._evaluate_main_skills()
        self._evaluate_education()
        self._evaluate_languages()
        self._evaluate_keywords()
        self._evaluate_experience()
        return self.score

    def _evaluate_main_skills(self):
        """Evaluates the resume's main skills by checking for matches with the filter's main skills.
        Adds points if skills are found in either the resume's skills section or in work experience descriptions.

        Scoring:
            +4 points for each skill found in skills.
            +6 points for each skill found in work experience"""
        exp_descs = "; ".join(ex.description.lower() for ex in self.resume.experiences)
        for skill in self.resume_filter.main_skills:
            skill_lower = skill.lower()
            if skill_lower in self.resume.skills.lower():
                self.score += 4
            if skill_lower in exp_descs:
                self.score += 6

    def _evaluate_education(self):
        """Evaluates the resume's education level relative to the filter's criteria.

        Scoring:
            +10 points for a higher education level.
            +5 points for a vocational education level"""
        if self.resume.education == EducationType.HIGHER.value:
            self.score += 10
        elif self.resume.education == EducationType.VOCATIONAL.value:
            self.score += 5

    def _evaluate_languages(self):
        """Evaluates the resume based on language proficiency requirements.
        Adds points for each language if the candidate's proficiency is above the required level.

        Scoring:
            +1 point for each level above the required level, up to a maximum of 5 points per language.
            Capped at 10 points for the total language score"""
        language_score = 0
        for lang_id, required_level in self.resume_filter.languages.items():
            required_level = required_level[0]
            actual_level = self.resume.languages.get(lang_id)
            if actual_level and actual_level >= required_level:
                language_score += min(actual_level - required_level, 5)
        self.score += min(language_score, 10)

    def _evaluate_keywords(self):
        """Evaluates the resume based on keywords specified in the filter.
        Searches for these keywords in the resume text.

        Scoring:
            +2 points per keyword match, capped at 15 points total"""
        if self.resume_filter.keywords:
            exp_descs = "; ".join(
                ex.description.lower() for ex in self.resume.experiences
            )
            keyword_matches = sum(
                1
                for keyword in self.resume_filter.keywords
                if keyword in exp_descs or keyword in self.resume.skills
            )
            self.score += min(keyword_matches * 2, 15)

    def _evaluate_experience(self):
        """Evaluates the resume based on the total work experience period.

        Scoring:
            +2 points for each half-year of experience, capped at a maximum of 35 points"""
        total_experience_years = sum(ex.period for ex in self.resume.experiences)
        experience_score = total_experience_years // 0.5
        self.score += min(experience_score * 2, 35)
