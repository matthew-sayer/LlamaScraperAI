class TransformData:
    def __init__(self, df, conn):
        self.df = df
        self.conn = conn

    def transformData(self):
        transformedDF = self.df
        #drop nulls
        transformedDF = transformedDF.dropna()
        #remove \n
        transformedDF = transformedDF.replace(r'\n',' ', regex=True)
        #remove excessive whitespace
        transformedDF = transformedDF.replace(r'\s+', ' ', regex=True)
        #remove [citation] tags
        transformedDF = transformedDF.replace(r'\[.*?\]', '', regex=True)

        return transformedDF

    def insertDataToDB(self, transformedDF):
        self.conn.execute('DROP TABLE IF EXISTS data')
        self.conn.execute('CREATE TABLE IF NOT EXISTS data \
                          AS SELECT \
                          * FROM transformedDF')

    