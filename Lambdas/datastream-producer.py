import json
import boto3


def lambda_handler(event, context):
    
    kinesis = boto3.client('kinesis', region_name='us-east-1')
    s3 = boto3.client('s3', region_name='us-east-1')
    print(event)
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        
        print(bucket, key)
        
        log = s3.get_object(Bucket=bucket,Key=key)['Body'].read().decode('utf-8')
        # print(log)
        # kinesis.put_record(log)
        response = kinesis.put_record(
            StreamName='log-stream',
            Data=json.dumps(log),
            PartitionKey='aa-bb'
        )
        
        print(response)
                
        
        # kinesis
    return {
        'statusCode': 200,
        'body': json.dumps('Log uploaded to Datastream')
    }
