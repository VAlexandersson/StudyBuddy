# main.py
import os
from study_buddy import StudyBuddy

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
        
        response = study_buddy.generate_response(query)
        print(response)

def main():
    run_study_buddy()

if __name__ == "__main__":
    main()