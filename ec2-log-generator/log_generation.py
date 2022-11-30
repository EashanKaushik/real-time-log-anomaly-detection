"""

httpSourceName - ['APIGW', 'ALB', 'CF', '-', 'APPSYNC']
timestamp - ['am', 'pm']
action - ['ALLOW', 'BLOCK', 'CAPTCHA', 'Count', 'Challenge']
httpRequest -> country
httpRequest -> httpMethod
httpStatus
"""
import json
import random
import datetime
import sys
import time
import boto3
import pytz

newYorkTz = pytz.timezone("America/New_York") 

session = boto3.Session(profile_name='default')
s3 = session.client('s3')

class GenerateLog():
    def __init__(self, anomaly=False, anomaly_in=None):
        self.anomaly = anomaly
        self.anomaly_in = anomaly_in
        
        
        self.anomaly_in_types = set(["action", "httpSourceName", "httpStatus", "country", "httpMethod"])
        if self.anomaly:
            assert self.anomaly_in, "anomaly_in must be defined"
            assert self.anomaly_in in self.anomaly_in_types, f"Anomaly type must be one of the {', '.join(list(self.anomaly_in_types))}"
        
        with open("log.json", "r") as log_template:
            self.log  = json.load(log_template)
        
        self.timestamp = datetime.datetime.now(newYorkTz).timestamp()
        self.action = None
        self.httpSourceName = None
        self.httpSourceId = None
        self.httpStatus = None
        self.httpRequest_country = None
        self.httpRequest_httpMethod = None
        
        
        if self.anomaly:
            self.normal_params()
            self.anomaly_params()
        else:
            self.normal_params()
    
    def normal_params(self):
                
        self.action = random.choices(
            population=["ALLOW", "CAPTCHA", "Challenge", "Count", "BLOCK"], 
            weights=[0.25, 0.25, 0.25 ,0.25, 0.001],  
            k=1
            )[0]
        
        self.httpSourceName = random.choices(
            population=["ALB", "APIGW", "APPSYNC", "CF", "-"], 
            weights=[0.25, 0.25, 0.25 ,0.25, 0.001],  
            k=1
            )[0]
        self.httpSourceId = self.httpSourceName.lower()
        self.httpStatus = random.choices(
            population=["200", "202", "307", "308", "403", "404", "502", "504"], 
            weights=[0.2, 0.2, 0.2, 0.2, 0.001, 0.001, 0.001 ,0.001],  
            k=1
            )[0]
        self.httpRequest_country = random.choices(
            population=["US", "UK", "IN", "XX", "YY", "ZZ", "WW"], 
            weights=[0.33, 0.33, 0.33, 0.001, 0.001, 0.001, 0.001],  
            k=1
            )[0]
        self.httpRequest_httpMethod = random.choices(
            population=["GET", "HEAD", "POST", "DELETE"], 
            weights=[0.33, 0.33, 0.33, 0.001],  
            k=1
            )[0]

    def anomaly_params(self):
        
        if self.anomaly_in == "action":
            print(f"Anomaly Generated in {self.anomaly_in}")
            self.action = random.choices(
                population=["ALLOW", "CAPTCHA", "Challenge", "Count", "BLOCK"], 
                weights=[0.1, 0.1, 0.1 ,0.1, 2],  
                k=1
                )[0]
        if self.anomaly_in == "httpSourceName":
            print(f"Anomaly Generated in {self.anomaly_in}")
            self.httpSourceName = random.choices(
                population=["ALB", "APIGW", "APPSYNC", "CF", "-"], 
                weights=[0.1, 0.1, 0.1 ,0.1, 2],  
                k=1
                )[0]
            self.httpSourceId = self.httpSourceName.lower()
        
        if self.anomaly_in == "httpStatus":
            print(f"Anomaly Generated in {self.anomaly_in}")
            self.httpStatus = random.choices(
                population=["200", "202", "307", "308", "403", "404", "502", "504"], 
                weights=[0.05, 0.05, 0.05 ,0.05, 2, 2, 2, 2],  
                k=1
                )[0]
            
        if self.anomaly_in == "country":
            print(f"Anomaly Generated in {self.anomaly_in}")
            self.httpRequest_country = random.choices(
                population=["US", "UK", "IN", "XX", "YY", "ZZ", "WW"], 
                weights=[0.1, 0.05, 0.05, 2, 2, 2, 2],  
                k=1
                )[0]
        if self.anomaly_in == "httpMethod":
            print(f"Anomaly Generated in {self.anomaly_in}")
            self.httpRequest_httpMethod = random.choices(
                population=["GET", "HEAD", "POST", "DELETE"], 
                weights=[0.15, 0.15, 0.15 , 2],  
                k=1
                )[0]
    def send_log(self):
        self.log["timestamp"] = self.timestamp
        self.log["action"] = self.action
        self.log["httpSourceName"] = self.httpSourceName
        self.log["httpSourceId"] = self.httpSourceId
        self.log["httpStatus"] = self.httpStatus
        self.log["httpRequest"]["country"] = self.httpRequest_country        
        self.log["httpRequest"]["httpMethod"] = self.httpRequest_httpMethod
        
        return json.dumps(self.log)

def job(anomaly, anomaly_in):
    
    count = 0
    
    while count != 5:
        # print(anomaly, anomaly_in)
    
        log = GenerateLog(anomaly, anomaly_in).send_log()
        
        response = s3.put_object(
            Body=log,
            Bucket='cloud-security-project-logs',
            Key=str(datetime.datetime.now(newYorkTz).timestamp()) + ".json",
        )
        count += 1
        time.sleep(10)

if __name__ == "__main__":
    
    anomaly_in = None
    if sys.argv[1].lower() == 'true':
        anomaly = True
        try:
            anomaly_in = sys.argv[2]
        except Exception as ex:
            print("Argument anomaly_in must be defined")
    elif sys.argv[1].lower() == 'false':
        anomaly = False
    else:
        raise Exception("Invalid argument must be true/false")
    
    job(anomaly, anomaly_in)
    
    
        

        