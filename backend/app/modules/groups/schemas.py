from pydantic import BaseModel, Field

class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    is_public: bool = False

class GroupResponse(BaseModel):
    id: int
    name: str
    is_public: bool
    join_code: str

class JoinGroupRequest(BaseModel):
    join_code: str = Field(min_length=4, max_length=20)