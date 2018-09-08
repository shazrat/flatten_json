#!/usr/bin/python

""" Flattens any nested JSON object into individual JSON objects
    with one level of nesting.

    Author: Shiraz Hazrat (shiraz@shirazhazrat.com)

    Usage:
        $ python flatten_json.py -f nested_data_file.json

    Notes:
        1. Naming convention to preserve data structure is:
            {parent_name}_{child_attribute_name}.
        2. ID values are added to every new object.
        3. Index values are added for arrays containing more than one object.
        4. Arrays will have their parent name simple-singularized:
            (remove tailing 's')

    TO DO:
        1. Handle arrays of primatives better (ex. startups[screenshots][available_sizes])
"""

import argparse
import json
import os


OUTPUT_DIR = './output'


def get_filename():
    """ Reads the command line argument with flag '-f' to determine local
        filename to load and process."""
    parser = argparse.ArgumentParser(description='Required: json file')
    parser.add_argument('-f', required=True, help="Local json filename",
        action='store')
    args = vars(parser.parse_args())
    filename = args['f']
    return filename


def read_data(filename):
    """ Opens local file as a JSON object.
        Args:
            filename (string)

        Returns:
            json_data (dictionary)
    """
    with open(filename) as f:
        file_data = f.read()
    try:
        json_data = json.loads(file_data)
    except ValueError as e:
        print("Invalid JSON detected. Unable to load file:", filename, e)
        raise
    return json_data


def get_id(data):
    """ Iterates through object to find any key equal to 'id'.
        Required for setting 'id' value on all child objects.
        Needs to be determined prior to diving into any nested object.

        Requires:
            data (dict)

        Returns:
            value (string)
        """
    for key, value in data.items():
        if key == 'id':
            return value


def flatten(result, data, key="", index=0, filename="", id_value=None, set_index=False):
    """ Recursively go through each level of a JSON object, splitting each level
        and category into individual objects while preserving their data
        structure in the form of naming and index values.
        
        Args:
            data (*)
            key (string)
            index (int): Objects with nested arrays require index value
            filename (string): Handles naming convention of output file
            id_value (string): Added to all new objects
        
        Returns:
            result (dict): Contains each flattened JSON object as a new key.
    """
    if type(data) is dict:
        if id_value == None:
            id_value = get_id(data)
        
        for key, val in data.items():
            if type(val) is dict:
                if filename:
                    newfilename = filename + '_' + key
                else:
                    newfilename = key                   
                if len(val) > 1:
                    if newfilename not in result:
                        result[newfilename] = [{}]
                    else:
                        result[newfilename].append({})
                    if id_value != None:
                        result[newfilename][-1]['id'] = id_value
                    if set_index:
                        result[newfilename][index]['__index'] = str(index)
                flatten(result, val, key, index, newfilename, id_value, set_index)
                
            elif type(val) is list:
                if filename:
                    newfilename = filename + '_' + key[:-1]
                else:
                    newfilename = key[:-1]
                if newfilename not in result:
                    result[newfilename] = []
                flatten(result, val, key, index, newfilename, id_value, set_index)

            else:
                flatten(result, val, key, index, filename, id_value, set_index)

    elif type(data) is list:
        for index in range(len(data)):
            result[filename].append({})
            if id_value != None:
                result[filename][-1]['id'] = id_value
            if len(data) > 1:
                set_index = True
                result[filename][-1]['__index'] = str(index)
            flatten(result, data[index], "", index, filename, id_value, set_index)

    else:
        if not filename:    # Handle cases where top-level object is primative
            filename = 'output'
            result[filename] = [{}]

        result[filename][-1][key] = data
    
    return result


def clean(result):
    """ Iterate through all objects to find any that have no value.
        
        Criteria:
            1. Object has less than two items
            2. Object has only 2 keys: 'id' and '__index'

        Args:
            result (dict)

        Returns:
            result (dict)
    """
    for filename in list(result.keys()):
        check_array_length = False
        for obj in result[filename][:]:
            if len(obj) < 2 or obj.keys() == set(['id', '__index']):
                result[filename].remove(obj)
                check_array_length = True
        if check_array_length:
            if len(result[filename]) == 0:
                del result[filename]

    return result


def write_to_files(result):
    """ If output directory does not exist, create it.
        Iterate through `output` (dict), creating a new file for each key and
        dump JSON data.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    for key, data in result.items():
        filename = key + '.json'
        with open(OUTPUT_DIR + '/' + filename, 'w') as f:
            json.dump(data, f, indent=4)


def main():
    filename = get_filename()
    json_data = read_data(filename)
    result = flatten({}, json_data)
    output = clean(result)
    write_to_files(output)


if __name__ == '__main__':
    # Execute only if run as a script
    main()
