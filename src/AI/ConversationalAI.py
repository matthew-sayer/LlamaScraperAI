from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import re
import logging

from src.Misc.error_handling import handleErrors

class ConversationalAI:
    @handleErrors()
    def __init__(self, data):
        dataString = data.to_string(index=False)
        logging.info("Data loaded successfully")

        self.sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', dataString)


        self.QAPipeline = pipeline(
            "question-answering",
            model="deepset/tinyroberta-squad2")
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
                            question=userInput,
                            context=context,
                            max_answer_len=1000)
        
        #remove whitespace before first letter of response
        output = re.sub(r'^\s+', '', response['answer'])
        
        return output