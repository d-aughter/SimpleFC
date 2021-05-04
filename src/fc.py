from re import sub
from collections import namedtuple, OrderedDict
from src.client import Client
from typing import Union, List


class FreeCompany:
    def __new__(cls, identifier: Union[List[str], int], client: Client):
        """
        Overrides __new__. Once called, FreeCompany object gets "converted" into a namedtuple object.
        This works as a constructor which hijacks all the parameters to create another, completely unrelated object.
        :param identifier: either a list with [server, FC name] or int with Lodestone ID of FC
        :param client: src.client.Client object
        """
        cls.client = client
        if isinstance(identifier, list):
            cls.id = cls._fetch_fc_id(identifier=identifier, client=cls.client)
        else:
            cls.id = identifier
        cls.fc_data = cls._fetch_fc_data(fc_id=cls.id, client=cls.client)
        free_company = cls._dict_to_namedtuple(data=cls.fc_data, name="FreeCompany")
        return free_company

    @classmethod
    def _fetch_fc_id(cls, identifier: List[str], client: Client) -> int:
        """
        Class method to fetch FC's Lodestone ID
        :param identifier: a list with [server, FC name]
        :param client: src.client.Client object
        :return: Lodestone ID of FC as int
        """
        fc = client.fc_by_name(server=identifier[0], name=identifier[1])
        return fc.get("Results")[0].get("ID")

    @classmethod
    def _fetch_fc_data(cls, fc_id: int, client: Client):
        """
        Class method to fetch FC's data
        :param fc_id: int of fc_id either known or fetched by FreeCompany._fetch_fc_id
        :param client: src.client.Client object
        :return: JSON response returned by making an HTTP request with correct params
        """
        return client.fc_by_id(fc_id=fc_id, fc_members=True)

    @classmethod
    def _dict_to_namedtuple(cls, data: dict, name: str, previous_name: str = ""):
        """
        Class method to generate a namedtuple object based on the provided dictionary
        This does all the heavy lifting for FreeCompany class
        Essentially converts dict into namedtuple, even recursively. Any other data types are left alone
        :param data: dict containing the initial data
        :param name: typename for namedtuple object. This identifies the object by giving it a "unique" name
        :param previous_name: typename to keep track when going recursive.
        :return: ideally, in the end, a namedtuple object with all the data in it
        """
        if isinstance(data, dict):
            # snake_case so invoking the param is easier
            # ex)
            # fc.free_company.active_member_count, is better than
            # fc.FreeCompany.ActiveMemberCount
            data = {cls._pascal_to_snake(k): v for k, v in data.items()}
            fields = data.keys()
            namedtuple_type = namedtuple(
                typename=name,
                field_names=data.keys(),
                rename=True,
            )
            field_value_pairs = OrderedDict(
                (
                    str(field),
                    cls._dict_to_namedtuple(
                        data=data[field],
                        name=cls._snake_to_pascal(field),
                        previous_name=cls._snake_to_pascal(field),
                    ),
                )
                for field in fields
            )
            try:
                return namedtuple_type(**field_value_pairs)
            except TypeError:
                return dict(**field_value_pairs)
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # if data is a list of dicts
            return [
                cls._dict_to_namedtuple(data=item, name=previous_name) for item in data
            ]
        else:
            return data

    @staticmethod
    def _pascal_to_snake(pascal: str) -> str:
        """
        Helper method to go from PascalCase to snake_case
        :param pascal: str of the PascalCaseString
        :return: snake_case version of pascal
        """
        name = sub("(.)([A-Z][a-z]+)", r"\1_\2", pascal)
        return sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    @staticmethod
    def _snake_to_pascal(snake: str) -> str:
        """
        Helper method to go from snake_case to PascalCase
        :param snake: str of the snake_case_string
        :return: PascalCase version of snake
        """
        return "".join([word.title() for word in snake.split("_")])
