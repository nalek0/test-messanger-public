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

    os.remove("database.db")
    db.create_all(app=app)


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

        index_get: TestResponse = client.get("main.index")
        assert(200 == index_get.status_code, index_get.response)

        admin = signup_user(admin_signup_data)
        assert(200 == admin.status_code, admin.response)
        admin_id = current_user.id
        logout()

        user: TestResponse = signup_user(user_signup_data)
        assert(200 == user.status_code, user.response)
        user_id = current_user.id
        logout()

        user_l = login_user(user_signup_data)
        assert(200 == user_l.status_code, user_l.response)
        add_friend_user = client.post("/api/user/add-friend", json={
            "user_id": admin_id
        })
        assert(200 == add_friend_user.status_code, add_friend_user.response)
        assert(1 == current_user.friends.count(), f"Number of friends: {current_user.friends.count()}")
        logout()

        admin_l = login_user(admin_signup_data)
        assert(200 == admin_l.status_code, admin_l.response)
        add_friend_admin = client.post("/api/user/add_friend", json={
            "user_id": user_id
        })
        assert(200 == add_friend_admin.status_code, add_friend_admin.response)
        assert(1 == current_user.friends.count(), f"Number of friends: {current_user.friends.count()}")
        logout()
