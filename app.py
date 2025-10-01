import streamlit as st
from db import engine
from models import Base

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

st.title("Amazon Cockpit")
st.write("✅ Backend and database are connected!")
