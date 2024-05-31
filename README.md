# ipycolonel <kbd>beta</kbd>

The IPython kernel alternative. Designed to be as lightweight as possible.
This project is still in beta, the ecosystem isn't yet complete.

```python
# tag: beta
from ipycolonel import Instance

instance = Instance("print('Hello, World!')")
print(instance.run())
# { 'stdout': 'Hello, World!\n', 'stderr': '' }
```

## Environment

Create an environment in `ipycolonel-environment/`. This will be copied to new notebooks (`.ipycolonel/`).
