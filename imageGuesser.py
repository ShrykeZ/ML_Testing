import json
import logging
import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

LABEL = '<LABEL>'

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    logger.info(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    image = event['Records'][0]['s3']['object']['key']
    output_key = 'output/rekognition_response.json'
    response = {'Status': 'Not Found', 'body': []}


    rekognition_client = boto3.client('rekognition')

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_labels


    try:
        response_rekognition = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': image
                }
            },
            MinConfidence=70
        )

        
        detected_labels = []
        
        if response_rekognition['Labels']:
            for label in response_rekognition['Labels']:
                detected_labels.append(label['Name'].lower())
            print(detected_labels)
        
            if LABEL in detected_labels:
                response['Status'] = f"Success! {LABEL} found"
                response['body'].append(response_rekognition['Labels'])
            else:
                response['Status'] = f"Failed! {LABEL} Not found"
                response['body'].append(response_rekognition['Labels'])
                
    except Exception as error:
        print(error)

    s3_client.put_object(
      Bucket=bucket,
      Key=output_key,
      Body=json.dumps(response, indent=4)
    )

    return response