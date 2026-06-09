import pytest
from uuid import uuid4


class TestCreateStudents:
    async def test_success(self, client):
        response = await client.post("/v1/students/", json={
    "name": "test",
    "age": 25,
    "email": "test@gmail.com",
    "phone": "+79999999999",
    "course": {"title": "test", "description": "Описание курса", "duration_hours": 10}
})
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['name'] == 'test'

    async def test_invalid_course(self, client):
        response = await client.post("/v1/students/", json={
            "name": "test"}
            )
        assert response.status_code == 422

    async def test_invalid_short_name(self, client):
        response = await client.post("/v1/students/", json={
    "name": "t",
    "age": 25,
    "email": "test@gmail.com",
    "phone": "+79999999999",
    "course": {"title": "test", "description": "Описание курса", "duration_hours": 10}
})
        assert response.status_code == 422

class TestGetStudents:
    async def test_success(self, client):
        created = await client.post("/v1/students/", json={
    "name": "test",
    "age": 25,
    "email": "test@gmail.com",
    "phone": "+79999999999",
    "course": {"title": "test", "description": "Описание курса", "duration_hours": 10}
}
                                    )
        student_id = created.json()['id']
        response = await client.get(f"/v1/students/{student_id}/")
        assert response.status_code == 200
        assert response.json().get('name') == 'test'

    async def test_not_found(self, client):
        response = await client.get(f"/v1/students/{uuid4()}/")
        assert response.status_code == 404

class TestUpdateStudents:
    async def test_success(self, client):
        created = await client.post("/v1/students/", json={
    "name": "test",
    "age": 25,
    "email": "test@gmail.com",
    "phone": "+79999999999",
    "course": {"title": "test", "description": "Описание курса", "duration_hours": 10}
})
        student_id = created.json()['id']
        response = await client.put(f"/v1/students/{student_id}/", json={
            "name": "test1",
            "age": 25,
            "email": "test@gmail.com",
            "phone": "+79999999999",
            'course': {'title': 'test1', 'description': 'Описание курса', 'duration_hours': 10}
        })
        assert response.status_code == 200
        assert response.json().get('name') == 'test1'

class TestDeleteStudents:
    async def test_success(self, client):
        created = await client.post("/v1/students/", json={
    "name": "test",
    "age": 25,
    "email": "test@gmail.com",
    "phone": "+79999999999",
    "course": {"title": "test", "description": "Описание курса", "duration_hours": 10}
})
        student_id = created.json()['id']
        response = await client.delete(f"/v1/students/{student_id}/")
        assert response.status_code == 204