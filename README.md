# real-time-logs-anomaly-monitoring

In this project, I have developed a pipeline to ingest logs from any source and store these logs in OpenSearch for anomaly detection. This pipeline works in real time and can be easily configured to monitor any field in your log file. A typical use case for such implementation: detecting anomalies, alerting security team, and presenting a dashboard to executives showing KPI on:
- WAF  (Web based Application firewall)
- System logs 
- Cloudwatch logs
- Splunk logs
- Cloudtrail logs

I have developed a script to generate mock log files from an ec2 instance to store them in s3. The script is ran using cron jobs and generates 4 random log files per minute. Script can either randomly generate anomalies or we can enfore anomalies 

## Architecture Diagram

<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205931500-d517c308-44cc-452a-9eea-87f68a3bc0bf.png" />
</p>

### Log-file

<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205931955-30378f62-8406-4590-a623-6d44e998d98b.png" />
</p>

Log file generated by ec2 has the following fields, highlighted fields reperesents the fields monitored for anomalies. As mentioned above, a python script is responsible for generating this log-file, there we know what to expect as values. Following we discuss  values various fields can take and their respective anomaly value. 

1. action can take the following value: ["ALLOW", "CAPTCHA", "Challenge", "Count", "BLOCK"], here "BLOCK" is the anomaly
2. httpSourceName  can take the following value: ["ALB", "APIGW", "APPSYNC", "CF", "-"], here "-" is the anomaly
3. httpStatus can take the following value: ["200", "202", "307", "308", "403", "404", "502", "504"], here "4xx" and "5xx" are the anomaly
4. country can take the following value:["US", "UK", "IN", "XX", "YY", "ZZ", "WW"], here "XX", "YY", "ZZ", "WW" are the anomaly
5. httpMethod can take the following value: ["GET", "HEAD", "POST", "DELETE"], here "DELETE" is the anomaly

### Transformed log-file

Kinesis-firehose transforms the log-file before storing it in opensearch. The log-file post transform looks like:

<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205932033-2555f28f-2489-4235-b1cc-a31efb406dbd.png" />
</p>

- K_action = 1 if action in ["ALLOW", "CAPTCHA", "Challenge", "Count"] else K_action = 0
- B_action = 1 if action in ["BLOCK"] else B_action = 0
- K_source = 1 if httpSourceName in ["ALB", "APIGW", "APPSYNC", "CF"] else K_source = 0
- UNK_source = 1 if httpSourceName not in ["ALB", "APIGW", "APPSYNC", "CF"] else UNK_source = 0
- G_httpstatus= 1 if httpStatus in ["2xx", "3xx"] else G_httpstatus= 0
- B_httpstatus= 1 if httpStatus in ["4xx", "5xx"] else B_httpstatus= 0
- K_country = 1 if country in ["US", "UK", "IN"] else K_country = 0
- UNK_country = 1 if country not in ["US", "UK", "IN"] else UNK_country = 0
- common_method = 1 if httpMethod in ["GET", "HEAD", "POST"] else common_method = 0
- uncommon_method = 1 if httpMethod in ["DELETE"] else uncommon_method = 0

## Opensearch (Anomaly Detector)
<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205932269-c532b38c-8d36-4fce-af01-03e16bec4ff9.png" />
</p>

### Historical Analysis for Block action anomaly
<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205932373-02caf58c-5f1a-4989-bd5d-e7916ea265c3.png" />
</p>

### Live HttpStatus anomaly trends
<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205932511-e836e3af-e4f9-4431-9d32-a1bc0a54ed1c.png" />
</p>

### Live unknown country anomaly trends
<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205932549-ce7a4355-404f-4f83-af15-fe6ffe266383.png" />
</p>

## Alerts
<p align="center">
  <img src="https://user-images.githubusercontent.com/50113394/205932637-86733e64-5ad2-4d7a-be75-67b32ba5ec33.png" />
</p>
