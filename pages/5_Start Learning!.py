import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
from datetime import date

st.title("Start Learning!")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False


if st.session_state["authentication_status"]:

    if "keep_graphics" not in st.session_state:
        st.session_state["keep_graphics"] = True
    if "finish_review" not in st.session_state:
        st.session_state["finish_review"] = False
    if "no_q" not in st.session_state:
        st.session_state["no_q"] = False


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


    def insert_data(insertion):
        with conn.cursor() as cur:
            cur.execute(insertion)
            print("data inserted")
            conn.commit()
            cur.close()

    if st.session_state.keep_graphics and ~(st.session_state.finish_review):
        # st.info("enter first block")
        user_id = run_query(f"select user_id from user_1 as U where U.username = '{st.session_state['username']}'")
        user_id = pd.DataFrame(user_id)
        user_id.columns = ['user_id']
        user_id = user_id['user_id'][0]
        st.session_state['user_id'] = user_id
        print("user_id = 111111", user_id)

        try:
            review_time = [0, 1, 3, 6]
            review_q = run_query(
                f"select max(L.learn_date) as learn_date, max(L.r_count) as r_count, L.mean_id \
                    from user_1 as U, learning_history as L \
                    where L.user_id = {user_id} and r_count < 4 \
                    group by L.mean_id")
            review_q = pd.DataFrame(review_q)
            review_q.columns = ['learn_date', 'r_count', 'mean_id']
            review_q_info = pd.DataFrame(columns=['learn_date', 'r_count', 'mean_id'])
            for i in range(len(review_q)):
                today = date.today()
                if (today - review_q['learn_date'][i]).days >= review_time[int(review_q['r_count'][i])+1] - review_time[int(review_q['r_count'][i])]:
                    entry = review_q[review_q['mean_id'] == int(review_q['mean_id'][i])]
                    review_q_info = pd.concat([review_q_info, entry])
            review_q = review_q_info
            question = review_q.sample(n=1, random_state=1)
            question = question.reset_index()
            question_info = run_query(f"select M.mean_id, M.vocab_id, V.name_1, meaning, part_of_speech, example \
                from meaning as M, vocab as V \
                where M.mean_id = {int(question['mean_id'][0])} and M.vocab_id = V.vocab_id")
            question_info = pd.DataFrame(question_info)
            question_info.columns = ['mean_id', 'vocab_id', 'vocabulary', 'meaning', 'part of speech', 'example']
            question_info['r_count'] = question['r_count']

            st.session_state['question'] = question_info
            

        except:
            st.session_state["finish_review"] = True
            st.session_state['undo_q'] = None
            st.session_state['question'] = None
            st.session_state['option_1'] = None
            st.session_state['option_2'] = None
            st.session_state['learning_history'] = None

        try:
            option_cand = run_query(
                f"select mean_id, vocab_id from meaning as M where M.mean_id != {int(question_info['mean_id'])}")
            option_cand = pd.DataFrame(option_cand)
            option_cand.columns = ['mean_id', 'vocab_id']
            option = option_cand.sample(n=3, random_state=1)
            option = option.reset_index()
            option_info = pd.DataFrame(
                columns=['mean_id', 'vocab_id', 'vocabulary', 'meaning', 'part of speech', 'example'])
            for i in range(len(option)):
                entry = run_query(f"select M.mean_id, M.vocab_id, V.name_1, meaning, part_of_speech, example \
                    from meaning as M, vocab as V \
                    where M.mean_id = {int(option['mean_id'][i])} and M.vocab_id = V.vocab_id")
                entry = pd.DataFrame(entry)
                entry.columns = ['mean_id', 'vocab_id', 'vocabulary', 'meaning', 'part of speech', 'example']
                option_info = pd.concat([option_info, entry])

            option_info = option_info.reset_index()
            st.session_state['option_1'] = option_info

            option = pd.concat([question_info, option_info])
            option = option.sample(frac=1)
            option = option.reset_index()
            st.session_state['option_2'] = option
        except:
            pass

    if st.session_state.keep_graphics and st.session_state.finish_review:
        user_id = run_query(f"select user_id from user_1 as U where U.username = '{st.session_state['username']}'")
        user_id = pd.DataFrame(user_id)
        user_id.columns = ['user_id']
        user_id = user_id['user_id'][0]
        st.session_state['user_id'] = user_id
        print("user_id = 2222222", user_id)

        try:
            st.session_state["no_q"] = False
            undo_q = run_query(
                f"select Distinct M.mean_id, M.vocab_id, V.name_1, meaning, part_of_speech, example from meaning as M, vocab as V, user_1 as U, learning_history as L where M.vocab_id = V.vocab_id and M.mean_id not in (select mean_id from learning_history where user_id = {st.session_state['user_id']})")
            undo_q = pd.DataFrame(undo_q)
            undo_q.columns = ['mean_id', 'vocab_id', 'vocabulary', 'meaning', 'part of speech', 'example']
            st.session_state['undo_q'] = undo_q

            question_info = undo_q.sample(n=1, random_state=1)
            question_info = question_info.reset_index()
            question_info['r_count'] = 0
            st.session_state['question'] = question_info
        except:
            st.info("No more question! You have finished all the questions!")
            st.session_state["no_q"] = True
            st.session_state['undo_q'] = None
            st.session_state['question'] = None
            st.session_state['option_1'] = None
            st.session_state['option_2'] = None
            st.session_state['learning_history'] = None


        try:
            option_cand = run_query(
                f"select mean_id, vocab_id from meaning as M where M.mean_id != {int(question_info['mean_id'])}")
            option_cand = pd.DataFrame(option_cand)
            option_cand.columns = ['mean_id', 'vocab_id']
            option = option_cand.sample(n=3, random_state=1)
            option = option.reset_index()
            option_info = pd.DataFrame(
                columns=['mean_id', 'vocab_id', 'vocabulary', 'meaning', 'part of speech', 'example'])
            for i in range(len(option)):
                entry = run_query(f"select M.mean_id, M.vocab_id, V.name_1, meaning, part_of_speech, example \
                                from meaning as M, vocab as V \
                                where M.mean_id = {int(option['mean_id'][i])} and M.vocab_id = V.vocab_id")
                entry = pd.DataFrame(entry)
                entry.columns = ['mean_id', 'vocab_id', 'vocabulary', 'meaning', 'part of speech', 'example']
                option_info = pd.concat([option_info, entry])

            option_info = option_info.reset_index()
            st.session_state['option_1'] = option_info

            option = pd.concat([question_info, option_info])
            option = option.sample(frac=1)
            option = option.reset_index()
            st.session_state['option_2'] = option
        except:
            pass

        learning_history = run_query("select * from learning_history")
        learning_history = pd.DataFrame(learning_history)
        st.session_state['learning_history'] = learning_history



    else:
        print('')

    if not (st.session_state["no_q"]):
        with st.form("my_form"):
            st.subheader(f'{st.session_state["question"]["vocabulary"][0]}')
            empty = st.empty()
            option_vocab = [st.session_state['option_2']['meaning'][0], st.session_state['option_2']['meaning'][1], st.session_state['option_2']['meaning'][2], st.session_state['option_2']['meaning'][3]]
            option_radio = empty.radio('choose the Mandarin translation of the vocabulary', option_vocab)
            st.session_state.keep_graphics = False
            submit = st.form_submit_button('Submit your answer')
            if submit:
                st.session_state.keep_graphics = True
                empty.empty()
                timestamp = datetime.now()
                learn_date = date.today()
                print()
                print(
                    f"INSERT INTO learning_history(vocab_id, mean_id, user_id, time, is_right) VALUES({st.session_state['question']['vocab_id'][0]}, {st.session_state['question']['mean_id'][0]}, {st.session_state['user_id']}, '{timestamp}', {option_radio == st.session_state['question']['meaning'][0]});")
                print()
                update_r_count = int(st.session_state['question']['r_count'])+1
                learned = insert_data(
                    f"INSERT INTO learning_history(vocab_id, mean_id, user_id, time, is_right, learn_date, r_count) VALUES({st.session_state['question']['vocab_id'][0]}, {st.session_state['question']['mean_id'][0]}, {st.session_state['user_id']}, '{timestamp}', {option_radio == st.session_state['question']['meaning'][0]}, '{learn_date}', {update_r_count});")

                st.write(f'You have submitted your answer: {option_radio}')
                if option_radio == st.session_state["question"]["meaning"][0]:
                    st.success("Your answer is correct!! Congratulation!!")
                    st.balloons()
                else:
                    st.warning("Your answer is incorrect! Don't worry, we will get back to this vocabulary later!")
                st.write(f'Here is an example sentence of: {st.session_state["question"]["vocabulary"][0]}')
                st.write(st.session_state["question"]["example"][0])

                learning_history = run_query("select * from learning_history")
                learning_history = pd.DataFrame(learning_history)
        next_q = st.button('Next question')




