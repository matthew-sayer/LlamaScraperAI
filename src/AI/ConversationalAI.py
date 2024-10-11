from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import re
import logging
import os

from src.Misc.error_handling import handleErrors

accessToken = os.getenv("HUGGINGFACE_ACCESS_TOKEN")

class ConversationalAI:
    @handleErrors()
    def __init__(self, data):
        dataString = data.to_string(index=False)
        logging.info("Data loaded successfully")

        self.sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', dataString)


        self.QAPipeline = pipeline(
            "text-generation",
            model="meta-llama/Llama-3.2-1B",
            token=accessToken)
        logging.info("Q&A Pipeline Initialised")

        logging.info("Initialising Semantic Search")
        self.semanticSearchModel = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = self.semanticSearchModel.encode(self.sentences, convert_to_tensor=True)
   
    @handleErrors(default_return_value="Error generating response.")
    def generateResponse(self, userInput):
        queryEmbeddings = self.semanticSearchModel.encode(userInput, convert_to_tensor=True) #Encodes the user input in the same way as the sentences
        scores = util.pytorch_cos_sim(queryEmbeddings, self.embeddings)[0] #Find similarity (cosine) score between input and sentences
        topK = min(5, len(self.sentences)) #Grab the top 5 scoring similar sentences
        topScoringResults = torch.topk(scores, k=topK) # Top k results - this has the top k scores and corresponding locations in the content (indices)

        topScoringSentences = [self.sentences[index] for index in topScoringResults.indices]

        context = " ".join(topScoringSentences)

        response = self.QAPipeline(
                            userInput + " " + context,
                            max_new_tokens=15,
                            truncation=True,
                            pad_token_id=self.QAPipeline.tokenizer.eos_token_id
                            )
        
        #remove whitespace before first letter of response
        output = response[0]['generated_text'][len(userInput):]
        
        filteredOutput = self.filter_response(output, context)

        return filteredOutput
    
    def filter_response(self, response, context):
        contextSentences = set(context.split('. '))
        responseSentences = response.split('. ')
        filteredSentences = [sentence for sentence in responseSentences if sentence not in contextSentences]
        cleanedSentences = [sentence.replace('scrapedText', '') for sentence in filteredSentences]

        return '. '.join(cleanedSentences)
    