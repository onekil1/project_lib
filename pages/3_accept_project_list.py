import sqlite3

import streamlit as st
import pandas as pd
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

def accept_list():
    db = sqlite3.connect(r"C:\Users\onekil1\Coding\project_lib\database\project_lib_db.db")
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(project)")
    columns = [column[1] for column in cursor.fetchall()]
    cursor.execute(
        "SELECT id, status, project_name, project_simple_desk, list_stat FROM project WHERE list_stat = ?",
        ("Проверка",))
    rows = cursor.fetchall()
    st.write("### Список проектов для проверки")
    if rows == []:
        st.info("Проекты совершенствования со статусом <На проверке> отсутствуют")
    else:
        projects = [dict(zip(columns, row)) for row in rows]
        db.close()
        df = pd.DataFrame(projects)
        columns = list(df.columns)
        columns[1], columns[2], columns[3] = columns[2], columns[3], columns[1]
        df = df[columns]
        for i, row in df.iterrows():
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(
                    f"**{row[columns[0]]}** — {row[columns[1]]}<br><span style='color:gray'>{row[columns[2]]}</span>",
                    unsafe_allow_html=True
                )
            with col2:
                if st.button(f"Подробнее", key=f"btn_{row['id']}"):
                    st.query_params = row['id']
                    st.switch_page("pages/4_project_page.py")

def interface():
    st.set_page_config(page_title="Согласование проектов", layout="wide")
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

    if "info_project" not in st.session_state:
        st.session_state.info_project = None

    if st.session_state["authentication_status"]:
        profile_info()
        accept_list()
        authenticator.logout(button_name="Выйти", location="sidebar")

interface()