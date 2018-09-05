#!/usr/bin/python

""" Flattens any nested JSON object into individual JSON objects
    with one level of nesting.

    Author: Shiraz Hazrat (shiraz@shirazhazrat.com)

    Usage:
        > python flatten_json.py -f nested_data_file.json

    TO DO: Find better way to handle many args when calling flatten
"""

import argparse
import json
import os

result = {}

def get_filename():
    # Reads the command line argument with flag '-f' to determine local filename
    # to process.
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
    json_data = json.loads(file_data)
    return json_data

def get_id(data):
    # Iterates through dictionary to find any key equal to 'id', and return that value
    for key, value in data.items():
        if key == 'id':
            return value

def flatten(data, key="", index=0, filename = "", id_value=None, set_index=False):
    """ Recursively go through each level of a JSON object, splitting each level and 
        category into individual objects while preserving their data structure in the
        form of naming and index values.
        
        Notes:
            1. Naming convention to preserve data structure is {parent_name}_{child_attribute_name}.
            2. ID values are added to every new object.
            3. Index values are added for arrays containing more than one object.
            4. Arrays will have their parent name simple-singularized (remove tailing 's')
            5. All sorted data is stored in `result` (dict), created outside this function.

        Args:
            data (*)
            key (string)
            index (int)
            filename (string)
            id_value (string)
        
        Returns:
            None
    """
    if type(data) is dict:
        # Handle dictionaries. Create new filename. Iterate through keys.
        # TO DO: Handle multiple ID values properly.
        if id_value == None:
            # Make sure it checks for new ID value in next top-level dict
            id_value = get_id(data)
        
        for key, val in data.items():
            if type(val) is dict:
                # Determine filename or set new one if one does not exist
                if not filename:
                    newfilename = key
                else:
                    newfilename = filename + '_' + key

                if len(val) > 1: # Prevents unnecessary containers from being created
                    if newfilename not in result:
                        result[newfilename] = [{}]
                    else:
                        result[newfilename].append({})
                    if id_value != None:
                        result[newfilename][-1]['id'] = id_value
                    if set_index:
                        result[newfilename][index]['__index'] = str(index)
                flatten(val, key, index, newfilename, id_value, set_index)
                
            elif type(val) is list:
                if not filename:
                    newfilename = key[:-1]
                else:
                    newfilename = filename + '_' + key[:-1]
                if newfilename not in result:
                    result[newfilename] = []
                flatten(val, key, index, newfilename, id_value, set_index)

            else:
                flatten(val, key, index, filename, id_value, set_index)

    elif type(data) is list:
        # Handle arrays (lists).
        # Create dictionary containers for each object of the array.
        # If array is larger than 1, set index values.
        # Set ID value in each container if ID value exists.
        for index in range(len(data)):
            result[filename].append({})
            if len(data) > 1:
                set_index = True
                result[filename][-1]['__index'] = str(index)
                # TO DO: Ensure this is only set to True for child executions and doesn't carry over
            if id_value != None:
                result[filename][-1]['id'] = id_value
                # result[filename][index]['id'] = id_value
            flatten(data[index], "", index, filename, id_value, set_index)

    else:
        # Handle primitive data types.
        if not filename:
            # Handle case where top-level item is primative
            filename = 'output'
            result[filename] = [{}]

        result[filename][-1][key] = data
        # result[filename][index][key] = data

    # print(result)

def clean(result):
    """ Iterate through all objects to find any that have no value.
        
        Criteria:
            1. Object does not have any keys apart from 'id' and '__index'

        Args:
            result (dict)

        Returns:
            output (dict)
    """
    for filename in list(result.keys()):
        # Iterate through 'result' to view contents of each individual output file
        check_array_length = False
        for obj in result[filename][:]:
            # Iterate through all objects to see if they have no valuable data
            if len(obj) < 2 or obj.keys() == set(['id', '__index']):
                result[filename].remove(obj)
                check_array_length = True
        if check_array_length:
            if len(result[filename]) == 0:
                del result[filename]

    return result

def write_to_files(result):
    # Create new dir called output and save all newly created files there.
    output_dir = './output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for key, data in result.items():
        filename = key + '.json'
        with open(output_dir + '/' + filename, 'w') as f:
            json.dump(data, f)

def main():
    filename = get_filename()
    json_data = read_data(filename)
    flatten(json_data)
    output = clean(result)
    write_to_files(output)

if __name__ == '__main__':
    # execute only if run as a script
    main()