import duckdb
from src.Misc.error_handling import handleErrors
import logging
import streamlit as st

_connection = None

@handleErrors(default_return_value=None)
@st.cache_resource
def createDatabase(path=':memory:'):
    global _connection
    if _connection is None:
        try:
            _connection = duckdb.connect(path)
            logging.info(f"Connected to database at {path}")
        except:
            logging.error(f"Failed to connect to database at {path}")
            _connection = None
    else:
        logging.info(f"Database connection already exists at {path}")
    return _connection