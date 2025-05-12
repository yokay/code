import streamlit as st

pages = {
    "Push & Pull Transformer AP Value ": [
        st.Page("APcalculator.py", title="AP")
    ],
    "Cap and inductor": [
        st.Page("ImpedanceCalculator.py", title="Impedance")
    ],
    "Smith Chart": [
        st.Page("SmithChart.py", title="Smith Chart") 
    ],
    "Unit Calc": [
        st.Page("unitCal.py", title="Unit Calc")
    ],
    "TO DO OR NOT TO DO": [
        st.Page("DOORNOTTODO.py", title="DO OR NOT TO DO")
    ]
}

pg = st.navigation(pages)
pg.run()


st.write(
    "Copyright © 2025 by [MYTHBIRD](https://www.mythbird.com)"
)

