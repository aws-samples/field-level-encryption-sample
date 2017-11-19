#!/bin/bash

# generate new RSA PEM key
openssl genrsa 2048 > private_encrypted_key.pem

# export public key
openssl rsa -in private_encrypted_key.pem -outform PEM -pubout -out public_key.pem

# export private key
openssl rsa -in private_encrypted_key.pem -out private_unencrypted_key.pem -outform PEM

# store the private key in Systems Manager Parameter Store
aws ssm put-parameter --type "SecureString" --name "/cloudfront/field-encryption/private-key" --value file://private_unencrypted_key.pem  --key-id "$KMSKEY"

# securely delete the private key material
shred -zvu -n  100 private*.pem