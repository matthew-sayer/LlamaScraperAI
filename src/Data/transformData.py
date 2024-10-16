from src.Misc.error_handling import handleErrors
from src.Misc.monitorTiming import monitorTiming

class TransformData:
    def __init__(self, df, conn):
        self.df = df
        self.conn = conn

    @handleErrors(default_return_value=None)
    @monitorTiming
    def transformData(self):
        transformedDF = self.df
        #drop nulls
        transformedDF = transformedDF.dropna()
        #drop duplicates
        transformedDF = transformedDF.drop_duplicates()
        #remove \n
        transformedDF = transformedDF.replace(r'\n',' ', regex=True)
        #remove excessive whitespace
        transformedDF = transformedDF.replace(r'\s+', ' ', regex=True)
        #remove [citation] tags
        transformedDF = transformedDF.replace(r'\[.*?\]', '', regex=True)

        return transformedDF
    
    @handleErrors(default_return_value=None)
    @monitorTiming
    def insertDataToDB(self, transformedDF):
        self.conn.execute('INSERT INTO data \
                            SELECT * FROM transformedDF')
            
    @handleErrors(default_return_value=None)
    @monitorTiming        
    def clearTable(self):
        self.conn.execute('DROP TABLE IF EXISTS data')
        
    @handleErrors(default_return_value=None)
    @monitorTiming 
    def insertURLsToHistoryDB(self, scrapedURLsDF):
        self.conn.execute('INSERT INTO scrapedURLs \
                              SELECT * FROM scrapedURLsDF')