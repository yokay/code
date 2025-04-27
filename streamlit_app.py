import streamlit as st



pages = {
    "Push & Pull Transformer AP Value ": [
        st.Page("APcalculator.py", title="Calculator")
    ],
    "Home": [
        st.Page("homepage.py", title="Home")
    ],
}

pg = st.navigation(pages)
pg.run()


st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com)"
)

