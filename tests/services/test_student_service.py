import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.services.student_service import StudentService
from src.schemas.students import StudentCreate, StudentUpdate, StudentRead
from src.exceptions.not_found import NotFoundException
from src.models.student import Students
import src.services.student_service as svc_module
from src.models.course import Course



@pytest.fixture
def student_service(mock_redis):
    service = StudentService(session=AsyncMock())
    svc_module.redis_client = mock_redis
    return service


@pytest.fixture
def sample_student():
    student = Students(name='test',
                        age=50,
                        email="test@gmail.com",
                        phone='+79999999999',
    )
    student.id = uuid4()
    student.course = Course(title="Python", description="Курс", duration_hours=40)
    student.course.id = uuid4()
    student.course.students = []
    return student

@pytest.fixture
def updated_student():
    student = Students(name="Обновлённый", age=50, email="test@gmail.com", phone="+79999999999")
    student.id = uuid4()
    student.course = Course(title="Django", description="Курс", duration_hours=40)
    student.course.id = uuid4()
    student.course.students = []
    return student



class TestGetStudentById:
    async def test_cache_miss_fetches_from_db(self, student_service, mock_redis, sample_student):
        student_service.students_repo.get_by_id = AsyncMock(return_value=sample_student)

        result = await student_service.get_student_by_id(sample_student.id)

        assert result.name == "test"
        mock_redis.setex.assert_called_once()

    async def test_cache_hit_skips_db(self, student_service, mock_redis, sample_student):
        student_read = StudentRead.model_validate(sample_student)
        mock_redis.get = AsyncMock(return_value=student_read.model_dump_json())
        student_service.students_repo.get_by_id = AsyncMock()

        await student_service.get_student_by_id(sample_student.id)

        student_service.students_repo.get_by_id.assert_not_called()

    async def test_not_found_raises_exception(self, student_service):
        student_service.students_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await student_service.get_student_by_id(uuid4())


class TestCreateStudent:
    async def test_create_returns_student_read(self, student_service, sample_student):
        student_service.students_repo.create = AsyncMock(return_value=sample_student)
        student_in = StudentCreate(
            name="test",
            course={"title": "test"}  # CourseCreate
        )

        result = await student_service.create_student(student_in)

        assert result.name == "test"


class TestDeleteStudent:
    async def test_delete_clears_cache(self, student_service, mock_redis, sample_student):
        student_service.students_repo.get_by_id = AsyncMock(return_value=sample_student)
        student_service.students_repo.delete = AsyncMock()

        await student_service.delete_student(sample_student.id)

        mock_redis.delete.assert_called_once_with(f"student:{sample_student.id}")

class TestUpdateStudent:
    async def test_update_success(self, student_service, mock_redis, sample_student, updated_student):
        student_service.students_repo.get_by_id = AsyncMock(return_value=sample_student)
        student_service.students_repo.update = AsyncMock(return_value=updated_student)

        student_in = StudentUpdate(
            name="Обновлённый",
            course={"title": "Django"}
        )
        result = await student_service.update_student(sample_student.id, student_in)

        assert result.name == "Обновлённый"
        student_service.students_repo.update.assert_called_once()

    async def test_update_clears_cache(self, student_service, mock_redis, sample_student, updated_student):
        student_service.students_repo.get_by_id = AsyncMock(return_value=sample_student)
        student_service.students_repo.update = AsyncMock(return_value=updated_student)

        await student_service.update_student(
            sample_student.id,
            StudentUpdate(name="Обновлённый", course={"title": "Django"})
        )


        mock_redis.setex.assert_called_once()

    async def test_update_not_found(self, student_service):
        student_service.students_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await student_service.update_student(
                uuid4(),
                StudentUpdate(name="Обновлённый", course={"title": "Django"})
            )