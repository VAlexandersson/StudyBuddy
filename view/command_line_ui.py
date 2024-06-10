from models.data_models import Query, Response
from view.user_interface import UserInterface

class CommandLineUI(UserInterface):
    def get_query(self) -> Query:
        """Gets the user's query from the command line."""
        text = input("> ")
        return Query(text=text)

    def post_response(self, response: Response):
        """Displays the response to the user on the command line."""
        print("\nResponse:", response.text)