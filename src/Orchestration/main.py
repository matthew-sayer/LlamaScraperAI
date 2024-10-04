import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.Data import pipeline as datapl
from src.AI import ConversationalAI as ai

def main():
    print("Initialising Data")
    ingestionPath = 'https://en.wikipedia.org/wiki/Data_engineering'
    data = datapl.pipeline(ingestionPath)

    print("Initialising AI")
    conversation = ai.ConversationalAI(data)

    while True:
        userInput = input("Enter your question: ")
        if userInput == "exit":
            print("Exiting...")
            break
        response = conversation.generateResponse(userInput)
        print("Response:", response)

main()