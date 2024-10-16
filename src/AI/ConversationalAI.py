from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import re
import logging
import os
from datasets import load_dataset

from src.Misc.error_handling import handleErrors
from src.Misc.monitorTiming import monitorTiming

accessToken = os.getenv("HUGGINGFACE_ACCESS_TOKEN")

class ConversationalAI:
    @handleErrors()
    @monitorTiming
    def __init__(self, data):
        dataString = data.to_string(index=False)
        logging.info("Data loaded successfully")

        self.sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', dataString)

        logging.info("Initialising Semantic Search")
        self.semanticSearchModel = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = self.semanticSearchModel.encode(self.sentences, convert_to_tensor=True) #Tensors are arrays which are used for calculations to find similarity
        #Tokens are the word in the sentence, embeddings are the vectors, which are numerical representations of tokens, that are used to find similarity between sentences
        #self.loadDataset()
        self.device = self.setProcessingDevice()
        
        self.QAPipeline = pipeline(
            "text-generation",
            model="meta-llama/Llama-3.2-1B",
            token=accessToken,
            device=0 if self.device == torch.device('cuda') else -1 #-1 because that is the default value for CPU
            )
        logging.info("Q&A Pipeline Initialised")
    
    #Dataset Processing
    @handleErrors(default_return_value="Error loading dataset.")
    def loadDataset(self):
        self.dataset = load_dataset("MuskumPillerum/General-Knowledge")
        self.datasetEmbeddings = self.preprocessDatasetEmbeddings()

    @handleErrors(default_return_value="Error generating response.")
    @monitorTiming
    def preprocessDatasetEmbeddings(self):
        datasetRows = [row['Answer'] for row in self.dataset['train']]
        datasetEmbeddings = self.semanticSearchModel.encode(
            datasetRows,
            convert_to_tensor=True,
            batch_size=16
        ).to(self.device)
        return {'rows': datasetRows, 'embeddings': datasetEmbeddings}
    
    #Set Processing Device
    @handleErrors(default_return_value=torch.device('cpu'))
    @monitorTiming
    def setProcessingDevice(self):
        if torch.cuda.is_available():
            logging.info("CUDA available. Using GPU for processing.")
            print("USING CUDA")
            return torch.device('cuda')
        else:
            logging.info("CUDA is NOT available. Defaulting to CPU for processing.")
            print("USING CPU")
            return torch.device('cpu')
    
    @handleErrors(default_return_value="Error generating response.")
    @monitorTiming
    def generateResponse(self, userInput, topKSetting=5, topP=0.9, temperature=0.7, maxLlamaTokens=40):
        queryEmbeddings = self.semanticSearchModel.encode(
            userInput,
            convert_to_tensor=True,
            batch_size=16
            ).to(self.device) #Encodes the user input in the same way as the sentences
        
        scores = util.pytorch_cos_sim(queryEmbeddings, self.embeddings)[0] #Find similarity (cosine) score between input and sentences
        topK = min(topKSetting, len(self.sentences)) #Grab the top scoring similar sentences
        topScoringResults = torch.topk(scores, k=topK) # Top k results - this has the top k scores and corresponding locations in the content (indices)

        topScoringSentences = [self.sentences[index] for index in topScoringResults.indices]

        context = " ".join(topScoringSentences)

        #dataset = util.pytorch_cos_sim(queryEmbeddings, self.datasetEmbeddings['embeddings'])[0]
        #torchResult = torch.topk(dataset, k=5) #Top 5 results
        #datasetContext = self.datasetEmbeddings['rows'][torchResult.indices[0]][:100] #Take the first 100 characters

        combinedDataContext = f"{userInput} {context}"

        response = self.QAPipeline(
                            combinedDataContext,
                            max_new_tokens=maxLlamaTokens,
                            temperature=temperature,
                            top_p=topP,
                            truncation=True,
                            pad_token_id=self.QAPipeline.tokenizer.eos_token_id
                            )
        
        #remove whitespace before first letter of response
        output = response[0]['generated_text'][len(userInput):].strip()
        
        return output