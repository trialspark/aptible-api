import requests

from functools import singledispatchmethod
from requests.compat import urljoin
from typing import Dict, Union, Iterator
from inflection import camelize, singularize

from .empty_response import EmptyResponse
from .. import model
from ..model import Resource, EmptyResource, ResourceClassFactory


class AptibleApi:
    # pylint: disable=inconsistent-return-statements

    def __init__(self, auth_token: str, uri_base="https://api.aptible.com"):
        self.auth_token = auth_token
        self.uri_base = uri_base
        self.api_base = self.fetch(self.uri_base)

    @property
    def request_headers(self) -> Dict:
        return {
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}',
        }

    def _resource_class(self, name: str):
        class_name = singularize(camelize(name))

        klass = None
        try:
            klass = getattr(model, class_name)
        except AttributeError:
            klass = ResourceClassFactory(class_name)
            setattr(model, class_name, klass)

        return klass

    def __getattr__(self, name):
        if name[:6] == "fetch_":
            klass = self._resource_class(name[6:])

            def _typed_fetch(resource_id: int, **kwargs):
                return self.fetch(klass, resource_id, **kwargs)

            return _typed_fetch

        # Delegate attrs to api_base
        try:
            delegated_attr_val = getattr(self.api_base, name)
        except AttributeError:
            # Clean up error messaging to AttributeError comes from this class
            raise AttributeError(f"{type(self)} object has no attribute {name}")

        return delegated_attr_val

    def _get(self, url: str) -> Union[EmptyResponse, requests.Response]:
        response = requests.get(url, headers=self.request_headers)

        if response.ok:
            return response

        return EmptyResponse()

    def _post(self, url: str, params: Dict) -> Union[EmptyResponse, requests.Response]:
        response = requests.post(url, headers=self.request_headers, json=params)

        if response.ok:
            return response

        return EmptyResponse()

    def _inflate_generator(self, resource_data: Dict) -> Iterator[Resource]:
        for value in resource_data["_embedded"].values():
            for data in value:
                yield self.inflate(data)

        if "next" in resource_data["_links"]:
            yield from self.fetch(resource_data["_links"]["next"]["href"])

    def inflate(self, resource_data: Dict) -> Union[EmptyResource, Resource, Iterator[Resource]]:
        resource_data.update({"manager": self})

        # Single resource
        if "_type" in resource_data:
            resource_type = resource_data["_type"]
            klass = self._resource_class(resource_type)
            return klass(**resource_data)

        # List of resources
        if "_embedded" in resource_data:
            return self._inflate_generator(resource_data)

        # Fallback for API base
        if "_links" in resource_data:
            return Resource(**resource_data)

        return EmptyResource(manager=self)

    @singledispatchmethod
    def fetch(self, *args, **kwargs) -> Union[EmptyResource, Resource, Iterator[Resource]]:
        raise NotImplementedError()

    @fetch.register
    def _(self, klass: type, resource_id: int) -> Union[EmptyResource, Resource, Iterator[Resource]]:
        target_url = urljoin(self.uri_base, klass.api_path)
        return self.fetch(target_url.format(resource_id))

    @fetch.register
    def _(self, url: str) -> Union[EmptyResource, Resource, Iterator[Resource]]:
        response = self._get(url)
        response_data = response.json()
        return self.inflate(response_data)

    @singledispatchmethod
    def create(self, *args, **kwargs) -> Union[EmptyResource, Resource, Iterator[Resource]]:
        raise NotImplementedError()

    @create.register
    def _(self, url: str, **kwargs) -> Union[EmptyResource, Resource, Iterator[Resource]]:
        return self.create(url, params=kwargs)

    @create.register
    def _(self, url: str, params: Dict) -> Union[EmptyResource, Resource, Iterator[Resource]]:
        response = self._post(url, params)
        response_data = response.json()
        return self.inflate(response_data)
