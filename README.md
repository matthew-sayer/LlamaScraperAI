# QnAScraperAI

Welcome to QnAScraperAI, a basic and lightweight web scraper and conversational AI tool that enables you to ask questions about a URL and up to 5 associated links.

## Features

- **Web Scraping**: Extracts data from a given URL and up to 5 associated links.
- **Conversational AI**: Uses a question-answering pipeline to answer questions based on the scraped data.
- **Semantic Search**: Implements semantic search to find the most relevant context for the questions.

## Requirements

- Docker (for containerised deployment)

### Python Packages

The required Python packages are listed in the `requirements.txt` file:

```txt
streamlit==1.39.0
duckdb==1.1.1
pandas==2.2.3
requests==2.32.3
beautifulsoup4==4.12.3
torch==2.4.1
sentence-transformers==3.1.1
transformers==4.45.1
```

## Usage
Docker

# Build the Docker image:
docker build -t qnascraper .

# Run the Docker container:
docker run -p 8501:8501 qnascraper

# Interact with the application
Open your web browser and navigate to http://localhost:8501.
Enter a URL to scrape data from.
Ask questions based on the scraped data.

## Model
The bot uses the deepset/tinyroberta-squad2 model for the question-answering pipeline. This model is a smaller, efficient version of RoBERTa fine-tuned on the SQuAD2.0 dataset, making it suitable for lightweight applications.

## License
This project is licensed under the MIT License. See the LICENSE file for details.