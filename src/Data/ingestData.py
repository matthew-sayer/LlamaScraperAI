import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
import time
from src.Misc.error_handling import handleErrors
from src.Misc.monitorTiming import monitorTiming

class Ingestion:
    def __init__(self, ingestionPath, connection, maxURLs):
        self.ingestionPath = ingestionPath
        self.conn = connection
        self.scrapedURLs = set()
        self.maxURLs = maxURLs

    @handleErrors(default_return_value=None)
    @monitorTiming
    def getPageContent(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    
    @handleErrors(default_return_value=([], None))
    @monitorTiming
    def getPageParagraphs(self, content):
        soupResponse = soup(content, 'html.parser')
        paragraphs = [p.text for p in soupResponse.find_all('p')]
        return paragraphs, soupResponse
    
    @handleErrors(default_return_value=set())
    @monitorTiming
    def getPageLinks(self, soupResponse, baseURL):
        links = set()
        for link in soupResponse.find_all('a', href=True):
            URL = urljoin(baseURL, link['href'])
            if URL not in self.scrapedURLs:
                links.add(URL)
        return links
    
    @handleErrors(default_return_value=pd.DataFrame(columns=['scrapedText']))
    @monitorTiming
    def ingestData(self):
            currentURL = self.ingestionPath
            paragraphsList = []
            urlsToVisit = {currentURL}
            urlsScraped = 0
            
            HTMLContents = self.getPageContent(currentURL)
            paragraphs, soupResponse = self.getPageParagraphs(HTMLContents)
            paragraphsList.extend(paragraphs)

            newLinks = self.getPageLinks(soupResponse, currentURL)
            urlsToVisit.update(newLinks)


            for url in urlsToVisit:
                if urlsScraped >= self.maxURLs:
                    print("Max URLs scraped")
                    break
                
                if url not in self.scrapedURLs:
                        self.scrapedURLs.add(url)
                        time.sleep(1)
                        HTMLContents = self.getPageContent(url)
                        paragraphs, _ = self.getPageParagraphs(HTMLContents)
                        paragraphsList.extend(paragraphs)
                        urlsScraped += 1

            df = pd.DataFrame(paragraphsList, columns=['Extracted_Text'])
            scrapedURLs = pd.DataFrame(list(self.scrapedURLs), columns=['Scraped_URLs'])
            return df, scrapedURLs