from database import User


class Friendship:
    @staticmethod
    def is_friend_for(client_user: User, user: User) -> bool:
        return client_user.friends.get(user.id) is not None
