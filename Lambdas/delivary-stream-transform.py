import base64
import json

def lambda_handler(event,context):
    output = []
    
    try:
        # loop through records in incoming Event
        for record in event["records"]:
            # extract message
            message = json.loads(base64.b64decode(event["records"][0]["data"]))
            
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

            ALLOW, CAPTCHA, Challenge, Count, BLOCK = filter_action(action) # ALLOW, CAPTCHA, Challenge, Count, BLOCK
            K_source, UNK_source = filter_httpSourceName(httpSourceName) # ALB, APIGW, APPSYNC, CF, UNK
            two, three, four, five = filter_httpStatus(httpStatus) # two, three, four, five
            US, UK, IN, UNK_country = filter_country(country) # US, UK, IN, UNK_country
            common_method, uncommon_method = filter_httpMethod(httpMethod) # common_method, uncommon_method
            
            # append new fields in message dict
            message["ALLOW"] = ALLOW
            message["CAPTCHA"] = CAPTCHA
            message["Challenge"] = Challenge
            message["Count"] = Count
            message["BLOCK"] = BLOCK
            message["K_source"] = K_source
            message["UNK_source"] = UNK_source
            message["2xx"] = two
            message["3xx"] = three
            message["4xx"] = four
            message["5xx"] = five
            message["US"] = US
            message["UK"] = UK
            message["IN"] = IN
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
    except Exception as e:
        print(e)
        
def filter_action(action):
    ALLOW, CAPTCHA, Challenge, Count, BLOCK = 0, 0, 0, 0, 0
    
    if action == "ALLOW":
        ALLOW = 1
    elif action == "CAPTCHA":
        CAPTCHA = 1
    elif action == "Challenge":
        Challenge = 1
    elif action == "Count":
        Count = 1
    elif action == "BLOCK":
        # Anomaly
        BLOCK = 1

    return ALLOW, CAPTCHA, Challenge, Count, BLOCK

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
    two, three, four, five = 0, 0, 0, 0
    
    if httpStatus[0] == "2":
        two = 1
    elif httpStatus[0] == "3":
        three = 1
    elif httpStatus[0] == "4":
        four = 1
    elif httpStatus[0] == "5":
        five = 1
    
    return two, three, four, five

def filter_country(country):
    US, UK, IN, UNK_country = 0, 0, 0, 0
    
    if country == "US":
        US = 1
    elif country == "UK":
        UK = 1
    elif country == "IN":
        IN = 1
    else:
        UNK_country = 1
    
    return US, UK, IN, UNK_country
    
def filter_httpMethod(httpMethod):
    common_method, uncommon_method = 0, 0
    
    if httpMethod == "DELETE":
        uncommon_method = 1
    else:
        common_method = 1
    
    return common_method, uncommon_method
