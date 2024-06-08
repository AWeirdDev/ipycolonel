# ipycolonel <kbd>beta</kbd>

The IPython kernel alternative. Designed to be as lightweight as possible.
This project is still in beta, the ecosystem isn't yet complete.

```python
# tag: beta
from ipycolonel import Instance

instance = Instance()
print(instance.run("print('bob the building, hes a building!')"))
print(instance.run("import math;print('whats this', math.pi)"))
# { 'stdout': 'Hello, World!\n', 'stderr': '' }
```

***

(c) 2024 AWeirdDev
