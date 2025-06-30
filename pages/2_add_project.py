import sqlite3

import streamlit as st
import streamlit_authenticator as sauth

from userinfo import profile_info

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
# -- Конвертирование docx в бинарный вид
def convert_to_blob(blob_file):
    blob_data = blob_file.read()
    return blob_data
# -- Загрузка введенных данных в базу данных
def _load_info(project_name, project_simple_desc, project_status, problem, solution, plan_col_effect, plan_qol_effect, plan_money_effect, passport_file, other_file, list_stat):
    db = sqlite3.connect(r"C:\Users\onekil1\Coding\project_lib\database\project_lib_db.db")
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO project (status, project_name, project_simple_desk, problem, solution, plan_col_effect, plan_qol_effect, plan_money, passport, other_file, list_stat) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (project_status, project_name, project_simple_desc, problem, solution, plan_col_effect, plan_qol_effect, plan_money_effect, passport_file, other_file, list_stat))
        db.commit()
        return True, "Проект совершенствования создан и направлен на согласование куратору подразделения!"
    except sqlite3.IntegrityError:
        db.rollback()
        return "Ошибка базы данных sqllite3"
    finally:
        db.close()
# -- Интерфейс с полями для внесения информации
def add_project():
    db = sqlite3.connect(r"C:\Users\onekil1\Coding\project_lib\database\project_lib_db.db")
    cursor = db.cursor()
    cursor.execute("SELECT status FROM status")
    status_list = [row[0] for row in cursor.fetchall()]
    db.close()
    with st.form("project_info", clear_on_submit=True):
        st.title("Форма для добавления проекта в базу знаний")
        st.header("Информация о проекте")
        project_name = st.text_input("Введите наименование проекта", placeholder="Цифровизация документооборота")
        project_simple_desc = st.text_input("Введите краткое описание проекта совершенствования", placeholder="Пример")
        col1, col2, col3 = st.columns(3)
        with col1:
            project_status = st.selectbox("Выберите статус проекта",
                                 options=status_list,
                                 index=None,
                                 placeholder="Выберите из списка",
                                 disabled=not status_list or status_list == ["Нет доступных подразделений"])
        st.header("Решение")
        problem = st.text_area("Описание проблемной ситуации", height=100, max_chars=800)
        sulution = st.text_area("Описание предлагаемого решения", height=100, max_chars=800)
        st.header("Эффективность")
        status_project = "Проверка"
        col4, col5, col6 = st.columns(3)
        with col4:
            plan_col_effect = st.text_area("Введите запланированные(фактические) количественные показатели", height=68, max_chars=50)
        with col5:
            plan_qol_effect = st.text_area("Введите запланированные(фактические) качественные показатели", height=68, max_chars=50)
        with col6:
            plan_money_effect = st.text_area("Введите запланированные(фактические) экономические показатели", height=68, max_chars=50)
        col7, col8  = st.columns(2)
        with col7:
            passport_file = st.file_uploader("Загрузите паспорт проекта", type=["docx"])
        with col8:
            other_file = st.file_uploader("Загрузите дополнительные файлы (необязательно)")
        submit = st.form_submit_button("Внести данные в базу знаний")
        if submit:
            if all([project_name, project_simple_desc, project_status, problem, sulution, plan_col_effect,
                    plan_qol_effect, plan_money_effect, passport_file]):
                blob_passport = convert_to_blob(passport_file)
                if other_file is not None:
                    blob_other_file = convert_to_blob(other_file)
                    load_result = _load_info(project_name, project_simple_desc, project_status, problem, sulution,
                                             plan_col_effect, plan_qol_effect, plan_money_effect, blob_passport,
                                             blob_other_file, status_project)
                else:
                    other_file = None
                    load_result = _load_info(project_name,project_simple_desc, project_status, problem, sulution,
                                             plan_col_effect, plan_qol_effect, plan_money_effect, blob_passport, other_file, status_project)
                if load_result is True:
                    st.session_state.info_project = "add"
                    return load_result
                else:
                    st.session_state.info_project = "not_add"
                    return load_result
            else:
                return "Ошибка: Все поля должны быть заполнены"
# -- Основная логика страницы
def interface():
    st.set_page_config(page_title="Добавить проект", layout="wide")
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
        result = add_project()
        if st.session_state.info_project == "add":
            st.sidebar.success(result)
        if st.session_state.info_project == "not_add":
            st.sidebar.error(result)
        authenticator.logout(button_name="Выйти", location="sidebar")

interface()