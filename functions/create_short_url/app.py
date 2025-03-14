import boto3
import json
import os
import random
import string
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def generate_short_id(length=6):
    """Genera un ID casuale per l'URL breve"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_html_form():
    return """
    <html>
        <head><title>URL Shortener</title></head>
        <body>
            <h1>URL Shortener</h1>
            <form action="/Prod/shorten" method="get">
                <input type="url" name="url" placeholder="Inserisci l'URL da accorciare" size="50" required>
                <input type="submit" value="Accorcia">
            </form>
        </body>
    </html>
    """

def lambda_handler(event, context):
    # Se è una richiesta alla root, mostra il form
    if event.get('path') == '/':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': get_html_form()
        }

    # Gestisci sia GET che POST
    if event.get('httpMethod') == 'GET':
        original_url = event.get('queryStringParameters', {}).get('url', '')
    else:
        # Mantieni il vecchio comportamento POST
        request_body = json.loads(event.get('body', '{}'))
        original_url = request_body.get('url', '')
    
    if not original_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'URL non specificato'})
        }
    
    # Genera un ID breve
    short_id = generate_short_id()
    
    # Salva la mappatura nel DB
    table.put_item(
        Item={
            'short_id': short_id,
            'original_url': original_url,
            'created_at': int(datetime.now().timestamp())
        }
    )
    
    # URL del servizio
    api_endpoint = os.environ['API_ENDPOINT']
    short_url = f"{api_endpoint}/{short_id}"
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'shortUrl': short_url,
            'originalUrl': original_url
        })
    }