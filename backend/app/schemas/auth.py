from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserResponse
