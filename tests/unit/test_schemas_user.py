import pytest
from src.schemas.users import UserBase, UserCreate


class TestUsernameValidation:
    def test_valid_username(self):
        user = UserBase(username="Alex")
        assert user.username == "Alex"

    def test_username_stripped(self):
        user = UserBase(username="  Alex  ")
        assert user.username == "Alex"

    def test_username_too_short(self):
        with pytest.raises(Exception):
            UserBase(username="A")

    def test_empty_username(self):
        with pytest.raises(Exception):
            UserBase(username="   ")


class TestEmailValidation:
    def test_valid_gmail(self):
        user = UserBase(username="Alex", email="alex@gmail.com")
        assert user.email == "alex@gmail.com"

    def test_valid_yandex(self):
        user = UserBase(username="Alex", email="alex@yandex.ru")
        assert user.email == "alex@yandex.ru"

    def test_invalid_domain(self):
        with pytest.raises(Exception):
            UserBase(username="Alex", email="alex@hotmail.com")

    def test_none_email_is_ok(self):
        user = UserBase(username="Alex", email=None)
        assert user.email is None


class TestAgeValidation:
    def test_valid_age(self):
        user = UserBase(username="Alex", age=25)
        assert user.age == 25

    def test_age_zero(self):
        with pytest.raises(Exception):
            UserBase(username="Alex", age=0)

    def test_negative_age(self):
        with pytest.raises(Exception):
            UserBase(username="Alex", age=-5)

    def test_age_over_100(self):
        with pytest.raises(Exception):
            UserBase(username="Alex", age=150)

    def test_age_none(self):
        user = UserBase(username="Alex", age=None)
        assert user.age is None