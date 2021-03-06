# Enhance the Security of Sensitive Customer Data by Using Amazon CloudFront Field-Level Encryption

***The complete post for this solution is [available on the AWS Security Blog](https://aws.amazon.com/blogs/security/how-to-enhance-the-security-of-sensitive-customer-data-by-using-amazon-cloudfront-field-level-encryption/).***

### How CloudFront field-level encryption works

Many web applications collect and store data from users as those users interact with the applications. For example, a travel booking website may ask for your passport number and less sensitive data such as your food preferences. This data is transmitted to web servers and also might travel among a number of services to perform tasks. However, this also means that your sensitive information may need to be accessed by only a small subset of these services (most other services do not need to access your data).
User data is often stored in a database for retrieval at a later time. One approach to protecting stored sensitive data is to cautiously configure and code each service to ensure that sensitive data is protected. For example, you can develop safeguards in logging functionality to ensure sensitive data is masked or removed. This can add complexity to your code base and limit performance.

Field-level encryption addresses this problem by ensuring sensitive data is encrypted at CloudFront edge locations. Sensitive data fields in HTTPS form POSTs are automatically encrypted with a user-provided public RSA key. After the data is encrypted, other systems in your architecture see only ciphertext. Even if this ciphertext unintentionally becomes externally available, the data is cryptographically protected and only designated systems with access to the private RSA key can decrypt the sensitive data.
It is critical to secure private RSA key material to prevent unauthorized access to the protected data. Management of cryptographic key material is a larger topic that is out of scope for this blog post, but should be carefully considered when implementing encryption in your applications. For example, in this blog post we store private key material as a secure string in the Amazon EC2 Systems Manager Parameter Store. The Parameter Store provides a centralized location for managing your configuration data such as plaintext data (such as database strings) or secrets (such as passwords) that are encrypted using AWS Key Management Service (AWS KMS). You may have an existing key management system in place that you can use, or you can use AWS CloudHSM. CloudHSM is a cloud-based hardware security module (HSM) that enables you to easily generate and use your own encryption keys in the AWS Cloud.

To illustrate field-level encryption, let's look at a simple form submission where Name and Phone values are sent to a web server using an HTTP POST. A typical form POST would contain data such as the following.

~~~
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length:60

Name=Jane+Doe&Phone=404-555-0150


Instead of taking this typical approach, field-level encryption converts this data similar to the following.
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 1713

Name=Jane+Doe&Phone=AYABeHxZ0ZqWyysqxrB5pEBSYw4AAA...
~~~

To further demonstrate field-level encryption in action, this blog post includes a sample serverless application that you can deploy by using a CloudFormation template, which creates an application environment using CloudFront, Amazon API Gateway and Lambda. The sample application is only intended to demonstrate field-level encryption functionality and is not intended for production use. The following diagram depicts the architecture and data flow of this sample application.

### Architecture Overview

![architecture diagram](images/secure-ingress-architecture.png)

Here is how the sample solution works:

1.	An application user submits an HTML form page with sensitive data, generating an HTTPS POST to CloudFront.
2.	Field-level encryption intercepts the form POST and encrypts sensitive data with the public RSA key and replaces fields in the form post with encrypted ciphertext. The form POST ciphertext is then sent to origin servers.
3.	The serverless application accepts the form post data containing cipher text where sensitive data would normally reside. If a malicious user were able to compromise your application and gain access to your data, such as the contents of a form, this data is encrypted.
4.	AWS Lambda stores data in a DynamoDB table, leaving sensitive data to remain safely encrypted at rest.
5.	An administrator the AWS Console and a Lambda function to view the sensitive data.
6.	During the session, the administrator retrieves cipher text from the DynamoDB table.
7.	An administrator decrypts sensitive data using private key material stored in EC2 Systems Manager Parameter Store.
8.	Finally, decrypted sensitive data is transmitted over SSL/TLS via the AWS console to the administrator for review.
