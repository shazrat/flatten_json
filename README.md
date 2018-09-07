# flatten_json

Given a deeply nested JSON object, this script splits it up into individual JSON objects with one level of nesting. The child objects are created such that the original JSON can be reconstructed.

## Naming convention

Child objects have the following naming convention:
{parent_name}_{child_attribute_name}

## Usage
```
$ python flatten_json.py -f json_file.json
```

Output files are saved to './output/*'

Notes:

1. ID values are added to every new object.
2. Index values are added for arrays containing more than one object.
3. Arrays will have their parent attribute name simple-singularized:
    (remove tailing 's')

## Reconstructing original JSON
```
$ python reconstruct_json.py --dir ./output
```
Notes:

1. Does not work correctly with files whose attribute names contain underscores.

Cheers.