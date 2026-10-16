  * [ Home ](https://developers.google.com/)
  * [ Products ](https://developers.google.com/products)
  * [ Google Identity ](https://developers.google.com/identity)
  * [ Credential Verification ](https://developers.google.com/identity/credential-verification)



Send feedback 

#  Perform SMS Verification on a Server Stay organized with collections  Save and categorize content based on your preferences. 

![Spark icon](/_static/images/icons/spark.svg)

## Page Summary

outlined_flag

  * Implementing automatic phone number verification requires both client and server portions of the verification flow, with the server handling message construction, sending, and code verification.

  * The phone verification server is responsible for constructing a verification message with a one-time code and app hash, sending it via SMS, and verifying the code when the client sends it back.

  * The verification message must be no longer than 140 bytes, contain a unique one-time code, and include an 11-character hash string identifying your app.

  * Generating a one-time code involves creating unguessable codes that can be linked to a user or phone number and are easy for users to type manually.

  * Computing your app's hash string requires using your app's package name and public key certificate, typically through a series of command-line steps.




To automatically verify phone numbers, you must implement both the client and server portions of the verification flow. This document describes how to implement the server portion.

The phone verification server is responsible for three tasks:

  1. Constructing a verification message that includes a one-time code and has the format the client-side SMS Retriever API expects
  2. Sending the verification message to to the user's device
  3. Verifying the one-time code when it's sent back to the server and completing any post-verification tasks your backend requires



The specifics of how your app interacts with the server are up to you. A common approach is to expose a REST API with two endpoints: one that receives requests to verify a given phone number and sends the SMS verification messages, and a second endpoint that receives one-time codes from your app.

## 1\. Construct a verification message

When your server receives a request to verify a phone number, first construct the verification message that you will send to the user's device. This message must:

  * Be no longer than 140 bytes
  * Contain a one-time code that the client sends back to your server to complete the verification flow (see Generating a one-time code)
  * Include an 11-character hash string that identifies your app (see Computing your app's hash string)



Otherwise, the contents of the verification message can be whatever you choose. It is helpful to create a message from which you can easily extract the one-time code later on. For example, a valid verification message might look like the following: 
    
    
    Your ExampleApp code is: 123ABC78
    
    
    
    
    
    FA+9qCX9VSu
    

### Generating a one-time code

You can implement one-time codes in many ways, as long as the codes are unguessable and you can link the codes to a user or phone number when the client app sends them back to your server. You should make the codes easy to type, to accommodate any situations which might require users to manually type the code.

One way to implement one-time codes is to generate random numbers, which you use as keys in a database table. For example, you might have a PendingVerifications table like the following:

ID | User | Expiration  
---|---|---  
123456789... | 1234 | 2017-3-14 1:59  
  
You can use the base32-encoded ID as a one-time code.

### Computing your app's hash string

Google Play services uses the hash string to determine which verification messages to send to your app. The hash string is made of your app's package name and your app's public key certificate. To generate the hash string:

  1. If you use [app signing by Google Play](https://support.google.com/googleplay/android-developer/answer/7384423), download your app signing certificate (`deployment_cert.der`) from the **App signing** section of the [Google Play console](https://play.google.com/apps/publish/).

Then, import the app signing certificate into a temporary key store: 
         
         keytool -importcert -file deployment_cert.der -keystore temporary.keystore -alias PlayDeploymentCert
         

If you sign your APKs directly, skip this step.

  2. Get your app signing certificate--either the one you imported above or the one you use to sign your APKs directly--as a lower-case hex string.

For example, to get the hex string from the temporary keystore created above, type the following command: 
         
         keytool -exportcert -keystore temporary.keystore -alias PlayDeploymentCert | xxd -p | tr -d "[:space:]"
         

If you sign your APKs directly, specify your production keystore and certificate alias.

  3. If you created a temporary keystore, delete it.

  4. Append the hex string to your app's package name, separated by a single space.

  5. Compute the SHA-256 sum of the combined string. Be sure to remove any leading or trailing whitespace from the string before computing the SHA-256 sum.

  6. Base64-encode the binary value of the SHA-256 sum. You might need to decode the SHA-256 sum from its output format first.

  7. Your app's hash string is the first 11 characters of the base64-encoded hash.




The following command computes the hash string from your app's production keystore:
    
    
    keytool -exportcert -alias PlayDeploymentCert -keystore MyProductionKeys.keystore | xxd -p | tr -d "[:space:]" | echo -n com.example.myapp `cat` | sha256sum | tr -d "[:space:]-" | xxd -r -p | base64 | cut -c1-11
    

**Note:** This command does not emit an error if the `keytool` command fails (for example, because the alias does not exist within the keystore). Before you run the entire pipeline, try running the `keytool` command by itself to ensure it's producing meaningful output.

Alternatively, you can get your app's hash string with the [AppSignatureHelper](https://github.com/googlesamples/android-credentials/blob/master/sms-verification/android/app/src/main/java/com/google/samples/smartlock/sms_verify/AppSignatureHelper.java) class from the SMS retriever sample app. However, if you use the helper class, be sure to remove it from your app after you get the hash string. **Do not use hash strings dynamically computed on the client in your verification messages.**

## 2\. Send the verification message by SMS

After you construct the verification message, send the message to the user's phone number using any SMS system.

For example, see [App verification using Twilio SMS](https://www.twilio.com/docs/api/rest/app-verification-using-twilio-sms) on Twilio's developer site.

**Important:** Don't send the one-time code or verification message back to the user's device through any channel other than SMS. In particular, don't return the one-time code in response the verification request for the purpose of client-side verification. You must generate and verify one-time codes only on the server.

When the user's device receives this message, the message is directed to your app. Your app extracts the one-time code and sends it back to your server to complete the verification process.

## 3\. Verify the one-time code when it's returned

A phone number verification server typically has a second endpoint that it uses to receive one-time codes back from client apps. When your server receives a one-time code from your app at this endpoint, do the following:

  1. Verify that the one-time code is valid and has not expired.
  2. Record that the user linked to the one-time code has completed phone number verification.
  3. Remove the one-time code's database record, or in some other way ensure that the same code can't be used again.



When you record the user's verification status and remove one-time code from your database, verification is complete.

Send feedback 
