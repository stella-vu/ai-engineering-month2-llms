from pydantic import BaseModel, Field

class CandidateContact(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""


class MatchResumetoJob(BaseModel):
    match_score: int = Field(0, ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class SkillGapAction(BaseModel):
    skill: str = ""
    status: str = ""
    reason: str = ""
    suggested_resume_bullet: str = ""
    learning_action: str = ""

class SkillGapActionPlan(BaseModel):
    contact: CandidateContact = Field(default_factory=CandidateContact)
    target_role: str = ""
    missing_skills: list[str] = Field(default_factory=list)
    actions: list[SkillGapAction] = Field(default_factory=list)



