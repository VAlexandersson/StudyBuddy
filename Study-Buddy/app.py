# app.py
from view.command_line_ui import CommandLineUI
from study_buddy import StudyBuddy
import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
  study_buddy = StudyBuddy(CommandLineUI())
  study_buddy.run(logger)

if __name__ == "__main__":
  main()