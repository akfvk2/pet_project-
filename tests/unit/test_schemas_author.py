import pytest
from src.schemas.authors import AuthorCreate, AuthorUpdate, AuthorBase

class TestNameValidator:
    def test_valid_name(self):
        author = AuthorBase(name="test")
        assert author.name == "test"

    def test_name_strippending(self):
        author = AuthorBase(name="  test  ")
        assert author.name.strip() == "test"

    def test_name_too_short(self):
        with pytest.raises(Exception):
            AuthorBase(name="t")

    def test_empty_name(self):
        with pytest.raises(Exception):
            AuthorBase(name=" ")


class TestBiographyValidator:
    def test_valid_biography(self):
        author = AuthorBase(name='test', biography="test")
        assert author.biography == "test"

    def test_biography_strippending(self):
        author = AuthorBase(name='test',biography="  test  ")
        assert author.biography.strip() == "test"

    def test_biography_too_short(self):
        with pytest.raises(Exception):
            AuthorBase(name='test',biography="t")

class TestNationalityValidator:
    def test_valid_nationality(self):
        author = AuthorBase(name='test',nationality="test")
        assert author.nationality == "test"

    def test_nationality_strippending(self):
        author = AuthorBase(name='test',nationality="  test  ")
        assert author.nationality.strip() == "test"

    def test_nationality_too_short(self):
        with pytest.raises(Exception):
            AuthorBase(name='test',nationality="t")