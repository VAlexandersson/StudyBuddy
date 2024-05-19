from models.data_models import Query, Response
from view.study_buddy_ui import StudyBuddyUI

class CommandLineUI(StudyBuddyUI):
    def get_user_query(self) -> Query:
        """Gets the user's query from the command line."""
        text = input("> ")
        return Query(text=text)

    def display_response(self, response: Response):
        """Displays the response to the user on the command line."""
        print("\nResponse:", response.text)