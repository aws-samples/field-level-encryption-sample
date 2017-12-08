# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import os
import json
import boto3

import aws_encryption_sdk
from aws_encryption_sdk.internal.crypto import WrappingKey
from aws_encryption_sdk.key_providers.raw import RawMasterKeyProvider
from aws_encryption_sdk.identifiers import WrappingAlgorithm, EncryptionKeyType

from Crypto.PublicKey import RSA
import base64

PrivateKeyPath = os.environ['PRIVATEKEYSSMPATH']
DBTableName = os.environ['TABLENAME']
provider_id = os.environ['PROVIDERID']

def decrypt_data(event, context):
    class SIFPrivateMasterKeyProvider(RawMasterKeyProvider):
        provider_id = provider_id

        def __new__(cls, *args, **kwargs):
            obj = super(SIFPrivateMasterKeyProvider, cls).__new__(cls)
            return obj

        def __init__(self, private_key_id, private_key_text):
            RawMasterKeyProvider.__init__(self)

            private_key = RSA.importKey(private_key_text)
            self._key = private_key.exportKey()

            RawMasterKeyProvider.add_master_key(self, private_key_id)

        def _get_raw_key(self, key_id):
            return WrappingKey(
                wrapping_algorithm=WrappingAlgorithm.RSA_OAEP_SHA256_MGF1,
                wrapping_key=self._key,
                wrapping_key_type=EncryptionKeyType.PRIVATE
            )

    def DecryptField(private_key, field_data):
        # add padding if needed base64 decoding
        field_data = field_data + '=' * (-len(field_data) % 4)
        # base64-decode to get binary ciphertext
        ciphertext = base64.b64decode(field_data)
        # decrypt ciphertext into plaintext
        plaintext, header = aws_encryption_sdk.decrypt(
            source=ciphertext,
            key_provider=sif_private_master_key_provider
        )
        return plaintext

    # retrieve private key from Parameter Store into local memory
    ssmclient = boto3.client('ssm')
    ssmresponse = ssmclient.get_parameter(
        Name=PrivateKeyPath,
        WithDecryption=True
    )
    private_key_text = ssmresponse['Parameter']['Value']
    sif_private_master_key_provider = SIFPrivateMasterKeyProvider("DemoPublicKey", private_key_text)

    # connect to DynamoDB table
    ddbclient = boto3.client('dynamodb')
    DBResponse = ddbclient.scan(TableName = DBTableName)

    d = []
    for i in DBResponse['Items']:
        # Phone fields are encrypted, each field will require decryption
        PhoneDecrypted = DecryptField( private_key_text, i['Phone']['S'] )
        d.append( ['Name: ' + i['Name']['S'], 'Email: ' + i['Email']['S'],
        'Phone Encrypted: ' + i['Phone']['S'][:30] + '...', 'Phone Decrypted: ' + PhoneDecrypted ] )

    # remove private key from local memory
    private_key_text = None

    # return result
    return d

def main():
	decrypt_data ("test", "test")

if __name__ == "__main__":
  main()
