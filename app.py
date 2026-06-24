import streamlit as st

st.set_page_config(page_title="World Cup Dashboard", layout="wide")

st.title("🌍 World Cup Group Dashboard")
st.write("Choose a group to view standings, match matrix, and remaining matches.")

group = st.selectbox("Group", list("ABCDEFGHIJKL"))

st.write("Selected group:", group)
