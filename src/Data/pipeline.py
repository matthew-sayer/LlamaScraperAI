import duckdb
from ..Data.createDatabase import createDatabase
from ..Data.ingestData import Ingestion
from ..Data.transformData import TransformData

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

    data = conn.execute('SELECT * FROM data').fetchdf()

    return data