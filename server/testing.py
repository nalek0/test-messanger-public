import os
import pytest
from flask_login import current_user
from werkzeug.test import TestResponse

from app import create_app
from database import db


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_main(client):
    admin_signup_data = {
        "first_name": "Aleksandr",
        "last_name": "Belash",
        "username": "admin",
        "password": "1234",
    }
    user_signup_data = {
        "first_name": "User",
        "last_name": "Userovich",
        "username": "user",
        "password": "user-password",
    }

    with client:
        def signup_user(data: dict) -> TestResponse:
            return client.post("/auth/signup", data=data)

        def login_user(data: dict) -> TestResponse:
            return client.post("/auth/login", data=data)

        def logout() -> None:
            client.get("/auth/logout")

        index_get: TestResponse = client.get("/")
        assert index_get.status_code in range(200, 300)

        admin = signup_user(admin_signup_data)
        assert admin.status_code in range(300, 400)
        admin_id = current_user.id
        logout()

        user: TestResponse = signup_user(user_signup_data)
        assert user.status_code in range(300, 400)
        user_id = current_user.id
        logout()

        user_l = login_user(user_signup_data)
        assert user_l.status_code in range(300, 400)
        add_friend_user = client.post("/api/user/add_friend", json={
            "user_id": admin_id
        })
        assert add_friend_user.status_code in range(200, 300)
        assert 1 == len(current_user.friends)
        logout()

        admin_l = login_user(admin_signup_data)
        assert admin_l.status_code in range(300, 400)
        add_friend_admin = client.post("/api/user/add_friend", json={
            "user_id": user_id
        })
        assert add_friend_admin.status_code in range(200, 300)
        assert 1 == len(current_user.friends)
        logout()
