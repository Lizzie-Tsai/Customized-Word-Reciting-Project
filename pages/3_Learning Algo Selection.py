import streamlit as st

st.title("My Learning Curve")

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False

if st.session_state["authentication_status"]:
    st.title(f'Welcome *{st.session_state["name"]}*')

    genre = st.radio(
        "Choose your learning Algo:",
        ('Algorithm 1', 'Algorithm 2'))

    if genre == 'Algorithm 1':
        st.write('You selected Algorithm 1.')
    else:
        st.write("You selected Algorithm 2.")
elif st.session_state["authentication_status"] is False:
    st.warning("Please login first.")
elif st.session_state["authentication_status"] is None:
    st.warning("Please login first.")