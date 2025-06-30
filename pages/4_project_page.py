import sqlite3

import streamlit as st
import streamlit_authenticator as sauth

from userinfo import profile_info

DB_PATH = r"C:\Users\onekil1\Coding\project_lib\database\project_lib_db.db"

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

def _decline_project(id_project):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("SELECT unit, role FROM accounts WHERE username = ?", (st.session_state["username"],))
    user_info = [row for row in cursor.fetchall()]
    unit = user_info[0][0]
    decline = "Отправлен на корректировку"
    cursor.execute("UPDATE project SET list_stat = ?, accept_name = ?, accept_unit = ? WHERE id = ?",
                   (decline, st.session_state["username"], unit, id_project))
    db.commit()
    db.close()
    return "Проект направлен на корректировку!"

def _accept_project(id_project):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("SELECT unit, role FROM accounts WHERE username = ?", (st.session_state["username"],))
    user_info = [row for row in cursor.fetchall()]
    unit = user_info[0][0]
    accept = "Согласован"
    cursor.execute("UPDATE project SET list_stat = ?, accept_name = ?, accept_unit = ? WHERE id = ?", (accept,st.session_state["username"],unit, id_project))
    db.commit()
    db.close()
    return "Проект согласован!"

def project_info():
    select_id = st.query_params
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM project WHERE id = ?", (select_id,))
    info_about = cursor.fetchall()
    if not info_about:
        st.write("Список согласования пуст!")
    else:
        st.title(f"Информация о проекте № {select_id}")
        st.write (info_about)
        st.download_button(
            label="Скачать паспорт проекта",
            data=info_about[0][9],
            file_name=f"passport_{select_id}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        if info_about[0][11] == "Проверка":
            if st.button("Согласовать проект"):
                result = _accept_project(select_id)
                st.sidebar.success(result)
            if st.button("Отправить на корректировку"):
                result = _decline_project(select_id)
                st.sidebar.success(result)

def interface():
    st.set_page_config("Страница проекта", layout="wide")
    st.sidebar.title("АСУ ПС")
    credentials = _load_credentials()
    authenticator = sauth.Authenticate(
        credentials,
        cookie_name="asu_ps_cookie",
        cookie_key="super_duper",
        cookie_expiry_days=1
    )
    authenticator.login(location="sidebar", key="login_form", fields={
        'Form name': 'Форма ввода учетных данных',
        'Username': 'Имя учетной записи',
        'Password': 'Пароль',
        'Login': 'Войти'})

    if st.session_state["authentication_status"]:
        project_info()
        profile_info()
        authenticator.logout(button_name="Выйти", location="sidebar")

interface()