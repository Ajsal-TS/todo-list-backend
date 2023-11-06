from pydantic import BaseModel


class User(BaseModel):
    """Schema of the user"""

    name: str
    password: str


class RevokedToken(BaseModel):
    token: str
