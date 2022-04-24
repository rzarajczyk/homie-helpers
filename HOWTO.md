# Build (Windows)
```shell
# py -m pip install --upgrade build
py -m build
 ```

# Install (Windows)
```shell
 py -m pip install C:\<path>\homie-helpers\dist\homie_helpers-<version>-py3-none-any.whl --force-reinstall
```

# Upload test (Windows)
```shell
# py -m pip install --upgrade tw
```

# Upload prod (Windows)
```shell
# py -m pip install --upgrade twine
py -m twine upload dist/*
```
