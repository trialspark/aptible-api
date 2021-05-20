from __future__ import annotations

from inflection import pluralize, underscore
from typing import Dict, Union, Iterator, Any
from datetime import datetime


class ResourceMetaClass(type):

    @property
    def api_path(cls):
        return f"/{pluralize(underscore(cls.__name__))}/{{}}"


class Resource(metaclass=ResourceMetaClass):

    def __init__(self, **kwargs):
        self._links = kwargs.setdefault('_links', {})
        self._embedded = kwargs.setdefault('_embedded', {})
        self._cache = {'embedded': {}}
        self._attrs = kwargs.copy()

        del self._attrs['_links']
        del self._attrs['_embedded']

    def _get_linked_resource(self, key: str) -> Union[Resource, Iterator[Resource]]:
        if key not in self._links:
            return None
        return self.manager.fetch(self._links[key]["href"])

    def _get_embedded_resources(self, key: str) -> Union[Resource, Iterator[Resource]]:
        if key not in self._embedded:
            return None

        embedded_cache = self._cache.get('embedded')
        if key in embedded_cache:
            return embedded_cache.get(key)

        return embedded_cache.setdefault(key, self.manager.inflate(self._embedded.get(key)))

    def __getattr__(self, name: str) -> Any:
        if name in self._attrs:
            if name == "_type":
                _type = self._attrs[name]
                if "manager" in self._attrs:
                    return self._attrs["manager"]._resource_class(_type)
                return _type

            if name[-3:] == "_at":
                return datetime.fromisoformat(self._attrs[name].replace('Z', '+00:00'))

            return self._attrs.get(name)

        if name in self._links:
            return self._get_linked_resource(name)

        if name in self._embedded:
            return self._get_embedded_resources(name)

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
                    return self.manager.create(target_url, params=kwargs)

                return _create_linked_resource

        raise AttributeError(f"{type(self)} object has no attribute {name}")

    def to_dict(self) -> Dict:
        data = self._attrs.copy()
        data.update({'_links': self._links.copy(), '_embedded': self._embedded.copy()})
        del data['manager']
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
