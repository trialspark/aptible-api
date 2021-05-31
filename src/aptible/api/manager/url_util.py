from typing import Dict, List, Union
from requests import Response
from urllib.parse import parse_qs, urlparse


def response_request_headers(response: Response) -> Dict[str, str]:
    return response.request.headers


def parse_url_params(url: str) -> Dict[str, Union[str, List[str]]]:
    parse_result = urlparse(url)
    query_params = parse_qs(parse_result.query, keep_blank_values=True)

    # Flatten query_params values
    return {
        key: value if len(value) > 1 else value[0]
        for key, value in query_params.items()
    }


def response_request_params(response: Response) -> Dict[str, Union[str, List[str]]]:
    request_url = response.request.url
    return parse_url_params(request_url)
