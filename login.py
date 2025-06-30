import streamlit as st
import streamlit_authenticator as sauth
from userinfo import profile_info
import sqlite3
import bcrypt

DB_PATH = r"C:\Users\onekil1\Coding\project_lib\database\project_lib_db.db"

# -- Загрузка пользователей + кеширование
@st.cache_data
def _load_credentials():
    with sqlite3.connect(DB_PATH) as db:
        cur = db.cursor()
        cur.execute("SELECT username, fullname, password FROM accounts")
        rows = cur.fetchall()
    creds = {"usernames": {}}
    for username, fullname, password in rows:
        if isinstance(password, bytes):
            password = password.decode("utf-8")
        creds["usernames"][username] = {
            "name": fullname,
            "password": password
        }
    db.close()
    return creds

# -- Форма регистрации
def registration_block():
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.cursor()
        cursor.execute("SELECT units_name FROM units")
        units = [r[0] for r in cursor.fetchall()]
        cursor.execute("SELECT role_name FROM role")
        roles = [r[0] for r in cursor.fetchall()]

    with st.sidebar.form("registration", clear_on_submit=True):
        st.subheader("Регистрация")
        fullname = st.text_input("ФИО", placeholder="Иванов Иван Иванович")
        username = st.text_input("Имя учетной записи", placeholder="cmbp_ivanov")
        password = st.text_input("Пароль", type="password")
        password_check = st.text_input("Повтор пароля", type="password")
        unit = st.selectbox("Подразделение", options=units, placeholder="ЦКИ")
        role = st.selectbox("Роль", options=roles, placeholder="Просмотр")
        submit = st.form_submit_button("Зарегистрироваться")
        if submit:
            success, msg = _register_user(fullname, username, password, password_check, unit, role)
            if success:
                st.success(msg)
            else:
                st.error(msg)

# -- Функция регистрации
def _register_user(fullname, username, password, password_check, unit, role):
    if password != password_check:
        return False, "❗Пароли не совпадают"
    if len(password) < 8:
        return False, "❗Пароль должен быть не менее 8 символов"
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
    try:
        with sqlite3.connect(DB_PATH) as db:
            cur = db.cursor()
            cur.execute("""
                INSERT INTO accounts (username, fullname, password, unit, role)
                VALUES (?, ?, ?, ?, ?)
            """, (username, fullname, hashed_pw, unit, role))
            db.commit()
        return True, "✅ Регистрация прошла успешно!"
    except sqlite3.IntegrityError:
        return False, "❗Пользователь с такой учетной записью уже существует!"
    finally:
        db.close()

# -- Интерфейс
def interface():
    st.set_page_config("Авторизация", layout="wide")
    st.sidebar.title("АСУ ПС")
    if "pole" not in st.session_state:
        st.session_state.pole = "login"
    credentials = _load_credentials()
    authenticator = sauth.Authenticate(
        credentials,
        cookie_name="asu_ps_cookie",
        cookie_key="super_duper",
        cookie_expiry_days=1
    )

    col1, col2, = st.sidebar.columns(2)
    if st.session_state["authentication_status"] is None:
        with col1:
            if st.button("Войти в систему"):
                st.session_state.pole = "login"
        with col2:
            if st.button("Регистрация"):
                st.session_state.pole = "reg"

    if st.session_state.pole == "login":
        authenticator.login(location="sidebar", key="login_form", fields={
                'Form name': 'Форма ввода учетных данных',
                'Username': 'Имя учетной записи',
                'Password': 'Пароль',
                'Login': 'Войти'
            }
        )
        if st.session_state["authentication_status"]:
            st.sidebar.info("Вы успешно зашли в систему")
            profile_info()
            authenticator.logout(button_name="Выйти", location="sidebar")
        elif st.session_state["authentication_status"] is False:
            st.sidebar.error("Неверное имя пользователя или пароль")
        elif st.session_state["authentication_status"] is None:
            st.sidebar.info("Введите учетные данные или зарегистрируйтесь")
    elif st.session_state.pole == "reg":
        registration_block()

interface()