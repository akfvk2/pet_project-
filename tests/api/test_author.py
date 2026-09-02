from uuid import uuid4

class TestCreateAuthor:
    async def test_success(self, client):
        response = await client.post("/v1/authors/", json={
    "name": "Толстой",
    "biography": "Русский писатель",
    "birth_date": "1828-09-09",
    "nationality": "Русский",
    "books": [{"title": "Война и мир", "page_count": 100, "genre": "Роман"}]
}
)
        assert response.status_code == 201
        assert response.json()['name'] == "Толстой"

    async def test_books(self, client):
        response = await client.post("/v1/authors/", json={
            "name": "Толстой",
            "biography": "Русский писатель",
            "birth_date": "1828-09-09",
            "nationality": "Русский",
            "books": []
        })
        assert response.status_code == 422

    async def test_short_username(self, client):
        response = await client.post("/v1/authors/", json={
    "name": "Т",
    "biography": "Русский писатель",
    "books": [{"title": "Война и мир", "page_count": 100, "genre": "Роман"}]
})
        assert response.status_code == 422

class TestGetAuthor:
    async def test_success(self, client):
        created = await client.post("/v1/authors/", json={
    "name": "Толстой",
    "biography": "Русский писатель",
    "birth_date": "1828-09-09",
    "nationality": "Русский",
    "books": [{"title": "Война и мир", "page_count": 100, "genre": "Роман"}]
}
)
        author_id = created.json()['id']
        response = await client.get(f"/v1/authors/{author_id}/")
        assert response.status_code == 200
        assert response.json()['name'] == "Толстой"

    async def test_not_found(self, client):
        response = await client.get(f"/v1/authors/{uuid4()}/")
        assert response.status_code == 404

class TestUpdateAuthor:
    async def test_success(self, client):
        created = await client.post("/v1/authors/", json={
    "name": "Толстой",
    "biography": "Русский писатель",
    "birth_date": "1828-09-09",
    "nationality": "Русский",
    "books": [{"title": "Война и мир", "page_count": 100, "genre": "Роман"}]
}
)
        user_id = created.json()['id']
        response = await client.put(f"/v1/authors/{user_id}/", json={
            "name": "Толстой1",
            "biography": "Русский писатель",
            "birth_date": "1828-09-09",
            "nationality": "Русский",
            "books": [{"title": "Война и мир", "page_count": 100, "genre": "Роман"}]
        })

        assert response.status_code == 200
        assert response.json()['name'] == "Толстой1"

class TestDeleteAuthor:
    async def test_success(self, client):
        created = await client.post("/v1/authors/", json={
    "name": "Толстой",
    "biography": "Русский писатель",
    "birth_date": "1828-09-09",
    "nationality": "Русский",
    "books": [{"title": "Война и мир", "page_count": 100, "genre": "Роман"}]
}

                                    )
        author_id = created.json()['id']
        response = await client.delete(f"/v1/authors/{author_id}/")
        assert response.status_code == 204


