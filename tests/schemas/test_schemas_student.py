import pytest
from src.schemas.students import StudentBase, StudentCreate
from src.exceptions.validation_error import ValidationException

class TestNameValidator:
    def test_valid_name(self):
        student = StudentBase(name="test")
        assert student.name == "test"

    def test_name_strippending(self):
        student = StudentBase(name=" test ")
        assert student.name == "test"

    def test_name_too_short(self):
        with pytest.raises(ValidationException):
            StudentBase(name="t")

    def test_name_empty(self):
        with pytest.raises(ValidationException):
            StudentBase(name="")


class TestPhoneValidator:
    def test_valid_phone(self):
        student = StudentBase(name="Тест",phone="+79094188968")
        assert student.phone == "+79094188968"

    def test_phone_too_short(self):
        with pytest.raises(ValidationException):
            StudentBase(name="Тест",phone="+790896")

class TestAgeValidator:
    def test_valid_age(self):
        student = StudentBase(name="Тест",age=10)
        assert student.age == 10

    def test_age_too_short(self):
        with pytest.raises(ValidationException):
            StudentBase(name="Тест",age="0")

    def test_age_long(self):
        with pytest.raises(ValidationException):
            StudentBase(name="Тест",age=9999)