elif st.session_state["authentication_status"] is False:
    st.warning("Please login first.")
elif st.session_state["authentication_status"] is None:
    st.warning("Please login first.")


# st.write("Ok now it's multi-  \nline")



# select name_1, meaning, part_of_speech, example
# from meaning as M, vocab as V
# where M.vocab_id = V.vocab_id


# select Distinct V.name_1, meaning, part_of_speech, example
# from meaning as M, vocab as V, user_1 as U, learning_history as L
# where M.vocab_id = V.vocab_id
# and L.user_id = 1
# and L.mean_id != M.mean_id

# select Distinct V.name_1, meaning, part_of_speech, example
# from meaning as M, vocab as V, user_1 as U, learning_history as L
# where M.vocab_id = V.vocab_id
# and L.mean_id != M.mean_id
# and L.user_id = U.user_id
# and U.username = 'jennie'


# select Distinct M.mean_id, M.vocab_id, V.name_1, meaning, part_of_speech, example
# from meaning as M, vocab as V, user_1 as U, learning_history as L
# where M.vocab_id = V.vocab_id and M.mean_id not in (select mean_id from learning_history)

# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sample.html

# INSERT INTO learning_history(learn_id, vocab_id, mean_id, user_id, time, is_right) VALUES(2, 2, 2, 1, 2023-05-28 23:59:47.182208, True);

# and L.user_id = U.user_id and U.username = '{st.session_state['username']}' and

# select max(L.learn_date) as learn_date, max(L.r_count) as r_count, L.mean_id
# from user_1 as U, learning_history as L
# where U.user_id = 1 and r_count < 4
# group by L.mean_id