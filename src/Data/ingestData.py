import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
import time
from src.Misc.error_handling import handleErrors

class Ingestion:
    def __init__(self, ingestionPath, connection):
        self.ingestionPath = ingestionPath
        self.conn = connection
        self.visitedURLs = set()

    @handleErrors(default_return_value=None)
    def getPageContent(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    
    @handleErrors(default_return_value=([], None))
    def getPageParagraphs(self, content):
        soupResponse = soup(content, 'html.parser')
        paragraphs = [p.text for p in soupResponse.find_all('p')]
        return paragraphs, soupResponse
    
    @handleErrors(default_return_value=set())
    def getPageLinks(self, soupResponse, baseURL):
        links = set()
        for link in soupResponse.find_all('a', href=True):
            URL = urljoin(baseURL, link['href'])
            if URL not in self.visitedURLs:
                links.add(URL)
        return links

    @handleErrors(default_return_value=pd.DataFrame(columns=['scrapedText']))
    def ingestData(self):
            currentURL = self.ingestionPath
            paragraphsList = []
            urlsToVisit = {currentURL}
            urlsScraped = 0
            
            HTMLContents = self.getPageContent(currentURL)
            paragraphs, soupResponse = self.getPageParagraphs(HTMLContents)
            paragraphsList.extend(paragraphsList)

            newLinks = self.getPageLinks(soupResponse, currentURL)
            urlsToVisit.update(newLinks)


            for url in urlsToVisit:
                if urlsScraped >= 5:
                    print("Max URLs scraped")
                    break
                
                if url not in self.visitedURLs:
                        self.visitedURLs.add(url)
                        time.sleep(1)
                        HTMLContents = self.getPageContent(url)
                        paragraphs, _ = self.getPageParagraphs(HTMLContents)
                        paragraphsList.extend(paragraphs)
                        urlsScraped += 1

            df = pd.DataFrame(paragraphsList, columns=['scrapedText'])
            return df