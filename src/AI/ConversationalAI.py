from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from sentence_transformers import SentenceTransformer, util
import torch
import re
import logging
import os
import uuid
from datasets import load_dataset
import streamlit as st

from src.Misc.error_handling import handleErrors
from src.Misc.monitorTiming import monitorTiming

accessToken = os.getenv("HUGGINGFACE_ACCESS_TOKEN")

class ConversationalAI:
    @handleErrors()
    @monitorTiming
    def __init__(self, data):
        try:
            dataString = data.to_string(index=False)
            logging.info("Data loaded successfully")

            self.sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', dataString)

            logging.info("Initialising Semantic Search")
            self.semanticSearchModel = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings = self.semanticSearchModel.encode(self.sentences, convert_to_tensor=True) #Tensors are arrays which are used for calculations to find similarity
            #Tokens are the word in the sentence, embeddings are the vectors, which are numerical representations of tokens, that are used to find similarity between sentences
            self.device = self.setProcessingDevice()

            quantisationConfig = BitsAndBytesConfig(load_in_4bit=True)
            print("Initialising quantisation config")

            self.model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-3.2-1B",
                quantization_config=quantisationConfig
            )
            print("Model initialised and quantised")

            self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B") # This is a tokenizer, which turns text into tokens
            print("Tokenizer initialised")
            
            self.QAPipeline = pipeline(
                "text-generation",
                model=self.model,
                token=accessToken,
                tokenizer=self.tokenizer,
                #device=0 if self.device == torch.device('cuda') else -1 #-1 because that is the default value for CPU
                )
            print("Q&A Pipeline initialised")
            logging.info("Q&A Pipeline Initialised")

            self.analyticsService = st.session_state['analyticsService']

            self.topResponses = self.analyticsService.getTruePositiveResponses()

        except Exception as e:
            logging.error(f"Failed to initialise Conversational AI: {e}")
    
    #Set Processing Device
    @handleErrors(default_return_value=torch.device('cpu'))
    @monitorTiming
    def setProcessingDevice(self):
        if torch.cuda.is_available():
            logging.info("CUDA available. Using GPU for processing.")
            return torch.device('cuda')
        else:
            logging.info("CUDA is NOT available. Defaulting to CPU for processing.")
            return torch.device('cpu')
    
    @handleErrors(default_return_value="Error generating response.")
    @monitorTiming
    def generateResponse(self, userInput, topKSetting=5, topP=0.9, temperature=0.7, maxLlamaTokens=40):
        messageID = str(uuid.uuid4()) #Generate message ID
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
        output = re.sub(r'\s+', ' ', output)
        output = output.replace('Extracted_Text', '').strip()
        #Remove last words after the last full stop
        output = output[:output.rfind('.')+1]
        
        #invoke auto evaluation
        try:
            self.AutoEvaluateResponse(messageID, userInput, output)
        except Exception as e:
            logging.error(f"Failed to autoevaluate response: {e}")

        st.session_state['lastResponse'] = output
        st.session_state['lastMessageID'] = messageID
        st.session_state['lastUserInput'] = userInput
    
        return output
    
    @handleErrors(default_return_value=None)
    @monitorTiming
    def AutoEvaluateResponse(self, messageID, userInput, output):
        try:
            #Create encoded embeddings for the user input and output
            inputEmbeddings = self.semanticSearchModel.encode(userInput, convert_to_tensor=True)
            outputEmbeddings = self.semanticSearchModel.encode(output, convert_to_tensor=True)
            #Work out the cosine similarity to score it
            cosineSimilarity = util.pytorch_cos_sim(inputEmbeddings, outputEmbeddings).item() #item will get the tensor value

            self.analyticsService.automatedEvaluation(messageID, userInput, output, cosineSimilarity)

        except Exception as e:
            logging.error(f"Failed to autoevaluate response: {e}")
            return None
        
        return cosineSimilarity
    
    @handleErrors(default_return_value=None)
    @monitorTiming   
    def getManualFeedback(self, userScore, userIntent):
        print("function getManualFeedback called")
        userInput = st.session_state['lastUserInput']
        output = st.session_state['lastResponse']
        messageID = st.session_state['lastMessageID']
        try:
            intentSimilarity = self.extractIntent(output, userIntent)
            print("intent similarity gathered", intentSimilarity)
            TestResult = self.categoriseAccuracy(userScore, intentSimilarity)
            print("test result", TestResult)
            self.analyticsService.manualEvaluation(messageID, userInput, userIntent, output, userScore, intentSimilarity, TestResult)
            print("manual evaluation insert attempted done with fields", messageID, userInput, userIntent, output, userScore, intentSimilarity, TestResult)

        except Exception as e:
            logging.error(f"Failed to extract intent similarity: {e}")
            return None
        

    
    @handleErrors(default_return_value=None)
    @monitorTiming   
    def extractIntent(self, output, userIntent):
        outputEmbeddings = self.semanticSearchModel.encode(output, convert_to_tensor=True)
        userFeedbackEmbeddings = self.semanticSearchModel.encode(userIntent, convert_to_tensor=True)

        intentSimilarity = util.pytorch_cos_sim(outputEmbeddings, userFeedbackEmbeddings).item()

        return intentSimilarity
    
    @handleErrors(default_return_value=None)
    @monitorTiming   
    def categoriseAccuracy(self, userScore, intentSimilarity):
        if intentSimilarity > 0.5 and userScore == "Good":
            TestResult = "True Positive" #Great match - user said it was good, and it's similar to their intent
        elif intentSimilarity <= 0.5 and userScore == "Good":
            TestResult = "False Positive" #Good match - user liked it, but it wasn't similar to their original intent
        elif intentSimilarity > 0.5 and userScore == "Bad":
            TestResult = "False Negative" #Similar, but user didn't like it
        elif intentSimilarity <= 0.5 and userScore == "Bad":
            TestResult = "True Negative" #Not similar, and user didn't like it. Bad response.

        return TestResult