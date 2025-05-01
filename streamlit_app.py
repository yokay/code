import streamlit as st



pages = {
    "Push & Pull Transformer AP Value ": [
        st.Page("APcalculator.py", title="AP")
    ],
    "Cap and inductor": [
        st.Page("ImpedanceCalculator.py", title="Impedance")
    ],
    "Schulte Grid": [
        st.Page("SchulteGrid.py", title="Schulte Grid")
    ],
}

pg = st.navigation(pages)
pg.run()


st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com)"
)

