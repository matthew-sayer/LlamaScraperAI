from src.Misc.error_handling import handleErrors

class TransformData:
    def __init__(self, df, conn):
        self.df = df
        self.conn = conn

    @handleErrors(default_return_value=None)
    def transformData(self):
        transformedDF = self.df
        #drop nulls
        transformedDF = transformedDF.dropna()
        #drop duplicates
        transformedDF = transformedDF.drop_duplicates()
        #convert to string
        transformedDF['scrapedText'] = transformedDF['scrapedText'].astype(str)
        #remove \n
        transformedDF = transformedDF.replace(r'\n',' ', regex=True)
        #remove excessive whitespace
        transformedDF = transformedDF.replace(r'\s+', ' ', regex=True)
        #remove [citation] tags
        transformedDF = transformedDF.replace(r'\[.*?\]', '', regex=True)

        return transformedDF
    
    @handleErrors(default_return_value=None)
    def insertDataToDB(self, transformedDF):
        try:
            tableExists = self.conn.execute(
                "SELECT * FROM data LIMIT 1"
            ).fetchdf()
        except:
            tableExists = None

        if tableExists is None or tableExists.empty:
            self.conn.execute('CREATE TABLE data \
                            AS SELECT \
                            * FROM transformedDF')
        else:
            self.conn.execute('INSERT INTO data \
                              SELECT * FROM transformedDF')
            
    @handleErrors(default_return_value=None)        
    def clearTable(self):
        self.conn.execute('DROP TABLE IF EXISTS data')