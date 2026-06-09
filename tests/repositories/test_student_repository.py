from src.repositories.student import StudentRepository
from src.models.student import Students
import pytest_asyncio
from uuid import uuid4


@pytest_asyncio.fixture
async def repo(db_session):
    return StudentRepository(db_session)

class TestStudentRepository:
    async def test_create_student(self, repo):
        student = Students(name='test',
                           age=50,
                           email="test@gmail.com",
                           phone='+79999999999')
        created = await repo.create(student)
        assert created.id == student.id
        assert created.name == 'test'

    async def test_get_by_id(self, repo):
        student = Students(name='test',
                           age=50,
                           email="test@gmail.com",
                           phone='+79999999999')
        created = await repo.create(student)
        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.name == 'test'

    async def test_get_by_id_not_found(self, repo):
        found = await repo.get_by_id(uuid4())
        assert found is None

    async def test_update_student(self, repo):
        sudent = Students(name='test',
                           age=50,
                           email="test@gmail.com",
                           phone='+79999999999')
        created = await repo.create(sudent)
        created.name ='updated'
        created.age = 50
        updated = await repo.update(created)
        assert updated.name == 'updated'
        assert updated.age == 50

    async def test_delete_student(self, repo):
        student = Students(name='test',
                           age=50,
                           email="test@gmail.com",
                           phone='+79999999999')
        created = await repo.create(student)
        await repo.delete(created)
        assert created.is_deleted is True
