import duckdb
from createDatabase import createDatabase
from ingestData import Ingestion
from transformData import TransformData

def pipeline(ingestionPath, isWeb):
    #Create an in-memory database
    conn = createDatabase(':memory:')

    #Ingest data from source
    ingestionObject = Ingestion(ingestionPath, conn, isWeb)
    df = ingestionObject.ingestData()
    ingestionObject.insertDataToDB(df)

    #Transform data in DBT
    transformationObject = TransformData()
    transformationObject.transformData()

ingestionPath = 'https://en.wikipedia.org/wiki/Data_engineering'
isWeb = True

pipeline(ingestionPath, isWeb)
