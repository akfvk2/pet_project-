from typing import Annotated
from fastapi import Depends
from src.mappers.room_mapper import RoomMapper
from src.repositories.room import RoomRepository


RoomMapperDep = Annotated[RoomMapper, Depends(RoomMapper)]
RoomRepositoryDep = Annotated[RoomRepository, Depends(RoomRepository)]