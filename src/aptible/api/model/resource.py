from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterator, List, Union

from inflection import pluralize, underscore

from ..error import UnknownEmbeddedResourceType


class ResourceMetaClass(type):

    @property
    def api_path(cls):
        return f"/{pluralize(underscore(cls.__name__))}/{{}}"


class Resource(metaclass=ResourceMetaClass):

    def __init__(self, **kwargs):
        self._manager = kwargs.setdefault('_manager', None)
        self._links = kwargs.setdefault('_links', {})
        self._embedded = kwargs.setdefault('_embedded', {})
        self._cache = {'embedded': {}}
        self._attrs = kwargs.copy()

        del self._attrs['_manager']
        del self._attrs['_links']
        del self._attrs['_embedded']

    def _inflate_embedded_resource(self, name: str) -> Union[Resource, List[Resource]]:
        embedded_cache = self._cache.get('embedded')
        if name in embedded_cache:
            return embedded_cache.get(name)

        raw_value = self._embedded.get(name)

        if isinstance(raw_value, dict):
            return embedded_cache.setdefault(name, self._manager._inflate_type(raw_value))

        if isinstance(raw_value, list):
            return embedded_cache.setdefault(name, [
                self._manager._inflate_type(value) for value in raw_value
            ])

        raise UnknownEmbeddedResourceType(
            f"Unknown embedded resource: {name} for type: {type(raw_value)}"
        )

    def __getattr__(self, name: str) -> Any:
        if name in self._attrs:
            if name == "_type":
                return self._manager._resource_class(self._attrs['_type'])

            if name[-3:] == "_at":
                return datetime.fromisoformat(self._attrs[name].replace('Z', '+00:00'))

            return self._attrs.get(name)

        if name in self._links:
            target_url = self._links[name]["href"]

            def _get_linked_resource(**kwargs) -> Union[Resource, Iterator[Resource]]:
                return self._manager.fetch(target_url, **kwargs)

            return _get_linked_resource

        if name in self._embedded:
            return self._inflate_embedded_resource(name)

        possible_link_key = name[:-3]
        if name[-3:] == "_id" and possible_link_key in self._links:
            link_url = self._links.get(possible_link_key).get("href")
            possible_id = link_url.split('/')[-1]
            if possible_id.isdigit():
                return int(possible_id)

        if name[:7] == "create_":
            possible_link_key = pluralize(name[7:]).lower()
            if possible_link_key in self._links:
                target_url = self._links.get(possible_link_key).get("href")

                def _create_linked_resource(**kwargs):
                    return self._manager.create(target_url, params=kwargs)

                return _create_linked_resource

        raise AttributeError(f"{type(self)} object has no attribute {name}")

    def to_dict(self) -> Dict:
        data = self._attrs.copy()
        data.update({'_links': self._links.copy(), '_embedded': self._embedded.copy()})
        return data

    @property
    def empty(self) -> bool:
        return False

    @property
    def api_path(self) -> str:
        return self._type.api_path


def ResourceClassFactory(name):
    def __init__(self, **kwargs):
        Resource.__init__(self, **kwargs)
    return type(name, (Resource, ), {"__init__": __init__})
