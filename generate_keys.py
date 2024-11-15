import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Peter Parker", "Rebecca Miller"]
usernames = ["pparker", "rmiller"]
passwords = ["abc", "def"]

hashed_passwords = stauth.Hasher(passwords).generate()
print(hashed_passwords)
'''
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
'''



'''
names = ["Peter Parker", "Rebecca Miller"]
usernames = ["pparker", "rmiller"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.authenticate(names,usernames,hashed_passwords, 'some_cookie_name','some_signature_key',cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")
'''

'''
list_usernames = ["jsmith", "rbriggs"]
list_email = ["jsmith@gmail.com", "rbriggs@gmail.com"]
list_name = ["John Smith", "Rebecca Briggs"]
list_passwords = ["abc123", "def456"] # 123 456 to be replaced by hashed values
list_emails_prehautorized = "melsby@gmail.com"
list_value_cookies = [30, "random_signature_key", "random_cookie_name"]


def autentificator_list_dict(list_usernames_, list_email_, list_name_, list_passwords_, list_emails_prehautorized_, list_value_cookies_):
    list_user = ["email", "name", "password"]
    list_cookies = ["expiry_days", "key", "name"]
    list_value_prehautorized = {"emails": list_emails_prehautorized_}
    # generation user list
    l_user_values = []
    for n in range(len(list_user) - 1):
        l_user_values.append([list_email_[n], list_name_[n], list_passwords_[n]])

    # list to dict
    credentials = {}
    usernames = {}
    cookie = {"cookie": dict(zip(list_cookies, list_value_cookies_))}
    prehautorized = {"preauthorized": list_value_prehautorized}

    user_values = {}
    for n in range(len(list_usernames_)):
        usernames[list_usernames_[n]] = dict(zip(list_user, l_user_values[n]))

    usernames = {"usernames": usernames}
    config = {"credentials": usernames, **cookie, **prehautorized}  # merge dict
    return config


config = autentificator_list_dict(list_usernames,list_email,list_name,list_passwords,list_emails_prehautorized,list_value_cookies)
print(config)
print(config["credentials"])
print(config["cookie"]["name"])
print(config["cookie"]["key"])
print(config["cookie"]["expiry_days"])
print(config["preauthorized"])
'''

'''
    if "my_input" not in st.session_state:
        st.session_state["my_input"] = ""

    my_input = st.text_input("Input a text here", st.session_state["my_input"])
    submit = st.button("Submit")
    if submit:
        st.session_state["my_input"] = my_input
        st.write("You have entered: ", my_input)


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

    rows = run_query("SELECT * from city limit 20")

    data=pd.DataFrame(rows)
    data.columns=['city_id','city','county_id','last_update']

    # st.title("Welcome to our English Learning APP!")
    st.table(data)
    result = st.button("Login to your account")
    if result:
        st.title("Login")
        with st.form("my_form"):
            st.write("Inside the form")
            slider_val = st.slider("Form slider")
            checkbox_val = st.checkbox("Form checkbox")

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.write("slider", slider_val, "checkbox", checkbox_val)

        st.write("Outside the form")
    else:
        st.title("Welcome to our English Learning APP!")
    '''

''''
if authentication_status == False:
    st.error("Username/password is incorrect")
if authentication_status == None:
    st.warning("Please enter your username and password")
if authentication_status:
    st.title("Main Page")
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Welcome {name}!")
    st.sidebar.success("Select a page above.")
'''