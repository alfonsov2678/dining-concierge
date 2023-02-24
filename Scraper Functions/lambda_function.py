import json
import boto3
import csv
from botocore.exceptions import ClientError
import pandas as pd
import datetime
def lambda_handler(event, context):
  
    # GET CSV FILE OF OUR SCRAPED RESTAURANSTS TO UPLOAD TO DYNAMODB
    s3 = boto3.client('s3')
    
    csvfile = s3.get_object(Bucket="dining-concierte", Key="final_scraping_data.csv")
    csvcontent = csvfile['Body'].read().decode("utf-8")
    csvreader = csv.reader(csvcontent.split('\n'))
    
    index = 0
    data = []

    for row in csvreader:
        # ensure we are not adding first row
        
        if index != 0:
            try:
                timestamp = int(datetime.datetime.utcnow().timestamp())
                row_changed = row[13]
                row_changed = row_changed.replace("\'", "\"")
                row_changed = row_changed.replace("None", "\"\"")
                addr = json.loads(row_changed)
                print(row)
                object = {
                    'BusinessID': row[1],
                    'Name': row[3],
                    'Address': addr['display_address'],
                    'Location': addr['city'],
                    'Coordinates':  row[11],
                    'NumberReviews':  row[7],
                    'Rating':  row[9],
                    'ZipCode': addr['zip_code'],
                    'Cuisine': row[17],
                    'insertedAtTimestamp': timestamp
                }
                
                print(object)
                data.append(object)
                
            except:
                print("oh no")
        index += 1
       
    insert_data(data)

    
    return
def insert_data(data_list, db=None, table='yelp-restaurants'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # overwrite if the same index is provided
    for data in data_list:
        print(data)
        response = table.put_item(Item=data)
    print('@insert_data: response', response)
    return response
    
def lookup_data(key, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        print(response['Item'])
        return response['Item']
def update_item(key, feature, db=None, table='6998Demo'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    # change student location
    response = table.update_item(
        Key=key,
        UpdateExpression="set #feature=:f",
        ExpressionAttributeValues={
            ':f': feature
        },
        ExpressionAttributeNames={
            "#feature": "from"
        },
        ReturnValues="UPDATED_NEW"
    )
    print(response)
    return response
def delete_item(key, db=None, table='yelp-restaurants'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)
    try:
        response = table.delete_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
    else:
        print(response)