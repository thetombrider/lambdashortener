import boto3
import json
import os
import random
import string
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def generate_short_id(length=6):
    """Genera un ID casuale per l'URL breve"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_html_form():
    return """
    <html>
        <head>
            <title>URL Shortener</title>
            <!-- Google Fonts link for Inter font -->
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: black;
                    color: white;
                    font-family: 'Inter', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                h1 {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .form-container {
                    background-color: #333;
                    padding: 20px;
                    border-radius: 8px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    width: 350px;
                    transition: 0.3s ease-in-out;
                }
                .form-container:hover {
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }
                input[type="url"], input[type="submit"] {
                    padding: 12px;
                    margin: 8px;
                    width: 100%;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                }
                input[type="url"] {
                    background-color: #555;
                    color: white;
                    margin-bottom: 16px;
                }
                input[type="submit"] {
                    background-color: #4CAF50;
                    color: white;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #45a049;
                }
                a {
                    color: #4CAF50;
                    text-decoration: none;
                    font-size: 18px;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="form-container">
                <h1>URL Shortener</h1>
                <form action="/shorten" method="get">
                    <input type="url" name="url" placeholder="Insert URL to shorten" size="50" required>
                    <input type="submit" value="Shorten">
                </form>
            </div>
        </body>
    </html>
    """



def lambda_handler(event, context):
    try:
        # Check if the request path is the root and show the HTML form
        if event.get('path') == '/':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': get_html_form()
            }

        # Handle the GET request for /shorten
        if event.get('httpMethod') == 'GET':
            original_url = event.get('queryStringParameters', {}).get('url', '')
        else:
            # If POST is used (as a fallback), get the URL from the body
            request_body = json.loads(event.get('body', '{}'))
            original_url = request_body.get('url', '')

        if not original_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'URL non specificato'})
            }

        # Generate short ID
        short_id = generate_short_id()

        # Save the mapping to DynamoDB with error handling
        try:
            table.put_item(
                Item={
                    'short_id': short_id,
                    'original_url': original_url,
                    'created_at': int(datetime.now().timestamp())
                }
            )
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Failed to save URL in DynamoDB', 'message': str(e)})
            }

        # API endpoint and short URL creation
        api_endpoint = "https://shortener.thetombrider.xyz"
        short_url = f"{api_endpoint}/{short_id}"

        # Simplified HTML response (to check if rendering is causing issues)
        html_response = f"""
            <html>
                <head>
                    <title>URL Shortener - Shortened URL</title>
                    <!-- Google Fonts link for Inter font -->
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
                    <style>
                        body {{
                            background-color: black;
                            color: white;
                            font-family: 'Inter', sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                        }}
                        h1 {{
                            text-align: center;
                        }}
                        .result-container {{
                            background-color: #333;
                            padding: 20px;
                            border-radius: 8px;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            width: 300px;
                        }}
                        a {{
                            color: #4CAF50;
                            text-decoration: none;
                            font-size: 18px;
                        }}
                        a:hover {{
                            text-decoration: underline;
                        }}
                        p {{
                            font-size: 18px;
                            text-align: center;
                        }}
                        .short-url {{
                            margin-top: 10px;
                            background-color: #555;
                            padding: 10px;
                            border-radius: 4px;
                            width: 100%;
                            text-align: center;
                        }}
                    </style>
                </head>
                <body>
                    <div class="result-container">
                        <h1>URL Shortened Successfully!</h1>
                        <p>Here is your shortened URL:</p>
                        <div class="short-url">
                            <a href="{short_url}" target="_blank">{short_url}</a>
                        </div>
                        <p><a href="/">Shorten another URL</a></p>
                    </div>
                </body>
            </html>
            """

    

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_response
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'message': str(e)})
        }
