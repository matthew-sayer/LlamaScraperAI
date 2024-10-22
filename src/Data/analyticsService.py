import duckdb
import logging
from src.Misc.error_handling import handleErrors
from src.Data.createDatabaseConnection import getAnalyticsDB

class AnalyticsService:
    @handleErrors(default_return_value=None)
    def __init__(self):
        self.analyticsDBconn = getAnalyticsDB()
    
    @handleErrors(default_return_value=None)
    def retrievePerformanceData(self, columnsInput="*", filters=""):

        try:
            query = f"SELECT {columnsInput} FROM performanceMonitor {filters}"
            return self.analyticsDBconn.execute(query).fetchdf()
        
        except Exception as e:
            logging.error(f"Failed to retrieve data from performance data table: {e}")
            return None
        
    @handleErrors(default_return_value=None)    
    def retrieveAutoEvaluationData(self, columnsInput="*", filters=""):
        try:
            query = f"SELECT {columnsInput} FROM autoEvaluation {filters}"
            return self.analyticsDBconn.execute(query).fetchdf()
        except Exception as e:
            logging.error("Failed to retrieve data from autoEvaluation table: {e}")
        
    @handleErrors(default_return_value=None)
    def retrieveManualEvaluationData(self, columnsInput="*", filters=""):
        try:
            query = f"SELECT {columnsInput} FROM manualEvaluation {filters}"
            return self.analyticsDBconn.execute(query).fetchdf()
        except Exception as e:
            logging.error("Failed to retrieve data from manualEvaluation table: {e}")

    @handleErrors(default_return_value=None)
    def automatedEvaluation(self, messageID, userInput, output, cosineSimilarity):
        try:
            self.analyticsDBconn.execute("""INSERT INTO autoEvaluation \
                                         (MessageID \
                                         ,UserInput \
                                         ,Response \
                                         ,SimilarityScore \
                                         ) \
                                         VALUES (?, ?, ?, ?)""",
                                         (messageID, userInput, output, cosineSimilarity))
        except Exception as e:
            logging.error(f"Failed to insert data into autoEvaluation table: {e}")
            return None
        
    def manualEvaluation(self, messageID, userInput, userIntent, output, userScore, intentSimilarity, TestResult):
        try:
            self.analyticsDBconn.execute("""INSERT INTO manualEvaluation \
                                         (MessageID \
                                         ,UserInput \
                                         ,UserScore
                                         ,Response \
                                         ,UserIntent \
                                         ,IntentSimilarity\
                                         ,TestResult)
                                         VALUES (?,?,?,?,?,?,?)""",
                                         (messageID, userInput, userScore, output, userIntent, intentSimilarity, TestResult))
        except Exception as e:
            logging.error(f"Failed to insert data into manualEvaluation table: {e}")
            return None