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
  table.blueTable {
    color: #000000;
    border: 1px solid #1C6EA4;
    background-color: #EEEEEE;
    width: 50%;
    text-align: left;
    border-collapse: collapse;
  }
  table.blueTable td, table.blueTable th {
    border: 1px solid #AAAAAA;
    padding: 3px 2px;
  }
  table.blueTable tbody td {
    font-size: 13px;
  }
  table.blueTable tr:nth-child(even) {
    background: #D0E4F5;
  }
  table.blueTable thead {
    background: #1C6EA4;
    background: -moz-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
    background: -webkit-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
    background: linear-gradient(to bottom, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
    border-bottom: 2px solid #444444;
  }
  table.blueTable thead th {
    font-size: 15px;
    font-weight: bold;
    color: #FFFFFF;
    border-left: 2px solid #D0E4F5;
  }
  table.blueTable thead th:first-child {
    border-left: none;
  }
  table.blueTable tfoot td {
    font-size: 14px;
  }
  table.blueTable tfoot .links {
    text-align: right;
  }
  table.blueTable tfoot .links a{
    display: inline-block;
    background: #1C6EA4;
    color: #FFFFFF;
    padding: 2px 8px;
    border-radius: 5px;
  }
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
    <h1>Field-Level Encryption Demo</h1>
    <p>This application demonstrates Amazon CloudFront Field-Level Encryption feature</p>
  </div>
  <div class="linksColumn"> 
    <p></p>
    <form action="/submission" method="post">
      <table class="blueTable">
        <tbody>
          <thead>
          <tr><th colspan="2">Fill out the form below</th></tr>
          <tr><td>Full Name:</td><td><input type="text" name="name" value="Jenny Smith"></td></tr>
          <tr><td>Email Address:</td><td><input type="text" name="email" value="jenny@domain.com"></td></tr>
          <tr><td>Phone Number:</td><td><input type="text" name="phone" value="404-867-5309"></td></tr>
          <tr><td>&nbsp;</td><td><input type="submit" value="Submit"></td></tr>
        </tbody>
      </table> 
    </form>
    <p>&nbsp;</p><p>&nbsp;</p>
    <table class="blueTable">
      <thead>
        <tr>
          <th>Configuration</th>
          <th>Values</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Profile ID</td><td>P3K946BBGPE0BD</td></tr>
        <tr><td>Public key alias</td><td>FLEdemo</td></tr>
        <tr><td>Provider name</td><td>AWS</td></tr>
        <tr><td>Pattern to match</td><td>phone</td></tr>
        <tr><td>Content Type</td><td>application/x-www-form-urlencoded</td></tr>
        <tr><td>Public key encoded</td><td>-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwGRBGuhacmw+C73kM6Zb
u1HRLoa9stjkbBPlbpp4HFRnNk+cFantfn2FoeRCh3IF0WMeJm6H7JVcp87IMUiz
q7eoFN5ToE4rXt7G/OQOdcaP4aepieMVXLsWNgjQXk6xTPovDhia78O6UaNs6hHf
G1PAaRc+ae6Y2yecgGfrwZ4yNIr9YEsW9CrftAWo4Mkz0UniDDWcRy8blfyijmZg
on6/avRst+BgKPNxMDxXHFOto2Mqm5Y0TpMgzqpIU0M9sAlvG/WMZfPwgE0D0h1t
7/T4gtUxLCnv28gPU03Xr/eyRfjWWNZ/cbXgIE1JpxOYXPDJXZKRdD/Z8OcrcO0U
1QIDAQAB
-----END PUBLIC KEY-----</td></tr>    
      </tbody>
    </table>      
  </div>
</body>
</html>
"""

def split2len(s, n):
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))

def mergewithbreaks(s,n):
    slist = split2len(s,n)
    output = ""
    for line in slist:
        output = output + line + "<br>"
    return output

def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    response = """
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
          color: #000000;
          background-color: #E0E0E0;
          font-family: Arial, sans-serif;
          font-size:14px;
          -moz-transition-property: text-shadow;
          -moz-transition-duration: 4s;
          -webkit-transition-property: text-shadow;
          -webkit-transition-duration: 4s;
          text-shadow: none;
        }
        table.blueTable {
          border: 1px solid #1C6EA4;
          background-color: #EEEEEE;
          width: 50%;
          max-width: 50%;
          overflow: scroll;
          text-align: left;
          border-collapse: collapse;
        }
        table.blueTable td, table.blueTable th {
          border: 1px solid #AAAAAA;
          padding: 3px 2px;
        }
        table.blueTable tbody td {
          font-family: "Courier New", Courier, monospace;
          font-size: 13px;
        }
        table.blueTable tr:nth-child(even) {
          background: #D0E4F5;
        }
        table.blueTable thead {
          background: #1C6EA4;
          background: -moz-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
          background: -webkit-linear-gradient(top, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
          background: linear-gradient(to bottom, #5592bb 0%, #327cad 66%, #1C6EA4 100%);
          border-bottom: 2px solid #444444;
        }
        table.blueTable thead th {
          font-size: 15px;
          font-weight: bold;
          color: #FFFFFF;
          border-left: 2px solid #D0E4F5;
        }
        table.blueTable thead th:first-child {
          border-left: none;
        }
        table.blueTable tfoot td {
          font-size: 14px;
        }
        table.blueTable tfoot .links {
          text-align: right;
        }
        table.blueTable tfoot .links a{
          display: inline-block;
          background: #1C6EA4;
          color: #FFFFFF;
          padding: 2px 8px;
          border-radius: 5px;
        }
        </style>
      </head>
      <body id="sample">
        <h1>Contact Info</h1>
        <table class="blueTable">
          <thead>
            <tr>
              <th>Input</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
    """

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
                #response = "Received message: %s" % request_body
                response = response + "<tr><td>name:</td><td>" + Name + "</td></tr>"
                response = response + "<tr><td>email:</td><td>" + Email + "</td></tr>"
                response = response + "<tr><td>phone (encrypted):</td><td>" + mergewithbreaks(Phone,60) + "</td></tr>"
                DBTableName = os.environ['TABLENAME']
                #response = response + "<br>dynamodb: " + DBTableName
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
                #response = response + "<br>DynamoDB response: " + str(DBResponse)



        except (TypeError, ValueError):
            logger.warning("TypeError:" + str(TypeError))
            logger.warning("ValueError:" + str(ValueError))        
    else:
        response = welcome
    
    response = response + """
          </tbody>
        </table>
      </body>
    </html>
    """
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    return [response]


if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
