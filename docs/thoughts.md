# Thoughts

Don't where to put these things so I just open a new markdown file to store it.

## Get relative path to a pytest test file

Cannot find any resources or any guide about make the test script to load text file relative to itself.

The setup: Test scripts in `tests/`, want it to load things further like `test_data/...` so the fullpath is `tests/test_data/...`

 I guess everyone just run from top-level and paths relative to top level instead? (`tests/test_data/...`)

This is the thing I tried.

```python
# Inside conftest.py
def get_test_file_full_path(request, rel_path):
    # ugly hack on PATH problem
    # Get hints from https://stackoverflow.com/questions/50815777/parametrize-the-test-based-on-the-list-test-data-from-a-json-file
    # Tried these:
    # request.node.fspath.strpath   - "/full/path/to/tests/conftest.py"
    # request.node.fspath.dirpath() - /full/path/to/tests , without the closing '/'
    # Strangely enough I cannot use request.node.fspath.dirpath() + "/" to form the path. The '/' will be removed
    # But it works for str(request.node.fspath.dirpath()) + "/"
    dir_full_path = str(request.node.fspath.dirpath()) + "/"
    return dir_full_path + rel_path

```
