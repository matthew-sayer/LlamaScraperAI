#Ingest data from specified file

import pandas as pd
import requests
from bs4 import BeautifulSoup as soup

class Ingestion:
    def __init__(self, ingestionPath, connection, isWeb):
        self.ingestionPath = ingestionPath
        self.conn = connection
        self.isWeb = isWeb

    def ingestData(self):
        if self.isWeb: #If it's a web page, we'll scrape it.
            response = requests.get(self.ingestionPath)
            soupResponse = soup(response.content, 'html.parser') #Parsing the HTML content of the page.
            soupData = {'paragraphs': [p.text for \
                                       p in soupResponse.find_all('p')]}
            df = pd.DataFrame(soupData['paragraphs'], columns=['scrapedText'])

        else: #If it's a csv, we'll directly read it in with pandas.
            df = pd.read_csv(ingestionPath)
        
        return df
        
    def insertDataToDB(self, df):
        self.conn.execute('DROP TABLE IF EXISTS data')
        self.conn.execute('CREATE TABLE IF NOT EXISTS data \
                          AS SELECT \
                          * FROM df')