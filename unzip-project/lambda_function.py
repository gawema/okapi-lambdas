from __future__ import print_function

import urllib
import zipfile
import boto3
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):

    try:
        bucket = event['bucket']
        user_id = event['user_id']
        project_id = event['project_id']
        file_name = event['file_name']
        key = user_id + '/' + project_id + '/' + file_name
        obj = s3.get_object(Bucket=bucket, Key=key)
        putObjects = []
        with io.BytesIO(obj['Body'].read()) as tf:

            # rewind the file
            tf.seek(0)

            # Read the file as a zipfile and process the members
            with zipfile.ZipFile(tf, mode='r') as zipf:
                for file in zipf.infolist():
                    fileName = file.filename
                    if not fileName.startswith('__MACOSX'):
                        putFile = s3.put_object(Bucket=bucket,
                                Key=user_id + '/' + project_id + '/'
                                + fileName, Body=zipf.read(file),
                                ContentType='text/html')
                        putObjects.append(putFile)

        # Delete zip file after unzip
        if len(putObjects) > 0:
            s3.delete_object(Bucket=bucket, Key=user_id + '/'
                             + project_id + '/' + file_name)

        return {
            'statusCode': 200,
            'body': {
                'lambda': 'unzip-project',
                'message': 'unziped project ' + project_id + ' successfully'
            }
        }
    
    except Exception as error:
        return {
            'statusCode': 500,
            'body': {
                'lambda': 'unzip-project',
                'message': 'unzipped project failed',
                'error': str(error)
            }
        }
