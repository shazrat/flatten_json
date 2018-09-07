#!/usr/bin/python

""" Reconstruct nested JSON file from flattened files.

    Author: Shiraz Hazrat (shiraz@shirazhazrat.com)

    Given a directory of flattened JSON files, reconstructs a single JSON file
    with proper data structure defined by: {parent_name}_{child_attribute_name}.
    
    TO DO:
        1. Some objects are not being placed in proper parent keys due to 
            attribute keys containing underscores.
"""

import argparse
import json
import os


def get_directory():
    """ Reads the command line argument with flag '-f' to determine local 
        filename to process.
    """
    parser = argparse.ArgumentParser(
        description='Required: Directory containing JSON files')
    parser.add_argument(
        '--dir', required=True, help="Directory containing JSON files",
        action='store')
    args = vars(parser.parse_args())
    directory = args['dir']
    if directory[-1] != '/':
        directory += '/'
    return directory


def get_files_list(directory):
    files = os.listdir(directory)
    filenames = []
    for i in files:
        filenames.append(i.replace('.json', ''))
    return filenames


def load_file(directory, filename):
    with open(directory + filename + '.json') as f:
        file_data = f.read()
    json_data = json.loads(file_data)
    return json_data


def load_all_files(directory, files_list):
    all_data = {}
    for file in files_list:
        all_data[file] = load_file(directory, file)
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
    """ TO DO: Incorrectly returns only last part of attribute names containing 
        underscores.
    """
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
        1. Get most deeply nested file, set as child
        2. Get attribute name
        3. Get parent name (if exists)
        4. Add child's data to parent using attribute name as key
        5. Remove child from all_data
        6. Repeat until all_data contains single key
    """
    while len(all_data) > 1:
        remaining_keys = list(all_data.keys())
        child_key = get_deepest_obj(remaining_keys)
        child_data = all_data[child_key]
        attribute_name = get_attribute_name(child_key, child_data)
        parent_key = get_parent_filename(child_key, remaining_keys)
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

def write_to_file(result, directory):
    """ Saves reconstructed JSON file to output directory.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = list(result.keys())[0] + '_reconstructed' '.json'
    with open(directory + filename, 'w') as f:
        json.dump(result, f, indent=4)


def main():
    directory = get_directory()
    files_list = get_files_list(directory)
    all_data = load_all_files(directory, files_list)
    result = reconstruct_json(all_data)
    write_to_file(result, directory)

if __name__ == '__main__':
    # Execute only if run as a script
    main()