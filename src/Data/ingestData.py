#Ingest data from specified file

import pandas as pd
import requests
from bs4 import BeautifulSoup as soup

class Ingestion:
    def __init__(self, ingestionPath, connection):
        self.ingestionPath = ingestionPath
        self.conn = connection

    def ingestData(self):
            response = requests.get(self.ingestionPath)
            soupResponse = soup(response.content, 'html.parser') 
            soupData = {'paragraphs': [p.text for \
                        p in soupResponse.find_all('p')]}
            df = pd.DataFrame(soupData['paragraphs'], columns=['scrapedText'])
            return df
        
    def insertDataToDB(self, df):
        self.conn.execute('DROP TABLE IF EXISTS data')
        self.conn.execute('CREATE TABLE IF NOT EXISTS data \
                          AS SELECT \
                          * FROM df')