import json
import boto3
import requests
from requests_aws4auth import AWS4Auth


# import AWS4Auth

region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, 'us-east-1', 'es', session_token=credentials.token)
searchPhotosLex = boto3.client('lex-runtime')
opensearchURL = "https://search-photos-uxu6px6tgt4pciyej5dr73yidi.us-east-1.es.amazonaws.com/"
headers = {"Content-Type": "application/json"}

def lambda_handler(event, context):
    print(event)
    searchQuery = event['q']
 
    response = searchPhotosLex.post_text(
        botName='photoBotNew',
        botAlias='photoBotAlias',
        userId="JON8XS9DNZ",
        inputText= searchQuery
    )
    labels = []
    query_words = searchQuery.split(" ")
    
    for word in query_words:
        labels.append(word)

    
    photos = []
    print("response from lex:")
    print(response)
    
    if 'slots' not in response:
        print('No photos found')
    else:
        #print("slot: ", response['slots'])
        slot_val = response['slots']
        for key, value in slot_val.items():
            if value != None:
                labels.append(value)
    
    print("Labels from lex:")
    print(labels)
    for label in labels:
     
        photoPath = opensearchURL + '/_search?q=labels:' + label
        response = requests.get(photoPath, headers=headers, auth=("master","Cloudcomputing!1"))
        print(response)
        
        responseLabels = json.loads(response.text)
        numberofLabels = responseLabels['hits']['total']['value']
        
        print("response labels:")
        print(responseLabels)
        
        if "hits" in responseLabels:
            if "hits" in responseLabels["hits"]:
                for hit in responseLabels["hits"]["hits"]:
                
                    photoBucket = hit["_source"]["bucket"]
                    print("photoBucket", photoBucket)
                    photoName = hit["_source"]["objectKey"]
                    print("photoName", photoName)
                    
                    # https://photosbucket02.s3.amazonaws.com/tmp.jpeg
                    photoURL = 'https://' + photoBucket + '.s3.amazonaws.com/' + photoName
                    photos.append(photoURL)

                
                
    
    return {
        'statusCode': 200,
        'body': {
            'photos': photos,
            'searchQuery': searchQuery,
            'labels': labels,
        },
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
