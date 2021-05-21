import json
import zipfile


def read_json_data(zip_filename, target_filename):
    with zipfile.ZipFile(str(zip_filename), 'r') as zip_file:
        return json.loads(zip_file.read(target_filename).decode('utf-8'))


def read_binary_file(zip_filename, target_filename):
    with zipfile.ZipFile(str(zip_filename), 'r') as zip_file:
        return zip_file.read(target_filename)
