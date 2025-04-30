import streamlit as st
import sqlite3

# --- Ініціалізація БД ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE
        )
    ''')
    # Додаємо колонку password, якщо її ще немає
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN password TEXT NOT NULL DEFAULT ""')
        conn.commit()
    except sqlite3.OperationalError:
        # Колонка вже існує — ігноруємо
        pass
    conn.close()

# --- Безпечне додавання користувача ---
def add_user(username, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Параметризований запит
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        st.success(f"Користувач '{username}' успішно доданий!")
    except sqlite3.IntegrityError:
        st.warning("Це ім'я користувача вже існує.")
    except sqlite3.Error as e:
        st.error(f"Помилка при додаванні користувача: {e}")
    finally:
        conn.close()

# --- Увійти в систему ---
def login_user(username, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Параметризований запит для входу
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        return user is not None
    except sqlite3.Error as e:
        st.error(f"Помилка при вході: {e}")
        return False
    finally:
        conn.close()

# --- Показати всіх користувачів ---
def show_users():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        rows = cursor.fetchall()
        for row in rows:
            st.write(f"ID: {row[0]} | Username: {row[1]}")
    except sqlite3.Error as e:
        st.error(f"Помилка при отриманні користувачів: {e}")
    finally:
        conn.close()

# --- Основна логіка Streamlit ---
def main():
    st.title("🛡️ Захист від SQL-ін’єкцій та обробка помилок у Python")

    st.markdown("""
    ###  Що таке SQL-ін’єкція?
    SQL-ін’єкція — це атака, коли шкідливий код вставляється в SQL-запит, наприклад:  
    `' OR '1'='1` ➜ дає доступ до облікового запису без правильного паролю.

    ###  Як захиститися?
    -  **Не** створюйте запити через конкатенацію:
        ```python
        "SELECT * FROM users WHERE username = '" + username + "'"
        ```
    -  **Використовуйте параметризовані запити**:
        ```python
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        ```
        Код захищає від атак типу:
                
        `' OR '1'='1` — класичний спосіб обійти автентифікацію.

        `admin' --` — коментар для відсікання частини запиту.

        `' OR 1=1; --` — ін’єкція з логічним обчисленням.

        Будь-які інші маніпуляції через вставлення SQL-виразів у поля username або password.

    ###  Додайте нового користувача:
    """)
    
    with st.form("register_form"):
        reg_username = st.text_input("Ім’я користувача для реєстрації")
        reg_password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Зареєструвати")
        if submitted:
            if reg_username and reg_password:
                add_user(reg_username, reg_password)
            else:
                st.warning("Заповніть обидва поля!")

    st.markdown("### 🔐 Вхід в систему:")
    with st.form("login_form"):
        login_username = st.text_input("Ім’я користувача")
        login_password = st.text_input("Пароль", type="password")
        login_submitted = st.form_submit_button("Увійти")
        if login_submitted:
            if login_user(login_username, login_password):
                st.success(f"Ласкаво просимо, {login_username}!")
            else:
                st.error("Невірне ім’я користувача або пароль.")

    st.markdown("### 👥 Список зареєстрованих користувачів:")
    show_users()

if __name__ == "__main__":
    init_db()
    main()
