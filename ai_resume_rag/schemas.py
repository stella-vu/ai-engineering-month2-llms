from pydantic import BaseModel, Field, model_validator


class JobMatchResult(BaseModel):
    match_score: int = Field(
        ge=0,
        le=100,
        description="Resume match score from 0 to 100.",
    )
    matched_skills: list[str]
    missing_or_weak_skills: list[str]
    resume_improvement_suggestions: list[str]
    do_not_add_unless_true: list[str]

    @model_validator(mode="after")
    def validate_score_matches_skills(self):
        if self.match_score == 0 and self.matched_skills:
            raise ValueError(
                "match_score cannot be 0 when matched_skills is not empty."
            )
        return self