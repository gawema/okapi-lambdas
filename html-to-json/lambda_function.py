import json
from bs4 import BeautifulSoup, ResultSet, element as Element
import boto3
import bson


s3 = boto3.resource('s3')

def convetToJson(el=None, newjson={}):
	if type(el) == Element.Tag:
		newId = str(bson.objectid.ObjectId())
		newjson = {
			'_id': newId,
			'name': el.name,
			'attributes': el.attrs,
			'child_components': []
		}
		for child in el.contents:
			if type(child) == Element.Tag:
				childComponent = convetToJson(child, newjson)
				newjson['child_components'].append(childComponent)
			else:
				newjson['text'] = child
		return newjson

def lambda_handler(event, context):
	try:
		bucket = event['bucket']
		html_filter = event['html_filter']
		file_path = event['file_path']
		
		obj = s3.Object(bucket, file_path)
		
		body = obj.get()['Body'].read()
		soup = BeautifulSoup(body, "html.parser")
		components = soup.findAll(html_filter)
		jComponents = []
		jComponent = {}
		for component in components:
			jComponent = convetToJson(component)
			jComponents.append(jComponent.copy())
			
		return {
		    'statusCode': 200,
		    'body': {
		    	'lambda': 'html-to-json',
		    	'message':'conversion to json succeded',
				'data': jComponents
		    },
		}
	except Exception as error:
		return {
			'statusCode': 500,
	        'body': {
	            'lambda': 'html-to-json',
	            'message': 'conversion to json failed',
	            'error': str(error)
	        }
    	}


	