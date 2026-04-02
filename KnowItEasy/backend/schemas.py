from pydantic import BaseModel, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if not re.fullmatch(r"[A-Za-z ]+", value):
            raise ValueError("Username should contain only letters and spaces")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not value.endswith("@gmail.com"):
            raise ValueError("Only Gmail addresses are allowed")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")

        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long")

        if not re.fullmatch(r"[A-Za-z ]+", value):
            raise ValueError("Username should contain only letters and spaces")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not value.endswith("@gmail.com"):
            raise ValueError("Only Gmail addresses are allowed")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")

        return value


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
