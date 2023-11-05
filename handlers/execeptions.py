
import logging


class AlgoliaAPIError(Exception):
    "Raised when the call to AlgoliaAPI return an status code different from 200"
    def __init__(self, status_code, message="Error while fetching the games."):
        self.status_code = status_code
        self.message = message
        logging.error(f' Error while calling the AlgoliaAPI: {str(status_code)}')
        super().__init__(self.message)

class PriceAPIError(Exception):
    def __init__(self, status_code, message="Error while calculating the game prices."):
        self.status_code = status_code
        self.message = message
        logging.error(f' Error while calling the PriceAPI: {str(status_code)}')
        super().__init__(self.message) 

class GoogleAPIError(Exception):
    def __init__(self, status_code, message='Error while calling Google Sheets API.'):
        self.status_code = status_code
        self.message = message
        logging.error(f' Error while calling the Google Sheets API: {str(status_code)}')
        super().__init__(self.message)