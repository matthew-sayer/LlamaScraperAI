# LlamaScraperAI

Welcome to LlamaScraperAI, a scraper and conversational AI tool that enables you to ask questions about a URL and a specified number of associated links.

![image](https://github.com/user-attachments/assets/bc5715a4-2ffe-4621-9e0d-f2f3ce9de7c1)

## Features

- **Web Scraping**: Extracts data from a given URL and links on the same page.
- **Conversational AI**: Uses a Meta LLAMA 3 text-generation pipeline to answer questions based on the scraped data.
- **Semantic Search**: Implements semantic search to find the most relevant context for the questions.
- **Search Page**: Enables the user to search through the DuckDB contents held in memory.
- **Automated and manual evaluation**: Enables scoring of AI chat responses against input similarity, and then manual scoring against user feedback and stated intent.
- **Analytics Page**: Enables the user to query the automated evaluation and manual evaluation tables with customisable SQL.

## Requirements

- Docker (for containerised deployment)

### Python Packages

The required Python packages are listed in the `requirements.txt` file.

## Deployment
### Build the Docker image
docker build -t qnascraperai .

### Run the Docker container
docker run -p 8501:8501 qnascraperai

### Interact with the application
Open your web browser and navigate to http://localhost:8501.
Enter a URL to scrape data from.
Ask questions based on the scraped data.

## Model
The bot uses the meta-llama/Llama-3.2-1B model for the text generation pipeline. For this, you will need to sign up to the model on HuggingFace, and create a Huggingface Access Token environment variable. You can configure the model in the src/AI/conversationalAI.py file to change the model it uses:

```python
self.QAPipeline = pipeline(
            "text-generation",
            model="meta-llama/Llama-3.2-1B",
            token=accessToken)
```

Additionally, you can change the Semantic Search model in the same file.
```python
        self.semanticSearchModel = SentenceTransformer('all-MiniLM-L6-v2')
```
