import json
import boto3

client = boto3.client('lexv2-runtime')

def lambda_handler(event, context):
    # TODO implement
    
    msg_from_user = event['messages']
    messages_response = []

    for message in msg_from_user:
        
        if message['type'] == "unstructured" :
            response = client.recognize_text(
            botId='GLFLFNYSUK',
            botAliasId='TSTALIASID',
            localeId='en_US',
            sessionId='testuser',
            text=message['unstructured']['text'])
            
        else:
            response = client.recognize_text(
            botId='GLFLFNYSUK',
            botAliasId='TSTALIASID',
            localeId='en_US',
            sessionId='testuser',
            text=message['structured']['text'])

        msg_from_lex = response.get('messages', [])
        
        if msg_from_lex:
            

            resp_message = {
                'type': 'unstructured',
                'unstructured': {
                    'id': response['ResponseMetadata']['RequestId'],
                    'text': msg_from_lex[0]['content'],
                    'date': response['ResponseMetadata']['HTTPHeaders']['date']
                },
            }


            messages_response.append(resp_message)

    resp = {
        'statusCode': 200,
        'messages': messages_response
    }
    
    # modify resp to send back the next question Lex would ask from the user
            
    # format resp in a way that is understood by the frontend
    # HINT: refer to function insertMessage() in chat.js that you uploaded
    # to the S3 bucket
    return resp
    
