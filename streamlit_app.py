import streamlit as st

pg = st.navigation([st.Page("pages/homepage.py", title="Home")],[st.Page("pages/homepage.py",title="test")])
pg.run()

st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com)"
)


