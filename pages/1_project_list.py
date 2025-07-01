import sqlite3

import streamlit as st
import pandas as pd
import streamlit_authenticator as sauth

from streamlit_dynamic_filters import DynamicFilters
from userinfo import profile_info,local_css

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
# -- Сопоставление выбранных тегов с существующими тегами проектов в базе знаний
def all_selected_tags(row_tags, selected_tags):
    tags = [tag.strip() for tag in row_tags.split(',') if tag.strip()]
    return all(tag in tags for tag in selected_tags)
# -- Выгрузка всех доступных тегов из БД
def _load_tags_from_db():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("SELECT tag_name FROM tags")
    all_tags = [row[0] for row in cursor.fetchall()]
    db.close()
    return all_tags
# -- Загрузка списка проектов
def project_list():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("SELECT id, status, project_name, project_simple_desk, list_stat, "
                   "tags FROM project WHERE list_stat = ?", ("Согласован",))
    rows = cursor.fetchall()
    db.close()
    col0, col00 = st.columns([9, 4.5])
    with col0:
        st.write("### Список проектов совершенствования")
    if rows == []:
        st.info("Проекты совершенствования отсутствуют в базе данных")
        db.close()
    else:
        projects = [row for row in rows]
        columns = ["id", "status", "project_name", "project_simple_desk", "list_stat", "tags"]
        df = pd.DataFrame(projects, columns=columns)
        all_tags = _load_tags_from_db()
        with col00:
            selected_tags = st.multiselect("Фильтр по тегам", options=all_tags, placeholder="При необходимости, выберите тег")
        if selected_tags:
            filtered_df = df[df['tags'].apply(lambda x: all_selected_tags(x, selected_tags))]
        else:
            filtered_df = df
        if filtered_df.empty:
            st.info("Проекты совершенствования с выбранными тегами отсутствуют")
        else:
            for i, row in filtered_df.iterrows():
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.markdown(
                        f"**{row["id"]}** — {row["project_name"]}<br><span style='color:gray'>{row["project_simple_desk"]}</span>",
                        unsafe_allow_html=True
                    )
                with col2:
                    splt = row["tags"].split(",")
                    for tag in splt:
                        st.markdown(f"- {tag}")
                with col3:
                    if st.button(f"Подробнее", key=f"btn_{row[0]}"):
                        st.query_params = row[0]
                        st.switch_page("pages/4_project_page.py")
# -- Основная логика страницы
def interface():
    st.set_page_config("Список проектов", layout="wide")
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
        profile_info()
        project_list()
        authenticator.logout(button_name="Выйти", location="sidebar")

local_css()
interface()