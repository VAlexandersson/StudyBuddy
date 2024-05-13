import os
from study_buddy import StudyBuddy
from llms.cohere_llm import CohereClient
from llms.huggingface_llm import HuggingFaceLLM
import chatbot_config

if chatbot_config.CHATBOT_TYPE == "Cohere":
    chatbot = CohereClient(api_key="<YOUR API KEY>")
elif chatbot_config.CHATBOT_TYPE == "HuggingFace":
    chatbot = HuggingFaceLLM(...)
else:
    raise ValueError(f"Unsupported chatbot type: {chatbot_config.CHATBOT_TYPE}")




def run_study_buddy():
    study_buddy = StudyBuddy()
    os.system('clear')
    print("Welcome to Study Buddy!\nWrite me a query and I will try my best to answer it.")
    print("Enter '/bye' to quit the program.")
    
    while True:
        query = input("> ")
        
        if query.lower() == '/bye':
            print("Thank you for using Study Buddy. Goodbye!")
            break
        
        # new_function call
        response = study_buddy.generate_response(query)
        print(response)



if __name__ == "__main__":
    run_study_buddy()
