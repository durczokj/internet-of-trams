import requests

class UnexpectedZtmResponseError(Exception):
    def __init__(self, response_text):
        self.response_text = response_text
        super().__init__(f"Unexpected ZTM Response: {response_text}")

class DataRetrievalError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message
        super().__init__(f"Data Retrieval Error: {error_message}")

class ZtmConnector:
    def __init__(self, api_key: str):
        self.__api_key = api_key
        
    def get(self, url, params=None):
        if params is None:
            params = {"apikey": self.__api_key}
        else:
            params["apikey"] = self.__api_key
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            response_dict = response.json()
            if response_dict["result"] == "false":
                error_message = response_dict.get("error", "Unknown error occurred.")
                raise DataRetrievalError(error_message)
            else:
                if response_dict["result"] == "Błędna metoda lub parametry wywołania":
                    raise DataRetrievalError(response_dict)
                else:
                    return response_dict["result"]
        else:
            raise UnexpectedZtmResponseError(response.text)