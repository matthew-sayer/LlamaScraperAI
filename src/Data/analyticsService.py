import duckdb
import logging
from src.Misc.error_handling import handleErrors
from src.Data.createDatabaseConnection import getAnalyticsDB

class AnalyticsService:
    @handleErrors(default_return_value=None)
    def __init__(self):
        self.analyticsDBconn = getAnalyticsDB()
    
    @handleErrors(default_return_value=None)
    def retrieveData(self, columnsInput="*", filters=""):

        try:
            query = f"SELECT {columnsInput} FROM performanceMonitor {filters}"
            return self.analyticsDBconn.execute(query).fetchdf()
        
        except Exception as e:
            logging.error(f"Failed to retrieve data from analytics DB: {e}")
            return None