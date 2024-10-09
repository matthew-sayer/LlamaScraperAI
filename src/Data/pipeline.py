import duckdb
from src.Data.createDatabase import createDatabase
from src.Data.ingestData import Ingestion
from src.Data.transformData import TransformData
from src.Misc.error_handling import handleErrors

@handleErrors(default_return_value=None)
def pipeline(ingestionPath, maxURLs):
    #Create an in-memory database
    conn = createDatabase(':memory:')

   #Extract Data
    ingestionObject = Ingestion(ingestionPath, conn, maxURLs)
    df = ingestionObject.ingestData()

    #Transform and Load Data
    ETObject = TransformData(df, conn)
    transformedDF = ETObject.transformData()
    ETObject.insertDataToDB(transformedDF)

    data = conn.execute('SELECT * FROM data').fetchdf()
    print(data)

    return data