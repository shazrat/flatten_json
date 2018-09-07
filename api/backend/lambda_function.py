""" Flattens any nested JSON object into individual JSON objects
    with one level of nesting.

    Author: Shiraz Hazrat (shiraz@shirazhazrat.com)

    Usage:
        JSON data can be provided in 2 ways:
            1. URL to JSON file
            2. Upload JSON file

    Notes:
        1. Naming convention to preserve data structure is:
            {parent_name}_{child_attribute_name}.
        2. ID values are added to every new object.
        3. Index values are added for arrays containing more than one object.
        4. Arrays will have their parent name simple-singularized:
            (remove tailing 's')
"""

import argparse
import json
import os
import urllib.request
import boto3
import zipfile
import shutil
import time


OUTPUT_BASE_PATH = '/tmp/output/'
S3_BASE_PATH = 'https://s3-us-west-1.amazonaws.com/datacoral-challenge/output/'


def parse_request_for_url(event):
    url = ""
    try:
        if 'dev' in event:
            request_body = event['body']
        else:
            request_body = json.loads(event['body'])
        if 'json_url' in request_body:
            url = str(request_body['json_url'])
    except Exception as e:
        err = "Unable to load URL, bad JSON in POST request: {}".format(e)
        err += str(event['body'])
        return (None, err)
    return (url, None)


def download_json_from_url(url):
    err = ""
    try:
        with urllib.request.urlopen(url) as f:
            json_data = json.loads(f.read().decode())
    except:
        return False
    return json_data


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
        print("Invalid JSON detected. Unable to load file:", filename)
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
            None
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


def write_to_files(result, output_dir):
    """ If output directory does not exist, create it.
        Iterate through `output` (dict), creating a new file for each key and
        dump JSON data.
    """
    files_list = []
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for key, data in result.items():
        filename = key + '.json'
        files_list.append(filename)
        with open(output_dir + '/' + filename, 'w') as f:
            json.dump(data, f, indent=4)

    shutil.make_archive('/tmp/flattened', 'zip', output_dir)
    return files_list


def save_to_s3(ID):
    output_dir = '/tmp/output/' + str(ID) + '/'
    s3_local_path = 'output/' + str(ID) + '/'
    s3 = boto3.resource('s3')
    files_list = os.listdir(output_dir)
    args = {'ACL': 'public-read', 'ContentType': 'application/json'}
    for file in files_list:
        local_path = output_dir + file
        s3.Bucket('datacoral-challenge').upload_file(local_path, s3_local_path + file,
            ExtraArgs=args)
    args = {'ACL': 'public-read', 'ContentType': 'application/zip'}
    s3.Bucket('datacoral-challenge').upload_file('/tmp/flattened.zip', s3_local_path + 'flattened.zip',
            ExtraArgs=args)


def generate_html(output_dir, s3_path):
    files_list = os.listdir(output_dir)
    html = '<head><title>Summary</title></head><body>'\
            '<h2>Summary</h2><p>{summary}</p></body>'
    summary = 'Your flattened JSON files can be downloaded from the following links:<br /><br />'
    for file in files_list:
        url_path = s3_path + file
        summary += '<a href="{url_path}" target="_blank">{url_path}</a><br />'.format(url_path = url_path)
    zip_path = s3_path + 'flattened.zip'
    summary += '<br /> All files (zip):<br />' \
        '<a href="{url_path}" target="_blank">{url_path}</a>'.format(url_path = zip_path)
    html = html.format(summary = summary)
    return html


def generate_response(body):
    return {
        'statusCode': '200',
        'body': body,
        'headers': {
            'Content-Type': 'text/html',
            "Access-Control-Allow-Origin" : "*"
        }
    }


def lambda_handler(event, context):
    ID = int(time.time())
    output_dir = OUTPUT_BASE_PATH + str(ID) + '/'
    s3_path = S3_BASE_PATH + str(ID) + '/'
    url = ""
    
    if event['httpMethod'] == 'GET':
        html = "Hello! This was not a POST request! Goodbye!"
    elif event['httpMethod'] == 'POST':
        if event['body']:
            url, err = parse_request_for_url(event)
            if err:
                html = err
        else:
            html = "Looks like there was no data sent in with POST request."

    if url:
        json_data = download_json_from_url(url)
    else:
        if 'dev' in event:
            json_data = event['body']
        else:
            try:
                json_data = json.loads(event['body'])
            except Exception as e:
                json_data = False
    if json_data:
        result = flatten({}, json_data)
        output = clean(result)
        files_list = write_to_files(output, output_dir)
        save_to_s3(ID)
        html = generate_html(output_dir, s3_path)
    else:
        html = "Valid JSON data was not provided."
    response = generate_response(html)
    return response
