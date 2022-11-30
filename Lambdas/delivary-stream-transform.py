import base64
import json

def lambda_handler(event,context):
    output = []
    print(event)
    
    # loop through records in incoming Event
    for record in event["records"]:
        # extract message
        message = json.loads(json.loads(base64.b64decode(record["data"])))
        print('timestamp: ', message["timestamp"])
        print('action: ', message["action"])
        print('httpSourceName: ', message["httpSourceName"])
        print('httpSourceId: ', message["httpSourceId"])
        print('httpStatus: ', message["httpStatus"])
        print('country: ', message["httpRequest"]["country"])
        print('httpMethod: ', message["httpRequest"]["httpMethod"])
        
        timestamp = message["timestamp"]
        action = message["action"]
        httpSourceName = message["httpSourceName"]
        httpSourceId = message["httpSourceId"]
        httpStatus = message["httpStatus"]
        country = message["httpRequest"]["country"]
        httpMethod = message["httpRequest"]["httpMethod"]

        K_action, B_action = filter_action(action) # ALLOW, CAPTCHA, Challenge, Count, BLOCK
        K_source, UNK_source = filter_httpSourceName(httpSourceName) # ALB, APIGW, APPSYNC, CF, UNK
        G_httpstatus, B_httpstatus = filter_httpStatus(httpStatus) # two, three, four, five
        K_country, UNK_country = filter_country(country) # US, UK, IN, UNK_country
        common_method, uncommon_method = filter_httpMethod(httpMethod) # common_method, uncommon_method
        
        # append new fields in message dict
        message["K_action"] = K_action
        message["B_action"] = B_action
        message["K_source"] = K_source
        message["UNK_source"] = UNK_source
        message["G_httpstatus"] = G_httpstatus
        message["B_httpstatus"] = B_httpstatus
        message["K_country"] = K_country
        message["UNK_country"] = UNK_country
        message["common_method"] = common_method
        message["uncommon_method"] = uncommon_method
        
        # base64-encoding
        data = base64.b64encode(json.dumps(message).encode('utf-8'))
        
        output_record = {
            "recordId": record['recordId'], # retain same record id from the Kinesis data Firehose
            "result": "Ok",
            "data": data.decode('utf-8')
        }
        output.append(output_record)
    return {"records": output}

        
def filter_action(action):
    K_action, B_action = 0, 0
    
    if action in ["ALLOW", "CAPTCHA", "Challenge", "Count"]:
        K_action = 1
    elif action == "BLOCK":
        # Anomaly
        B_action = 1

    return K_action, B_action

def filter_httpSourceName(httpSourceName):
    K_source, UNK_source = 0, 0
    
    if httpSourceName == "ALB":
        K_source = 1
    elif httpSourceName == "APIGW":
        K_source = 1
    elif httpSourceName == "APPSYNC":
        K_source = 1
    elif httpSourceName == "CF":
        K_source = 1
    else:
        UNK_source = 1
    
    return K_source, UNK_source

def filter_httpStatus(httpStatus):
    G_httpstatus, B_httpstatus = 0, 0
    
    if httpStatus[0] == "2":
        G_httpstatus = 1
    elif httpStatus[0] == "3":
        G_httpstatus = 1
    elif httpStatus[0] == "4":
        B_httpstatus = 1
    elif httpStatus[0] == "5":
        B_httpstatus = 1
    
    return G_httpstatus, B_httpstatus

def filter_country(country):
    K_country, UNK_country = 0, 0
    
    if country == "US":
        K_country = 1
    elif country == "UK":
        K_country = 1
    elif country == "IN":
        K_country = 1
    else:
        UNK_country = 1
    
    return K_country, UNK_country
    
def filter_httpMethod(httpMethod):
    common_method, uncommon_method = 0, 0
    
    if httpMethod == "DELETE":
        uncommon_method = 1
    else:
        common_method = 1
    
    return common_method, uncommon_method
