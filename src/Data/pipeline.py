import duckdb
from ..Data.createDatabase import createDatabase
from ..Data.ingestData import Ingestion
from ..Data.transformData import TransformData

def pipeline(ingestionPath):
    #Create an in-memory database
    conn = createDatabase(':memory:')

   #Extract Data
    ingestionObject = Ingestion(ingestionPath, conn)
    df = ingestionObject.ingestData()

    #Transform and Load Data
    ETObject = TransformData(df, conn)
    transformedDF = ETObject.transformData()
    ETObject.insertDataToDB(transformedDF)

    data = conn.execute('SELECT * FROM data').fetchdf()
    print(data)

    return data