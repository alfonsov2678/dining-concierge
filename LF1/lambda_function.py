import json
import random
import decimal 
import boto3

sqs = boto3.client('sqs')
def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']
    
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None    

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}

def elicit_intent(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [ message ] if message != None else None,
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }



def DiningIntent(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    
    cuisine = get_slot(intent_request, 'cuisine')
    date = get_slot(intent_request, 'date')
    location = get_slot(intent_request, 'location')
    partySize = get_slot(intent_request, 'partySize')
    email = get_slot(intent_request, 'email')
    time = get_slot(intent_request, 'time')
    
    # Validate parameters
    if cuisine is None:
        text = "Thank you. Unfortunately, I can't find your chosen cuisine choice. Please input it again"
        fulfillment_state = "Fulfilled"    
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
        return close(intent_request, session_attributes, fulfillment_state, message)
    if date is None:
        text = "Thank you. Unfortunately, I forgot your chosen date. Please input it again"
        fulfillment_state = "Fulfilled"
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
        return close(intent_request, session_attributes, fulfillment_state, message)
    if location is None:
        text = "Thank you. Unfortunately, I forgot your chosen location. Please input it again"
        fulfillment_state = "Fulfilled"    
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
        return close(intent_request, session_attributes, fulfillment_state, message)
    if partySize is None:
        text = "Thank you. Unfortunately, I forgot your chosen party size. Please input it again"
        fulfillment_state = "Fulfilled"    
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
        return close(intent_request, session_attributes, fulfillment_state, message)
    if email is None:
        text = "Thank you. Unfortunately, I forgot your email. Please input it again"
        fulfillment_state = "Fulfilled"  
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
        return close(intent_request, session_attributes, fulfillment_state, message)
    if time is None:
        text = "Thank you. Unfortunately, I forgot your chosen time. Please input it again"
        fulfillment_state = "Fulfilled" 
        message =  {
            'contentType': 'PlainText',
            'content': text
        }
        return close(intent_request, session_attributes, fulfillment_state, message)


    # ADD TO THE SQS QUEUE
    
    messageBody = {
        'cuisine': cuisine,
        'date': date,
        'location': location,
        'partySize': partySize,
        'email': email,
        'time': time
    }
    
    message_json = json.dumps(messageBody, separators=(',', ':'))
    
    sqs.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/214763411219/DiningConciergeQueue",
        MessageBody=message_json
    )
    
    
    
    text = "You???re all set. Expect my suggestions shortly! Have a good day"
    message =  {
            'contentType': 'PlainText',
            'content': text
    }
    
    fulfillment_state = "Fulfilled"
    
    return close(intent_request, session_attributes, fulfillment_state, message)
    
def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningIntent':
        return DiningIntent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    response = dispatch(event)
    return response