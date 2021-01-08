import re
from bs4 import BeautifulSoup, ResultSet,element as Element
import json
import boto3

s3 = boto3.resource('s3')

def convertToHtml(json, element):
    element += '<' + json['name']
    if hasattr(json, 'attributes'):
        for attr in json['attributes']:
            element += " " + attr + '="' +  json['attributes'][attr] + '"'
    element += '>' + json['text']
    if len(json['child_components']) > 0:
        for child in json['child_components']:
            element = convertToHtml(child, element)
    element += '</'+ json['name'] + ">"
    return element

def lambda_handler(event, context):
    try:
        bucket = event['bucket']
        html_filter = event['html_filter']
        updatedPages = []
        
        for page in event['pages']:
            file_path = page['path']
            components = page['components']
            sComponents = []
            for component in components:
                sComponent = convertToHtml(component, '')
                sComponents.append(sComponent)
            
            obj = s3.Object(bucket, file_path)
            body = obj.get()['Body'].read()
            soup = BeautifulSoup(body, "html.parser")
            for i, component in enumerate(soup.findAll(html_filter)):
                soup = re.sub(str(component), str(sComponents[i]), str(soup), 1)
            
            s3.Bucket(bucket).put_object(Key=file_path, Body=soup)
            file_object = s3.Bucket(bucket).Object(file_path)
            file_object.Acl().put(ACL = 'public-read')
            updatedPages.append(file_path)
        
        return {
            'statusCode': 200,
            'body': {
                'lambda': 'json-to-html',
                'message': 'conversion to html succeded',
                'data': updatedPages
            }
        }
    except Exception as error:
        return {
            'statusCode':500,
            'body': {
                'lambda': 'json-to-html',
                'message': 'conversion to html failed',
                'data': updatedPages
            }
        }