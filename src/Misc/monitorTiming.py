import time
import logging
from src.Data.createDatabaseConnection import getAnalyticsDB
from src.Misc.error_handling import handleErrors

@handleErrors(default_return_value=None)
def monitorTiming(func):
    def wrapper(*args, **kwargs): #The args and kwargs will allow us to pass any number of arguments to a function

        analyticsDBConnection = getAnalyticsDB()
        className = args[0].__class__.__name__ if args else 'UnknownClass'
        funcName = f"{className}.{func.__name__}"

        if analyticsDBConnection is None:
            logging.error("Failed to connect to analytics DB")
            return None
        startTime = time.time()
        startTimeFormatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
        try:
            result = func(*args, **kwargs)
            runSuccess = True
        except:
            logging.error(f"Function Failed to Run: {funcName}")
            runSuccess = None
            result = None
        endTime = time.time()

        timeTaken = endTime - startTime

        insertRecordToDB(analyticsDBConnection, startTimeFormatted, funcName, timeTaken, runSuccess)

        return result
    
    return wrapper
    
  
def insertRecordToDB(analyticsDBConnection, startTimeFormatted, funcName, timeTaken, runSuccess):
    analyticsDBConnection.execute("""INSERT INTO performanceMonitor \
                                    (Start_Time, Function_Name, Time_Taken, Run_Success) \
                                    VALUES (?,?,?,?)""", (startTimeFormatted, funcName, timeTaken, runSuccess)
    )