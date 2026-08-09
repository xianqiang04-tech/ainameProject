from http.client import HTTPException

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator, ValidationError
from typing import Annotated

RawPasswordStr = Annotated[str,Field(...,min_length=6,max_length=10)]

class RegisterIn(BaseModel):
    email: EmailStr
    username: Annotated[str,Field(...,min_length=2,max_length=10)]
    password: RawPasswordStr
    confirm_password: RawPasswordStr
    code: Annotated[str,Field(...,min_length=4,max_length=4)]

    @model_validator(mode="after")
    def password_validator(self):
        password = self.password
        confirm_password = self.confirm_password
        if password != confirm_password:
            raise HTTPException(400,"Passwords don't match")
        return self

class UserCreateSchema(BaseModel):
    email: EmailStr
    password: RawPasswordStr
    username: Annotated[str,Field(min_length=2,max_length=10)]

class LoginIn(BaseModel):
    email: EmailStr
    password: RawPasswordStr


class UserSchema(BaseModel):
    email: EmailStr
    username: Annotated[str,Field(min_length=2,max_length=10)]
    role: str
    model_config = ConfigDict(from_attributes=True)

class LoginoutSchema(BaseModel):
   user:UserSchema
   access_token:str
   refresh_token:str

