import streamlit as st

pg = st.navigation([st.Page("homepage.py", title="Home")],[st.Page("APcalculator.py",title="test")])
pg.run()

st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com)"
)


