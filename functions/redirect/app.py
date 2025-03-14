import boto3
import json
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    # Estrai l'ID breve dal percorso
    short_id = event['pathParameters']['shortId']
    
    # Cerca nel database
    response = table.get_item(
        Key={
            'short_id': short_id
        }
    )
    
    # Verifica se l'URL è stato trovato
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'URL non trovato'})
        }
    
    # Redireziona all'URL originale
    original_url = response['Item']['original_url']
    
    return {
        'statusCode': 301,
        'headers': {
            'Location': original_url
        },
        'body': ''
    }