import pytest
from uuid import uuid4
from src.services.room_service import RoomService
from src.schemas.rooms import RoomCreate
from src.exceptions.not_found import NotFoundException
from src.repositories.room import RoomRepository


@pytest.fixture
def room_repo(db_session):
    return RoomRepository(db_session)

@pytest.fixture
def service(db_session):
    return RoomService(RoomRepository(db_session))


class TestCreateRoom:
    async def test_create_success(self, service):
        result = await service.create(RoomCreate(roomname="Переговорка 1"))
        assert result.roomname == "Переговорка 1"
        assert result.id is not None


class TestGetRoom:
    async def test_get_by_id_success(self, service):
        created = await service.create(RoomCreate(roomname="Переговорка 2"))
        result = await service.get_by_id(created.id)
        assert result.id == created.id
        assert result.roomname == "Переговорка 2"

    async def test_get_by_id_not_found(self, service):
        with pytest.raises(NotFoundException):
            await service.get_by_id(uuid4())


class TestDeleteRoom:
    async def test_delete_success(self, service, db_session, room_repo):
        created = await service.create(RoomCreate(roomname="Переговорка 3"))
        result = await service.delete(created.id)
        assert result is True
        room = await room_repo.get_by_id(created.id)
        assert room.is_deleted is True

    async def test_delete_not_found(self, service):
        with pytest.raises(NotFoundException):
            await service.delete(uuid4())