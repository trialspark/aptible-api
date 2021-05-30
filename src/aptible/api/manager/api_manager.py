from functools import singledispatchmethod
from typing import Dict, Iterator, List, Union
from urllib.parse import parse_qs, urlparse

import requests
from inflection import camelize, singularize
from requests.compat import urljoin

from .. import model
from ..error import UnknownResourceInflation
from ..model import Resource, ResourceClassFactory


class ApiManager:
    # pylint: disable=inconsistent-return-statements

    def __init__(self, api_base: str):
        self.api_uri_base = api_base
        self.api_base = self.fetch(self.api_uri_base)

    @property
    def request_headers(self) -> Dict:
        return {
            'Accepts': 'application/json',
            'Content-Type': 'application/json',
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

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        if 'headers' not in kwargs:
            kwargs['headers'] = dict()
        kwargs['headers'].update(self.request_headers)

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def _get(self, url: str, **kwargs) -> requests.Response:
        return self._request('get', url, **kwargs)

    def _post(self, url: str, **kwargs) -> requests.Response:
        return self._request('post', url, **kwargs)

    def _response_request_headers(self, response: requests.Response) -> Dict[str, str]:
        return response.request.headers

    def _parse_url_params(self, url: str) -> Dict[str, Union[str, List[str]]]:
        parse_result = urlparse(url)
        query_params = parse_qs(parse_result.query, keep_blank_values=True)

        # Flatten query_params values
        return {
            key: value if len(value) > 1 else value[0]
            for key, value in query_params.items()
        }

    def _response_request_params(self, response: requests.Response) -> Dict[str, Union[str, List[str]]]:
        request_url = response.request.url
        return self._parse_url_params(request_url)

    def _inflate_type(self, resource_data: Dict) -> Resource:
        resource_type = resource_data["_type"]
        klass = self._resource_class(resource_type)
        return klass(_manager=self, **resource_data)

    def _inflate_generator(self, response: requests.Response) -> Iterator[Resource]:
        resource_data = response.json()

        for value in resource_data["_embedded"].values():
            for data in value:
                yield self._inflate_type(data)

        if "next" in resource_data["_links"]:
            headers = self._response_request_headers(response)
            params = self._response_request_params(response)

            next_url = resource_data["_links"]["next"]["href"]
            next_params = self._parse_url_params(next_url)

            params.update(next_params)

            next_response = self._get(next_url, headers=headers, params=params)
            yield from self._inflate_generator(next_response)

    def _inflate(self, response: requests.Response) -> Union[Resource, Iterator[Resource]]:
        resource_data = response.json()

        # Single resource
        if "_type" in resource_data:
            return self._inflate_type(resource_data)

        # List of resources
        if "_embedded" in resource_data:
            return self._inflate_generator(response)

        # Fallback for API base
        if "_links" in resource_data:
            return Resource(_manager=self, **resource_data)

        raise UnknownResourceInflation(f"Attempt to inflate resource data failed: {resource_data}")

    @singledispatchmethod
    def fetch(self, *args, **kwargs) -> Union[Resource, Iterator[Resource]]:
        raise NotImplementedError()

    @fetch.register
    def _(self, url: str, **kwargs) -> Union[Resource, Iterator[Resource]]:
        kwargs = kwargs if 'params' in kwargs else {'params': kwargs}
        response = self._get(url, **kwargs)
        return self._inflate(response)

    @fetch.register
    def _(self, klass: type, resource_id: int, **kwargs) -> Union[Resource, Iterator[Resource]]:
        target_url_template = urljoin(self.api_base, klass.api_path)
        target_url = target_url_template.format(resource_id)
        return self.fetch(target_url, **kwargs)

    def create(self, url: str, **kwargs) -> Union[Resource, Iterator[Resource]]:
        kwargs = kwargs if 'data' in kwargs else {'data': kwargs}
        response = self._post(url, **kwargs)
        return self._inflate(response)

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
