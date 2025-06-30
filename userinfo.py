import sqlite3
import streamlit as st

DB_PATH = r"C:\Users\onekil1\Coding\project_lib\database\project_lib_db.db"

# -- Информационная панель пользователя
def profile_info():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("SELECT unit, role FROM accounts WHERE username = ?", (st.session_state["username"], ))
    user_info = [row for row in cursor.fetchall()]
    role = user_info[0][1]
    unit = user_info[0][0]
    profile = {
        "Пользователь:": st.session_state["name"] ,
        "Подразделение:": unit ,
        "Роль:": role
    }
    st.sidebar.write("### Информация о пользователе:")
    st.sidebar.write(profile)
    col1, col2 = st.sidebar.columns(2)
    if role == "Просмотр" or "Администратор" or "Координатор проектов" or "Эксперт":
        with col1:
            if st.button("Список проектов "):
                st.switch_page("pages/1_project_list.py")
    if role == "Эксперт" or "Администратор":
        with col2:
            if st.button("Согласование проекта"):
                st.switch_page("pages/3_accept_project_list.py")
    if role == "Администратор" or "Координатор проектов":
        with col1:
            if st.button("Добавить проект"):
                st.switch_page("pages/2_add_project.py")
    if role == "Администратор":
        with col1:
            if st.button("Удалить проект"):
                st.switch_page("pages/5_delete_project_list.py")
    if role == "Координатор проектов" or "Администратор":
        with col2:
            if st.button("Корректировка проекта"):
                st.sidebar.write("В разработке")

def local_css():
    file = r"C:\Users\onekil1\Coding\project_lib\styles.css"
    with open(file) as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

if __name__ == "__main__":
    print("1")