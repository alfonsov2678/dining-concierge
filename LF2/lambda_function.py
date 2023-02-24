import json
import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import random
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
sqs = boto3.client('sqs')
REGION = 'us-east-1'
HOST = 'search-restaurants-bpghfelsc36anywkjxme7z5wsu.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'
def lambda_handler(event, context):
    
    # get the messages from the queue
    current_messages = sqs.receive_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/214763411219/DiningConciergeQueue", WaitTimeSeconds=20)
    
    # for each message run the recommendation algorithm
    try:
        for message in current_messages['Messages']:
            
            print(message)
            message_body = message['Body']
            message_body = message_body.replace("\'", "\"")
            message_body = json.loads(message_body)
            
            
            # query desired cuisine
            results = query(message_body['cuisine'])
        
            # randomly choose restaurant
            restaurant_chosen_one = random.choice(results)
            restaurant_chosen_two = random.choice(results)
            restaurant_chosen_three = random.choice(results)
            
            # query that restaurants info from DynamoDB
            restaurant_chosen_one_info = lookup_data({ 'BusinessID': restaurant_chosen_one['RestaurantID']})
            restaurant_chosen_two_info = lookup_data({ 'BusinessID': restaurant_chosen_two['RestaurantID']})
            restaurant_chosen_three_info = lookup_data({ 'BusinessID': restaurant_chosen_three['RestaurantID']})
            
            msg_sent = "Hello. Here are my {} restaurant recommendations for {} people for {} at {} in {}. 1. {} located at {}. 2. {} located at {}. 3. {} located at {}. Enjoy your meal!".format(message_body['cuisine'], message_body['partySize'], 
            message_body['time'], message_body['date'], message_body['location'], restaurant_chosen_one_info['Name'], ' '.join(restaurant_chosen_one_info['Address']), restaurant_chosen_two_info['Name'], 
            ' '.join(restaurant_chosen_two_info['Address']), restaurant_chosen_three_info['Name'], ' '.join(restaurant_chosen_three_info['Address']) )
            
            ses = boto3.client('ses')
            msg = ses.send_email(Source="alfonsolv3@gmail.com",Destination={
                'ToAddresses': [
                    'alfonsolv3@gmail.com',
                ]
            },
            Message={
                'Subject': {
                    'Data': 'Your Dining Concierge Recommendations',
                },
                'Body': {
                    'Text': {
                        'Data': msg_sent,
                    }
                }
            })
             
            results = [restaurant_chosen_two_info, restaurant_chosen_one_info, restaurant_chosen_three_info]

            
            # DELETE OUR MESSAGE FROM THE QUEUE AS IT HAS BEEN HANDLED
            current_messages = sqs.delete_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/214763411219/DiningConciergeQueue",
            ReceiptHandle=message['ReceiptHandle'])
    
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                },
                'body': json.dumps({'results': results})
            }
    except Exception as e: 
            print("exception")
            print(e)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                },
                'body': {}
            }
        
def lookup_data(key, db=None, table='yelp-restaurants'):
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
        
def query(term):
    q = {'size': 1000, 'query': {'multi_match': {'query': term}}}
    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
    res = client.search(index=INDEX, body=q)
    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])
    return results
def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)
                    
