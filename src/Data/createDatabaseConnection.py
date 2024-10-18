import duckdb
from src.Misc.error_handling import handleErrors
import logging
import streamlit as st

_mainDBConnection = None
_analyticsDBConnection = None

@handleErrors(default_return_value=None)
@st.cache_resource
def createMainDB(path=':memory:'):
    global _mainDBConnection
    if _mainDBConnection is None:
        try:
            _mainDBConnection = duckdb.connect(path)
            logging.info(f"Connected to database at {path}")
            _mainDBConnection.execute("CREATE TABLE IF NOT EXISTS data (Extracted_Text TEXT)")
            _mainDBConnection.execute("CREATE TABLE IF NOT EXISTS scrapedURLs (URL TEXT)")
        except:
            logging.error(f"Failed to connect to database at {path}")
            _mainDBConnection = None
    else:
        logging.info(f"Database connection already exists at {path}")

    return _mainDBConnection

@handleErrors(default_return_value=None)
@st.cache_resource
def getAnalyticsDB(path='analytics.db'):
    global _analyticsDBConnection

    if _analyticsDBConnection is None:
        try:
            _analyticsDBConnection = duckdb.connect(path)
            logging.info(f"Connected to analytics database at {path}")
            createAnalyticsTables(_analyticsDBConnection)
        except duckdb.Error as e:
            logging.error(f"Failed to connect to database at {path}: {e}")
            _analyticsDBConnection = None
        except Exception as e:
            logging.error(f"Unexpected error while connecting to database at {path}: {e}")
            _analyticsDBConnection = None
    else:
        logging.info(f"Analytics database connection already exists at {path}")

    return _analyticsDBConnection

@handleErrors(default_return_value=None)
def createAnalyticsTables(_analyticsDBConnection):
    try:
        _analyticsDBConnection.execute("""CREATE TABLE IF NOT EXISTS \
                                performanceMonitor \
                                (Start_Time DATETIME \
                                ,Function_Name TEXT  \
                                ,Time_Taken DOUBLE \
                                ,Run_Success BOOLEAN \
                                )""")
        
        _analyticsDBConnection.execute("""CREATE TABLE IF NOT EXISTS \
                                        autoEvaluation \
                                        (MessageID STRING PRIMARY KEY \
                                        ,UserInput TEXT \
                                        ,Response TEXT \
                                        ,SimilarityScore DOUBLE \
                                        ,Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP \
                                       )""")

        _analyticsDBConnection.execute("""CREATE TABLE IF NOT EXISTS \
                                        manualEvaluation \
                                        (MessageID STRING PRIMARY KEY \
                                        ,UserInput TEXT \
                                        ,UserIntent TEXT \
                                        ,Response TEXT \
                                        ,UserScore TEXT \
                                        ,IntentSimilarity DOUBLE \
                                        ,TestResult TEXT \
                                        ,Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP \
                                       )""")
        logging.info("Tables created in analytics database")
    except duckdb.Error as e:
        logging.error(f"Failed to create tables in analytics database: {e}")
        return None