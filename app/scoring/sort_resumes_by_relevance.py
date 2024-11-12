from typing import List, Tuple

from app.scoring.scoring import ResumeEvaluator
from app.services.resume_filter import ResumeFilter
from app.services.resume_python_object import ResumeModel


def sort_resumes_by_relevance(
    resumes: List[ResumeModel], resume_filter: ResumeFilter
) -> List[Tuple[ResumeModel, int]]:
    """
    Sorts a list of resumes by their relevance scores based on the specified filter criteria.

    This function evaluates each resume's relevance score using the provided `resume_filter` criteria and
    sorts the resumes from highest to lowest score. It returns a list of tuples, each containing a resume and
    its calculated relevance score.

    Parameters:
    ----------
    resumes : List[ResumeModel]
        A list of `ResumeModel` instances representing the resumes to be evaluated and sorted.

    resume_filter : ResumeFilter
        A `ResumeFilter` instance containing the criteria for evaluating resume relevance.

    Returns:
    -------
    List[Tuple[ResumeModel, int]]
        A list of tuples where each tuple contains a `ResumeModel` instance and its relevance score,
        sorted in descending order by the score. Resumes with higher relevance appear first in the list"""
    scored_resumes = [
        (resume, ResumeEvaluator(resume, resume_filter).evaluate())
        for resume in resumes
    ]

    scored_resumes.sort(key=lambda x: x[1], reverse=True)

    return scored_resumes
