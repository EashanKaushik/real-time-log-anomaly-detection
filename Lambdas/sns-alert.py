import json
import boto3
SENDER_EMAIL = ""
RECEIVER_EMAIL = ""

def lambda_handler(event, context):
    sns_message = event["Records"][0]["Sns"]
    
    ses = boto3.client('ses')
    
    charset = "UTF-8"

    # subject = f""
    # body_text = f""
    
    response = ses.send_email(Source=SENDER_EMAIL,
                          Destination={
                              'ToAddresses': [
                                  RECEIVER_EMAIL,
                              ],
                          }, Message={
                              'Subject': {
                                  'Data': sns_message["Subject"],
                                  'Charset': charset
                              },
                              'Body': {
                                  'Text': {
                                      'Data': sns_message["Message"],
                                      'Charset': charset
                                  }
                              }
                          },
                          )

    print(response)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
