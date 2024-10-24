import duckdb
from src.Data.createDatabaseConnection import createMainDB, getAnalyticsDB
from src.Data.ingestData import Ingestion
from src.Data.transformData import TransformData
from src.Misc.error_handling import handleErrors
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@handleErrors(default_return_value=None)
def pipeline(ingestionPath, maxURLs):
    #Create an in-memory scraped data database
    mainDBConn = createMainDB()
    
    if mainDBConn is None:
        logging.error("Failed to create database")
        return None

   #Extract Data
    logging.info("Initialising ingestion object")
    ingestionObject = Ingestion(ingestionPath, mainDBConn, maxURLs)
    df, scrapedURLs = ingestionObject.ingestData()
    

    #Transform and Load Data
    extractTransformObject = TransformData(df, mainDBConn)
    transformedDF = extractTransformObject.transformData()
    extractTransformObject.insertDataToDB(transformedDF)
    extractTransformObject.insertURLsToHistoryDB(scrapedURLs)

    data = mainDBConn.execute('SELECT * FROM data').fetchdf()
    scrapedURLsDF = mainDBConn.execute('SELECT * FROM scrapedURLs').fetchdf()

    return data, scrapedURLsDF, extractTransformObject