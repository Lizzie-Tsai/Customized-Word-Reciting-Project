import streamlit as st
import psycopg2
import pandas as pd
import datetime

st.title("My Learning History")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False



if st.session_state["authentication_status"]:
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


    option = st.selectbox(
        'Sort by which attribute?',
        ('time', 'level', 'vocabulary', 'part of speech'))
    if option == 'time':
        option = 'time'
    elif option == 'level':
        option = 'level_1'
    elif option == 'vocabulary':
        option = 'V.name_1'
    elif option == 'part of speech':
        option = 'part_of_speech'

    option_2 = st.selectbox(
        'Ascending or descending?',
        ('Ascending', 'Descending'))
    if option_2 == 'Ascending':
        option_2 = 'asc'
    elif option_2 == 'Descending':
        option_2 = 'desc'

    option_3 = st.selectbox(
        'Select vocabularies you answer correctly?',
        ('all vocabularies', 'only vocabularies I answer incorrectly', 'only vocabularies I answer correctly'))

    if option_3 == 'only vocabularies I answer incorrectly':
        option_3 = ' and L.is_right = False'
    elif option_3 == 'only vocabularies I answer correctly':
        option_3 = ' and L.is_right = True'
    elif option_3 == 'all vocabularies':
        option_3 = ''

    b_d = st.date_input(
        "What is the begin date you want to check?",
        datetime.date(2023, 5, 28))
    st.write('The begin date you want to check:', b_d)

    e_d = st.date_input(
        "What is the end date you want to check?",
        datetime.date(2023, 5, 30))
    st.write('The end date you want to check:', e_d)


    learning_history = run_query(f"select distinct L.is_right, L.learn_id, L.time, V.name_1, meaning, part_of_speech, example, level_1 \
    from vocab as V, user_1 as U, meaning as M, learning_history as L \
    where L.user_id = {st.session_state['user_id']} and V.vocab_id = M.vocab_id and L.mean_id = M.mean_id{option_3} and L.time >= '{b_d}' and L.time < '{e_d}' \
    order by {option} {option_2}")
    learning_history = pd.DataFrame(learning_history)
    try:
        learning_history.columns = ['is_right', 'learn_id', 'time', 'vocabulary', 'translation', 'part of speech', 'example', 'level']
    except:
        pass

    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8-sig')
        # return df.to_csv()


    csv = convert_df(learning_history)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='learning_history.csv',
        mime='text/csv',
    )

    st.table(learning_history)




elif st.session_state["authentication_status"] is False:
    st.warning("Please login first.")
elif st.session_state["authentication_status"] is None:
    st.warning("Please login first.")





# select L.learn_id, L.time, V.name_1, meaning, part_of_speech, example, level_1
# from vocab as V, user_1 as U, meaning as M, learning_history as L
# where U.user_id = 1 and V.vocab_id = M.vocab_id and L.mean_id = M.mean_id