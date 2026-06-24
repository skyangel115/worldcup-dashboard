import streamlit as st

st.title("World Cup Dashboard")

group = st.selectbox(
    "Group",
    list("ABCDEFGHIJKL")
)

st.write("Selected group:", group)
