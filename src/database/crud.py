from database.models import Users
from database.database import Session


def create_user(name: str, tg_id: int):
    with Session() as session:
        user = session.query(Users).filter(
            Users.user_tg_id == tg_id).one_or_none()
        if user is None:
            new_user = Users(user_tg_id=tg_id, user_name=name)
            session.add(new_user)
            session.commit()
            print("User created!")

        else:
            print(f"User with {tg_id=} already exist!")
