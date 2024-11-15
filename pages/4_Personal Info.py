import streamlit as st
import psycopg2
import pandas as pd

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()



st.title("Personal Info")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False


if st.session_state["authentication_status"]:
    st.title(f'Welcome *{st.session_state["name"]}*')
    # st.write(f"SELECT * from user_1 WHERE username = '{st.session_state['username']}'")
    userinfo = run_query(f"SELECT * from user_1 WHERE username = '{st.session_state['username']}'")
    userinfo = pd.DataFrame(userinfo)
    userinfo.columns = ['username', 'name', 'email', 'password', 'gender', 'birth', 'prepare_time', 'level', 'user_id']

    # st.balloons()
    st.write("Your Name:")
    st.info(userinfo["name"][0])
    st.write("Your Username:")
    st.info(userinfo["username"][0])
    st.write("Your Email:")
    st.info(userinfo["email"][0])
    st.write("Your Gender:")
    st.info(userinfo["gender"][0])
    st.write("Your Prepare Time:")
    st.info(userinfo["prepare_time"][0])
    st.write("Your Level:")
    st.info(userinfo["level"][0])

    # st.table(userinfo)
elif st.session_state["authentication_status"] is False:
    st.warning("Please login first.")
elif st.session_state["authentication_status"] is None:
    st.warning("Please login first.")

