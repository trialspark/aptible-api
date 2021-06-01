# aptible-api

Python client for api.aptible.com. Aptible's API is built on HAL+JASON so this
package includes a simplified engine for generating Resource types based on
JSON objects provided by the API / specifications in
[draft-kelly-json-hal-06](https://datatracker.ietf.org/doc/html/draft-kelly-json-hal-06)

## Installation

```shell
pip install aptible-api
```

## Usage

Fist create an instance of the API

```python
from aptible.api import AptibleApi

aptible_api = AptibleApi()
```

Then authorize the application via either account credentials or a token.

```python
# Via account credentials
aptible_api.authorize(email='user@example.com', password='password')

# Via a token
from pathlib import Path
from json import JSONDecoder

tokens_path = Path('~/.aptible/tokens.json')
tokens_json = JSONDecoder.decode(tokens_path.read_text())
token = tokens_json['https://auth.aptible.com']

aptible_api.authorize(token=token)
```

From here, you can interact with the API however you wish.

```python
accounts = aptible_api.accounts()
account = next(accounts)
account.handle
# >>> 'demo-account'

next(account.apps()).handle
# >>> 'foodle'

new_app = account.create_app(handle='foo-app')
new_app.href
# >>> 'https://api.aptible.com/apps/1337'
```

## Contributing

1. Fork the project.
2. Commit your changes, with tests.
3. Ensure that your code passes tests (`pipenv run py.test`) and meets pylint
   style guide (`pipenv run pylint`).
4. Create a new pull request on GitHub.

## Copyright

MIT License, see [LICENSE](LICENSE.md) for details.

Copyright (c) 2021 TrialSpark, Inc. and contributors.
