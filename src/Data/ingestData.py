import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
import time
import logging

#Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager #This is a package that automatically downloads the latest version of the Chrome driver

from src.Misc.error_handling import handleErrors
from src.Misc.monitorTiming import monitorTiming

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Ingestion:
    def __init__(self, ingestionPath, connection, maxURLs):
        self.ingestionPath = ingestionPath
        self.conn = connection
        self.scrapedURLs = set()
        self.maxURLs = maxURLs
        logging.info("Initialising driver for selenium")
        self.driver = self.initialiseDriver()
        if self.driver is None:
            logging.error("Driver initialisation failed")
            raise Exception("Driver initialisation failed")
        else:
            logging.info(f"Driver initialised successfully: {self.driver}")

    def initialiseDriver(self): 
        logging.info("Initialising Selenium driver")
        try:
            # Set up Chrome options
            driverOptions = Options()
            driverOptions.headless = True  # Running in headless mode for efficiency

            # Initialize the WebDriver with Chrome
            chrome_driver_version = "130.0.6723.5800"

            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager(driver_version=chrome_driver_version).install()), 
                options=driverOptions
            )

            # Wait a second to ensure the driver is fully started
            time.sleep(1) 
            logging.info("Selenium driver initialised successfully")
            return driver

        except Exception as e:
            logging.error(f"Error while initialising Selenium driver: {e}")
            return None
         

    @handleErrors(default_return_value=None)
    @monitorTiming
    def getPageContent(self, url): #Get the page contents of the specified URL
        try:
            logging.info(f"Getting page content from {url}")
            self.driver.get(url)
            time.sleep(5)
            pageSource = self.driver.page_source
            logging.debug("Page content length: ", len(pageSource))
            return pageSource
        except Exception as e:
            logging.error(f"Error while getting page content from {url}: {e}")
            return None
    
    @handleErrors(default_return_value=([], None))
    @monitorTiming
    def getPageParagraphs(self): #Extract paragraphs from the page
        logging.info("Extracting paragraphs from page")
        paragraphs = [p.text for p in self.driver.find_elements(By.TAG_NAME, 'p')]
        logging.info(f"Extracted {len(paragraphs)} paragraphs. List: {paragraphs}")
        return paragraphs
    
    @handleErrors(default_return_value=set())
    @monitorTiming
    def getPageLinks(self, baseURL): #Extract links from the page which can be visited
        logging.info("Extracting links from page")
        links = set()
        for link in self.driver.find_elements(By.TAG_NAME, 'a'):
            href = link.get_attribute('href')
            if href:
                URL = urljoin(baseURL, href)
                if URL not in self.scrapedURLs:
                     links.add(URL)
        return links
    
    @handleErrors(default_return_value=pd.DataFrame(columns=['scrapedText']))
    @monitorTiming
    def ingestData(self): #Orchestrate the ingestion process
            logging.info("Starting data ingestion process")
            paragraphsList = []
            urlsToVisit = [self.ingestionPath] #Creates a list with the initial specified URL starting
            self.scrapedURLs.add(self.ingestionPath) #Add the initial URL to the scraped URL list

            logging.debug(f"Initial URLs to visit: {urlsToVisit}")
            logging.debug(f"Initial scraped URLs: {self.scrapedURLs}")
            logging.debug(f"Max URLs to scrape: {self.maxURLs}")

            while urlsToVisit and len(self.scrapedURLs) <= self.maxURLs: #While the number of scraped URLs is less than the maximum number of URLs
                
                currentURL = urlsToVisit.pop(0) #pop gets the first URL in the list

                try:
                    logging.info(f"Scraping URL: {currentURL}")
                    content = self.getPageContent(currentURL) #Get the contents of the URL
                    if content is None:
                        logging.error("No content was scraped - the content is empty. The source may not have data or it may be blocked.")
                        continue

                    paragraphs = self.getPageParagraphs() #Get paragraphs from content

                    if not paragraphs:
                        logging.error(f"No paragraphs found for URL {currentURL}")
                        
                    paragraphsList.extend(paragraphs) #Add paragraphs to list

                    tables = self.driver.find_elements(By.TAG_NAME, 'table') #Find all tables on the page
                    for table in tables:
                        df = pd.read_html(table.get_attribute('outerHTML'))[0] #Get the outerHTML of the table and put it into a DF
                        paragraphsList.append({"Table": df}) #Add the table to the list of paragraphs
                        
                    newLinksToScrape = self.getPageLinks(currentURL) #Get the page links available
                    for newURL in newLinksToScrape:
                            if newURL not in self.scrapedURLs and newURL not in urlsToVisit:
                                urlsToVisit.append(newURL) #Add new URL to the list of URLs to visit
                    self.scrapedURLs.add(currentURL)

                    if not paragraphsList:
                        logging.error("No data was scraped - the paragraphs list is empty. The source may not have data or it may be blocked.")

                except Exception as e:
                    logging.error(f"Error while scraping {currentURL}: {e}")


            df = pd.DataFrame(paragraphsList, columns=['Extracted_Text'])
            scrapedURLs = pd.DataFrame(list(self.scrapedURLs), columns=['Scraped_URLs'])

            logging.info(f"Scraped data: {df.head()}")
            logging.info(f"Scraped URLs: {scrapedURLs.head()}")

            return df, scrapedURLs