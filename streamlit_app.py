import streamlit as st

st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com)"
)

pg = st.navigation([st.Page("homepage.py", title="Home")],[st.Page("APcalculator.py",title="test")])
pg.run()




