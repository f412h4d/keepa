import os
import json

# mongodb
from pymongo import MongoClient

ROOT_CATEGORY = '12312312312'
DIR_PATH = './products'
ERRORS_FILE = 'errors.txt'


def get_json_files(path):
    return [f for f in os.listdir(path) if f.endswith('.json')]


def get_product_info(asin):
    print(f'ASIN: {asin}\n')
    with open(f'{DIR_PATH}/{asin}', 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {asin}: {str(e)}")
            return None

    product = data["products"][0]
    product['fetch_category'] = ROOT_CATEGORY

    return product


def save_to_db(product_obj):
    if product_obj is None:
        return  # Skip processing if the product object is None (error decoding JSON)

    client = MongoClient(
        'mongodb://capsmark:Cap.CAP_Online.ADSDJKHbqwg__ivqiy2.1sdf23.r329p.8iuhs_djklh@10.206.0.3:27017/?authMechanism=DEFAULT')

    db = client['keepa']
    collection = db['products']
    collection.create_index([("asin", 1)], unique=True)

    try:
        # Try to insert the document
        result = collection.insert_one(product_obj)
        print(f"Inserted document ID: {result.inserted_id}")

    except Exception as e:
        # Handle the case where a duplicate key error occurs
        if 'E11000' in str(e):
            print(f"Duplicate key error: ASIN {product_obj['asin']} already exists in the database.")
        else:
            print(f"Error inserting document: {str(e)}")
            # Save the filename to the errors file
            with open(ERRORS_FILE, 'a') as errors_file:
                errors_file.write(f"Error processing file: {product_obj['asin']}.json\n")


json_files_list = get_json_files(DIR_PATH)

print(f" {len(json_files_list)} JSON files in the specified directory.\n")

for json_file in json_files_list:
    print(json_file)
    product = get_product_info(json_file)

    save_to_db(product)
