import requests

BASE_URL = "https://xivapi.com"


class Client:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fc_by_name(self, server: str, name: str) -> dict:
        """
        Makes an HTTP request to fetch JSON data of the FC identified by name
        :param server: server to search for FC
        :param name: name of the FC
        :return: dict containing the JSON response
        """
        request_url = f"{BASE_URL}/freecompany/search"
        params = dict(name=name, server=server, private_key=self.api_key)
        response = requests.get(request_url, params=params)
        response.raise_for_status()
        return response.json()

    def fc_by_id(self, fc_id: int, fc_members: bool = False) -> dict:
        """
        Makes an HTTP request to fetch JSON data of the inquired Lodestone ID's FC
        :param fc_id: int of Lodestone FC ID
        :param fc_members: if True, list of all the members will be returned
        :return: dict containing the JSON response
        """
        request_url = f"{BASE_URL}/freecompany/{fc_id}"
        params = dict(private_key=self.api_key, data="FCM" if fc_members else None)
        response = requests.get(request_url, params=params)
        response.raise_for_status()
        return response.json()
