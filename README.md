# Protect Sensitive Data in Web Forms with Field-Level Encryption and CloudFront

Many web applications have a need to collect sensitive data from users.  For example, a travel booking web site may ask for your passport number, as well as some less sensitive data such as name, phone number and email address.  This data is transmitted to web servers and may also bounce among a number of microservices to perform useful work.  Finally, it is likely to be stored in a database for later retrieval.

Typical approach to sensitive data protection is that each microservice and database access must be carefully configured and coded to ensure sensitive data is protected.  For example, you would develop safeguards in logging functionality to ensure sensitive data is masked or stripped out.  This can add complexity to your codebase, drag down performance, and even then the safeguards rarely provide perfect protection.

Field-Level Encryption solves this problem in a unique way.  Sensitive data fields in https form POSTs are automatically encrypted with customer-provided public RSA key.  From that point, all other systems in your architecture would only see cyphertext.  Even if one of these systems leaks out this cyphertext, the data is cryptographically protected.  Only designated systems with access to the private RSA key can decrypt sensitive data.

For example, a typical form post would contain data like this:

````
POST / HTTP/1.1
Host: foo.com
Content-Type: application/x-www-form-urlencoded

Name=Bob&Phone=1235551212
````

Field-Level Encryption converts this to:
````
POST / HTTP/1.1
Host: foo.com
Content-Type: application/x-www-form-urlencoded

Name=Bob&Phone=<encrypted>ejYx52fxx2jjnwetvxx</encrypted>
````

Field-Level Encryption adds another security layer to CloudFront, in addition to security feautres such as TLS encryption support, DDoS resilience, access logging, and others.  CloudFront integrates with AWS Shield for DDoS protection and with AWS WAF for protection against application-layer attacks, such as SQL injection and cross-site scripting.  Please review [AWS Best Practices for DDoS Resiliency](https://d0.awsstatic.com/whitepapers/Security/DDoS_White_Paper.pdf) and   [Use AWS WAF to Mitigate OWASP&#39;s Top 10 Web Application Vulnerabilities](https://d0.awsstatic.com/whitepapers/Security/aws-waf-owasp.pdf) whitepapers for more details on edge security in AWS.


## Architecture Ovierview

![architecture diagram](images/secure-ingress-architecture.png)

1. User fills out HTML form page with sensitive data and submits the form, generating https POST to **Amazon CloudFront**.
2. **Field-Level Encryption** feature of Amazon CloudFront intercepts the form POST and encrypts sensitive data with the public RSA key and replaces fields in the form post with encrypted ciphertext.  Form post is then safely sent to origin servers.
3. **Elastic Beanstalk** Application accepts the form post data containing ciphertext where sensitive data would normally reside. If any data leak was to occur in the application, for example writing out form contents to logs, the sensitive data remains safe protected with encryption.
4. Elastic Beanstalk stores data in a **DynamoDB** table, leaving sensitive data to remain safely encrypted at rest.
5. Administrator who needs to view sensitive data logs in remotely via SSH to a bastion host **EC2** instance.
6. In the remote session, administrator retrieves ciphertext from the DynamoDB table.
7. Administrator decrypts sensitive data using private RSA key stored on the secure EC2 instance.
8. Finally, decrypted sensitive data is transmitted via SSH to the administrator for review.


## Deployment Walkthrough

1. Deploy CloudFormation template
2. SSH to EC2 instance
3. Generate RSA key pair
4. Upload public key to CloudFront and associate with Field-Level Encryption configuration

## Testing Steps

1. Open URL in the browser
2. Fill out HTML form with sensitive data, click Submit
3. SSH to EC2 instance
4. Run Python script to download ciphertext from DynamoDB and decrypt sensitive data fields