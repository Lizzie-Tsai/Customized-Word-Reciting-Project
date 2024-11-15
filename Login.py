import streamlit as st
import streamlit_authenticator as stauth
#pip install psycopg2
import psycopg2
import pandas as pd
import yaml
from yaml.loader import SafeLoader

import pickle
from pathlib import Path

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)


# Initialize connection.
# Uses st.experimental_singleton to only run once.
# @st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()


# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


with open('./credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

users = run_query("SELECT * from user_1")
users = pd.DataFrame(users).iloc[:,[0,1,2,3]]
users.columns = ['username', 'name', 'email', 'password']
# st.table(users)
# print(config["credentials"]["usernames"])

for i in range(len(users)):
    username = users.iloc[i, 0]
    user_info = {'email': users.iloc[i, 2], 'name': users.iloc[i, 1],
                 'password': users.iloc[i, 3]}
    config["credentials"]["usernames"][username] = user_info
# print(config["credentials"]["usernames"])
# print(config)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"]
)

name, authentication_status, username = authenticator.login("Login", "main")
# print(authentication_status)
if st.session_state["authentication_status"]:
    st.session_state["login"] = True
    user_id = run_query(f"select user_id from user_1 as U where U.username = '{st.session_state['username']}'")
    user_id = pd.DataFrame(user_id)
    user_id.columns = ['user_id']
    user_id = user_id['user_id'][0]
    st.session_state['user_id'] = user_id
    authenticator.logout('Logout', 'main', key='unique_key')
    st.title(f'Welcome *{st.session_state["name"]}*')
    st.title('Ranking')
    users = run_query("SELECT U.username, count(L.is_right), U.level from user_1 as U, learning_history as L \
                      where U.user_id = L.user_id and L.is_right = True\
                      group by U.username \
                      order by count(L.is_right) desc")
    users = pd.DataFrame(users)
    users.columns = ['username', 'vocabulary learned', 'user level']
    st.table(users)
    # rows = run_query("SELECT * from city limit 20")
    # data = pd.DataFrame(rows)
    # data.columns = ['city_id', 'city', 'county_id', 'last_update']
    # st.table(data)

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

    #　(py_3.8) C:\Users\Lizzie0930\PycharmProjects\pythonProject3>
    # 　python -m streamlit run C:\Users\Lizzie0930\PycharmProjects\pythonProject3\Login.py

