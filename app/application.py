import logging
import logging.handlers
import os
import boto3
import urllib

from wsgiref.simple_server import make_server


# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/opt/python/log/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

welcome = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
  <!--
    Copyright 2012 Amazon.com, Inc. or its affiliates. All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

        http://aws.Amazon/apache2.0/

    or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
  -->
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Amazon CloudFront Field-Level Encryption - Demo</title>
  <style>
  body {
    color: #ffffff;
    background-color: #E0E0E0;
    font-family: Arial, sans-serif;
    font-size:14px;
    -moz-transition-property: text-shadow;
    -moz-transition-duration: 4s;
    -webkit-transition-property: text-shadow;
    -webkit-transition-duration: 4s;
    text-shadow: none;
  }
  body.blurry {
    -moz-transition-property: text-shadow;
    -moz-transition-duration: 4s;
    -webkit-transition-property: text-shadow;
    -webkit-transition-duration: 4s;
    text-shadow: #fff 0px 0px 25px;
  }
  a {
    color: #0188cc;
  }
  .textColumn, .linksColumn {
    padding: 2em;
  }
  .textColumn {
    position: absolute;
    top: 0px;
    right: 50%;
    bottom: 0px;
    left: 0px;

    text-align: right;
    padding-top: 11em;
    background-color: #1BA86D;
    background-image: -moz-radial-gradient(left top, circle, #6AF9BD 0%, #00B386 60%);
    background-image: -webkit-gradient(radial, 0 0, 1, 0 0, 500, from(#6AF9BD), to(#00B386));
  }
  .textColumn p {
    width: 75%;
    float:right;
  }
  .linksColumn {
    position: absolute;
    top:0px;
    right: 0px;
    bottom: 0px;
    left: 50%;
    background-color: #E0E0E0;
  }
  h1 {
    font-size: 500%;
    font-weight: normal;
    margin-bottom: 0em;
  }
  h2 {
    font-size: 200%;
    font-weight: normal;
    margin-bottom: 0em;
  }
  ul {
    padding-left: 1em;
    margin: 0px;
  }
  li {
    margin: 1em 0em;
  }
  </style>
</head>
<body id="sample">
  <div class="textColumn">
    <h1>Secure Ingress Demo</h1>
    <p>This application demonstrates Amazon CloudFront Field-Level Encryption feature</p>
  </div>
  <div class="linksColumn"> 
    <h2>Fill out the form below:</h2>
    <form action="/submission" method="post">
      Full Name:<br>
      <input type="text" name="name" value="e.g. Jenny Smith"><br>
      Email Address:<br>
      <input type="text" name="email" value="e.g. jenny@domain.com"><br><br>
      Phone Number:<br>
      <input type="text" name="phone" value="e.g. 404-867-5309"><br><br>
      <input type="submit" value="Submit">
    </form>
  </div>
</body>
</html>
"""

def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    if method == 'POST':
        try:
            if path == '/':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size).decode()
                logger.info("Received message: %s" % request_body)
            elif path == '/submission':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size).decode()
                logger.info("Received message: %s" % request_body)
                urldecoded_body = urllib.parse.unquote(request_body)
                RowList = urldecoded_body.split('&')
                for Row in RowList:
                    NameValuePair = Row.split('=')
                    FieldName = NameValuePair[0]
                    FieldValue = NameValuePair[1]
                    if   FieldName == 'name':
                        Name = FieldValue
                    elif FieldName == 'email':
                        Email = FieldValue
                    elif FieldName == 'phone':
                        Phone = FieldValue                        
                logger.info('name=' + Name)
                logger.info('email=' + Email)    
                logger.info('phone=' + Phone)
                response = "Received message: %s" % request_body
                response = response + "<br>name: " + Name
                response = response + "<br>email: " + Email
                response = response + "<br>phone: " + Phone
                DBTableName = os.environ['TABLENAME']
                response = response + "<br>dynamodb: " + DBTableName
                logger.info("about to connect to dynamodb")
                ddbclient = boto3.client('dynamodb', region_name='us-east-1')
                logger.info("about to put_item")
                DBResponse = ddbclient.put_item(
                  TableName = DBTableName,
                  Item = {
                    'Email': {'S': Email},
                    'Phone': {'S': Phone},
                    'Name':  {'S': Name }
                  }
                )
                logger.info("<br>DynamoDB response: " + str(DBResponse))
                response = response + "<br>DynamoDB response: " + str(DBResponse)


        except (TypeError, ValueError):
            logger.warning("TypeError:" + str(TypeError))
            logger.warning("ValueError:" + str(ValueError))        
    else:
        response = welcome
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    return [response]


if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
