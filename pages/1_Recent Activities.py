import streamlit as st
import psycopg2
import pandas as pd


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


st.title("Recent Activities")


if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False

# st.write("You have entered", st.session_state["my_input"])
if st.session_state["authentication_status"]:
    st.title(f'Welcome *{st.session_state["name"]}*')

    stat = run_query(f"select learn_date, count(learn_id)\
    from learning_history\
    where is_right = False and user_id = {st.session_state['user_id']}\
    group by learn_date")
    stat = pd.DataFrame(stat)


    stat_true = run_query(f"select learn_date, count(learn_id)\
    from learning_history \
    where is_right = True and user_id = {st.session_state['user_id']}\
    group by learn_date")
    stat_true = pd.DataFrame(stat_true)
    if len(stat) >= 1 and len(stat_true) >= 1:
        stat.columns = ['date', 'incorrect vocabulary count']
        stat_true.columns = ['date', 'correct vocabulary count']
    elif len(stat) >= 1 and len(stat_true) < 1:
        stat.columns = ['date', 'incorrect vocabulary count']
        stat_true['date'] = stat['date']
        stat_true['correct vocabulary count'] = [0 for i in range(len(stat['date']))]
    elif len(stat) < 1 and len(stat_true) >= 1:
        stat_true.columns = ['date', 'correct vocabulary count']
        stat['date'] = stat_true['date']
        stat['incorrect vocabulary count'] = [0 for i in range(len(stat_true['date']))]
    elif len(stat) < 1 and len(stat_true) < 1:
        stat['date'] = 0
        stat_true['date'] = 0
        stat['incorrect vocabulary count'] = 0
        stat_true['correct vocabulary count'] = 0
    try:
        stat = df = pd.merge(stat, stat_true, how='outer', on='date', suffixes=('_left', '_right'))
    except:
        pass
    st.bar_chart(stat, x='date', y=['incorrect vocabulary count', 'correct vocabulary count'])
    # st.warning("no learning history")




elif st.session_state["authentication_status"] is False:
    st.warning("Please login first.")
elif st.session_state["authentication_status"] is None:
    st.warning("Please login first.")

