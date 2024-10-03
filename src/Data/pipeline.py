import duckdb
from createDatabase import createDatabase
from ingestData import Ingestion
from transformData import TransformData

def pipeline(ingestionPath):
    #Create an in-memory database
    conn = createDatabase(':memory:')

    #Ingest data from source
    ingestionObject = Ingestion(ingestionPath, conn)
    df = ingestionObject.ingestData()
    ingestionObject.insertDataToDB(df)

    #Transform data in DBT
    transformationObject = TransformData()
    transformationObject.transformData()

ingestionPath = 'https://en.wikipedia.org/wiki/Data_engineering'

pipeline(ingestionPath)
