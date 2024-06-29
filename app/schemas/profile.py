from pydantic import BaseModel


class ProfileBase(BaseModel):
    full_name: str = None
    department: str = None
    contact_info: str = None
    preferred_sports: str = None
    preferred_time: str = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

    class Config:
        from_attributes = True
