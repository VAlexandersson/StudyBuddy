from models.data_models import Query, Response
from view.base_ui import BaseUI

class CommandLineUI(BaseUI):
    def get_query(self) -> Query:
        """Gets the user's query from the command line."""
        text = input("> ")
        return Query(text=text)

    def post_response(self, response: Response):
        """Displays the response to the user on the command line."""
        print("\nResponse:", response.text)