## Example

```python
from pathlib import Path
token_path = Path("~/.aptible/tokens.json").expanduser()

from json import JSONDecoder
token_json = JSONDecoder().decode( token_path.read_text() )
token = token_json['https://auth.aptible.com']

from aptible.api import AptibleApi
aptible_api = AptibleApi()
aptible_api.authorize(token=token)

from aptible.api.model.app import App
app = aptible_api.fetch(App, 15514)
# or app = aptibe_api.fetch('App', 15514)

operation = app.create_operation(type='configure', env={"new_key": "value"})

print(operation.to_dict())
```
