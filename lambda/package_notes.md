
### Building Lambda Decrypt Package

***Use these steps as a general guideline if you need to build your own decryption function package for Lambda.***

#### Launch documented Amazon Linux AMI:
http://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html

#### ssh and install environment:

~~~~
mkdir fle
sudo yum -y install gcc
virtualenv fle
source fle/bin/activate
pip install --upgrade pip
pip install cryptography aws_encryption_sdk pycrypto

cd fle/lib/python2.7/site-packages/; zip -r ~/fle_decrypt_data.zip * .*

cd fle/lib64/python2.7/site-packages/; zip -r ~/fle_decrypt_data.zip * .*
~~~~

#### Lastly add the function code to the zip from here:

https://github.com/aws-samples/field-level-encryption-sample/blob/master/lambda/fle_decrypt_data.py

#### More info:
 http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html
