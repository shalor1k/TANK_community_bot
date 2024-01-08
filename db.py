import psycopg2.extras

conn = psycopg2.connect(dbname='tank_community', user='shalor1k',
                        password='AiRa6779', host='localhost')

cur = conn.cursor()


async def check_user(user_id: int, username: str) -> bool:
    cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
    personal_id = cur.fetchone()

    if personal_id is not None:
        return True

    else:
        cur.execute("SELECT MAX(id) FROM users")
        max_personal_id = cur.fetchone()
        if max_personal_id[0] is None:
            max_personal_id = 0
        else:
            max_personal_id = max_personal_id[0] + 1

        await add_user(max_personal_id, user_id, username)

        return False


async def add_user(personal_id: int, user_id: int, username: str) -> None:
    try:
        cur.execute(f"INSERT INTO users (id, tg_id, username) VALUES ({personal_id}, {user_id}, '{username}')")
        conn.commit()

        cur.execute(f"INSERT INTO users_forms (id, themes, matches) VALUES ({personal_id},"
                    f" ARRAY[{['Путешествия', 'Еда', 'Работа и карьера', 'Досуг в Москве', 'Спорт и увлечения']}], "
                    f"ARRAY[{999999}])")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в add_user {e}")


async def update_column_in_users_forms(value: str, column: str, user_id: int) -> bool:
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
        personal_id = cur.fetchone()[0]
        cur.execute(f"UPDATE users_forms SET {column} = '{value}' WHERE id = {personal_id}")
        conn.commit()

        return True

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в update_column_in_users_forms {e}")
        return False


async def select_themes(user_id: int) -> list:
    cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
    personal_id = cur.fetchone()[0]
    cur.execute(f"SELECT themes FROM users_forms WHERE id = {personal_id}")
    themes_list = cur.fetchone()

    return themes_list[0]


async def select_user_from_users_forms_with_match(user_id):
    cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
    personal_id = cur.fetchone()[0]

    cur.execute(f"SELECT MIN(id) FROM users_forms WHERE match_flag = 'false' AND id != {personal_id}")
    user_id = cur.fetchone()[0]

    if user_id is not None:
        cur.execute(f"SELECT fullname FROM users_forms WHERE id = {user_id}")
        fullname = cur.fetchone()[0]

        if fullname is not None:
            cur.execute(f"SELECT matches FROM users_forms WHERE id = {personal_id}")
            matches = cur.fetchone()[0]
            if user_id not in matches:
                return user_id, fullname
            return 0, 0

        return 0, 0

    return 0, 0


async def update_themes(user_id: int, themes: list) -> None:
    cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
    personal_id = cur.fetchone()[0]

    cur.execute(f"UPDATE users_forms SET themes = ARRAY[{themes}] WHERE id = {personal_id}")
    conn.commit()


async def select_fullname(user_id: int) -> str:
    cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
    personal_id = cur.fetchone()[0]

    cur.execute(f"SELECT fullname FROM users_forms WHERE id = {personal_id}")
    name = cur.fetchone()[0]

    return name


async def select_tg_id(user_id: int) -> int:
    cur.execute(f"SELECT tg_id FROM users WHERE id = {user_id}")
    tg_id = cur.fetchone()

    return tg_id[0]


async def check_car(user_id: int) -> int:
    cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
    personal_id = cur.fetchone()[0]

    cur.execute(f"SELECT car FROM users_forms WHERE id = {personal_id}")
    car = cur.fetchone()[0]

    if car is not None:
        return 1
    return 0


async def update_match_flag(user_id: int, match_flag: bool) -> None:
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
        personal_id = cur.fetchone()[0]

        cur.execute(f"UPDATE users_forms SET match_flag = '{match_flag}' WHERE id = {personal_id}")
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в update_match_flag {e}")


async def append_to_matches(user_id: int, interlocutor_id: int) -> None:
    try:
        cur.execute(f"SELECT id FROM users WHERE tg_id = {user_id}")
        personal_id = cur.fetchone()[0]

        cur.execute(f"SELECT id FROM users WHERE tg_id = {interlocutor_id}")
        interlocutor_personal_id = cur.fetchone()[0]

        cur.execute(f"UPDATE users_forms SET matches = array_append(matches, {interlocutor_personal_id})"
                    f" WHERE id = {personal_id}")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Ошибка в append_to_matches {e}")
