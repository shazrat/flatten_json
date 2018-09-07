#!/usr/bin/python

""" Given a directory of flattened JSON files, reconstructs a single JSON file
    with proper data structure defined by: {parent_name}_{child_attribute_name}.
    
    TO DO:
        1. Some objects are not being placed in proper parent keys.
"""

import argparse
import json
import os


OUTPUT_DIR = './output'
# Hard-code for now
directory = './output'

def get_directory():
    # Reads the command line argument with flag '-f' to determine local filename
    # to process.
    parser = argparse.ArgumentParser(description='Required: Directory containing JSON files')
    parser.add_argument('--dir', required=True, help="Directory containing JSON files",
        action='store')
    args = vars(parser.parse_args())
    directory = args['--dir']
    return directory


def get_files_list():
    files = os.listdir(directory)
    filenames = []
    for i in files:
        filenames.append(i.replace('.json', ''))
    return filenames

# def get_parent_name(files_list):
#     for file in files_list:
#         if '_' not in file:
#             return file + 's'

def load_file(filename):
    with open(directory + '/' + filename + '.json') as f:
        file_data = f.read()
    json_data = json.loads(file_data)
    return json_data

def load_all_files(files_list):
    all_data = {}
    for file in files_list:
        all_data[file] = load_file(file)
    return all_data

def get_deepest_obj(files_list):
    max_depth = 0
    max_index = 0
    for idx, name in enumerate(files_list):
        depth = len(name.split('_'))
        if depth > max_depth:
            max_depth = depth
            max_index = idx
    return files_list[max_index]

def get_attribute_name(filename, data):
    attribute = filename.split('_')[-1]
    if len(data) > 1:
        attribute += 's'
    return attribute

def get_parent_filename(filename, remaining_keys):
    parent_filename = '_'.join(filename.split('_')[:-1])
    if parent_filename not in remaining_keys:
        parent_filename = get_parent_filename(parent_filename, remaining_keys)
    return parent_filename

def clean_obj(data):
    for idx, val in enumerate(data):
        if '__index' in data[idx]:
            del data[idx]['__index']
        del data[idx]['id']
    return data

def reconstruct_json(all_data):
    """
    1. Get full file list
    2. Load all files into all_data dict
    3. Get most deeply nested file, set as child
    4. Get attribute name (if file contains array > 1, append s)
    5. Get parent name (if exists)
    5. Add child's data to parent using attribute name as key
    6. Remove child from all_data dict
    7. Repeat until all_data contains single key
    """
    while len(all_data) > 1:
        remaining_keys = list(all_data.keys())
        child_key = get_deepest_obj(remaining_keys)
        print("current_file:", child_key)
        child_data = all_data[child_key]
        attribute_name = get_attribute_name(child_key, child_data)
        print("attribute name:", attribute_name)
        parent_key = get_parent_filename(child_key, remaining_keys)
        # Ensure a proper container is made for the parent key
        print("parent name:", parent_key)
        parent_data = all_data[parent_key]
        child_data = clean_obj(child_data)
        if len(parent_data) < len(child_data):
            parent_data[-1][attribute_name] = child_data
        else:
            for idx, val in enumerate(child_data):
                parent_data[idx][attribute_name] = val
        del all_data[child_key]
    
    parent_key = remaining_keys[0]
    new_parent_key = parent_key + 's'
    all_data[new_parent_key] = all_data.pop(parent_key)

    return all_data

def write_to_file(result):
    """ If output directory does not exist, create it.
        Iterate through `output` (dict), creating a new file for each key and
        dump JSON data.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    filename = list(result.keys())[0] + '_reconstructed' '.json'
    with open(OUTPUT_DIR + '/' + filename, 'w') as f:
        json.dump(result, f, indent=4)


def reconstruct_json_old(files_list, parent_name):
    """
    1. Get full file list
    2. Get most deeply nested file, set as current_file
    3. Get attribute name (if file contains array > 1, append s)
    4. Find parent file (if exists)
    5. Add current_file's data to parent file using attribute name as key
        Each object should be added to corresponding object index in parent file
    6. Remove current_file from full file list
    7. Repeat until full file list is empty
    """
    result[parent_name] = []
    for file in files_list:
        result[parent_name]
        json_data = load_file(file)
        attributes = file.replace('.json', '').split('_')
        print(attributes)
        # Number of attributes determines depth
        for depth in len(attributes):
            pass

        if len(json_data) == 1:
            # Don't change attribute key name. Just append each item
            pass
        else:
            # Add 's' to attribute key name
            pass
        if file == 'restaurant.json':
            print(json_data)
        for obj in json_data:
            for key, val in obj.items():
                result[parent_name]
        
    print(result)

def main():
    files_list = get_files_list()
    print("Files list:", files_list)
    all_data = load_all_files(files_list)
    # print(all_data)
    result = reconstruct_json(all_data)
    print(result)
    write_to_file(result)

if __name__ == '__main__':
    main()