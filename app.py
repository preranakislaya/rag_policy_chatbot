import streamlit as st
import requests
from datetime import datetime
from database import create_tables, create_user, login_user, create_chat_tables, create_chat_session, get_user_sessions, save_message, load_messages, clear_chat_messages

st.set_page_config(
    page_title = 'Chatbot',
    layout = 'wide'
)

create_tables()
create_chat_tables()

st.title('Welcome to our AI chatbot')

# -------------------------
# LOGIN SESSION
# -------------------------

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'username' not in st.session_state:
    st.session_state.username = None


# -------------------------
# LOGIN PAGE
# -------------------------

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox('Menu', ['Login', 'Signup'])

    # LOGIN
    if menu == 'Login':
        st.subheader('Login')

        username = st.text_input('Username')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            user = login_user(username, password)

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]

                st.success("Login successful")
                st.rerun()

            else:
                st.error("Invalid username or password")

    # SIGNUP
    else:

        st.subheader("Create Account")
        new_username = st.text_input("Create Username")
        new_password = st.text_input('Create Password', type='password')

        if st.button('Signup'):

            success = create_user(new_username, new_password)

            if success:
                st.success("Account created successfully")

            else:
                st.error("Username already exists")

    st.stop()


# -------------------------
# CREATING CHAT SESSIONS
# -------------------------
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = None

if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# -------------------------
# SIDEBAR
# -------------------------

with st.sidebar:

    st.success(f"Logged in as: {st.session_state.username}")
    
    if st.button('Clear Current Chat'):
        
        if st.session_state.current_session_id:
            clear_chat_messages(st.session_state.current_session_id)

            st.rerun()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

    st.header("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose file",type=["pdf", "docx", "csv", "xlsx"]
    )

    if uploaded_file and not st.session_state.file_uploaded:
        with st.spinner("Uploading and processing file..."):
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue())
            }

            response = requests.post("http://backend:8000/upload", files=files)

            if response.status_code == 200:
                data = response.json()
                st.session_state.vector_id = data["vector_id"]

                session_name = uploaded_file.name

                session_id = create_chat_session(
                    st.session_state.user_id,
                    session_name,
                    data["vector_id"],
                    uploaded_file.name
                )

                st.session_state.current_session_id = session_id
                st.session_state.current_chat = session_name

                st.success(f"""
                    File uploaded successfully
                    Chunks created: {data['chunks']}
                    """
                )
                st.session_state.file_uploaded = True

            else:
                st.error("Upload failed")

    

    # show current active chat
    if st.session_state.current_chat:

        st.info(f"Current Chat: {st.session_state.current_chat}")


    # CREATING SIDEBAR CHAT HISTORY
    st.divider()
    st.subheader('Chat History')

    # NEW CHAT BUTTON
    if st.button('New Chat'):

        session_count = len(get_user_sessions(st.session_state.user_id)) + 1
        new_chat_name = 'New Chat'

        session_id = create_chat_session(
            st.session_state.user_id,
            new_chat_name
        )

        st.session_state.current_chat = new_chat_name
        st.session_state.current_session_id = session_id

        # reset current uploaded document
        if "vector_id" in st.session_state:
            del st.session_state.vector_id

        st.session_state.file_uploaded = False

        st.rerun()

    # SHOWING CHAT LIST
    sessions = get_user_sessions(st.session_state.user_id)

    for session in sessions:

        if st.button(
            session["session_name"],
            key=f"session_{session['id']}"
        ):

            st.session_state.current_chat = session["session_name"]
            st.session_state.current_session_id = session["id"]
            st.session_state.vector_id = session["vector_id"]
            st.session_state.file_uploaded = True

            st.rerun()

# DISPLAY CHAT
current_messages = []

if st.session_state.current_session_id:
    db_messages = load_messages(st.session_state.current_session_id)

    for msg in db_messages:
        current_messages.append({
            "role": msg["role"],
            "content": msg["content"],
            "time": msg["timestamp"]
        })

for msg in current_messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])
        st.caption(msg['time'])

# USER INPUT
query = st.chat_input('Ask your query...')

if query:

    # no active chat selected
    if not st.session_state.current_session_id:
        st.error("Please create chat first")
        st.stop()

    # saving user message to db
    save_message(st.session_state.current_session_id, 'user', query)

    with st.chat_message('user'):
        st.markdown(query)

    # check if document uploaded
    if "vector_id" not in st.session_state:

        st.error("Please upload document first")
        st.stop()

    # CALLING BACKEND PROGRAM
    response = requests.post(
        "http://backend:8000/chat",
        json = {'query': query, 'vector_id': st.session_state.vector_id}
        )

    answer = response.json()['answer']
    sources = response.json()['sources']

    # showing assistant response
    with st.chat_message('assistant'):
        st.markdown(answer)
        st.caption(f'Sources: {sources}')

    save_message(st.session_state.current_session_id, 'assistant', answer)

    

