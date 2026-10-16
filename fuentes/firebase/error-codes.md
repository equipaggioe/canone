  * [ Firebase ](https://firebase.google.com/)
  * [ Documentation ](https://firebase.google.com/docs)
  * [ FCM ](https://firebase.google.com/docs/cloud-messaging)
  * [ Run ](https://firebase.google.com/docs/run)



Send feedback 

#  FCM Error Codes Stay organized with collections  Save and categorize content based on your preferences. 

## REST error codes for the HTTP v1 API

HTTP error responses for the HTTP v1 API contain an error code, an error message, and error status. They may also contain a `details` array with more details on the error.

Here are two sample error responses:

#### Example 1: Error response from an HTTP v1 API request with an invalid value in a data message
    
    
    {
      "error": {
        "code": 400,
        "message": "Invalid value at 'message.data[0].value' (TYPE_STRING), 12",
        "status": "INVALID_ARGUMENT",
        "details": [
          {
            "@type": "type.googleapis.com/google.rpc.BadRequest",
            "fieldViolations": [
              {
                "field": "message.data[0].value",
                "description": "Invalid value at 'message.data[0].value' (TYPE_STRING), 12"
              }
            ]
          }
        ]
      }
    }
    

#### Example 2: Error response from an HTTP v1 API request with an invalid registration token
    
    
    {
      "error": {
        "code": 400,
        "message": "The registration token is not a valid FCM registration token",
        "status": "INVALID_ARGUMENT",
        "details": [
          {
            "@type": "type.googleapis.com/google.firebase.fcm.v1.FcmError",
            "errorCode": "INVALID_ARGUMENT"
          }
        ]
       }
    }
    

Note that both messages have the same code and status, but the details array contains values in different types. The first example has type `type.googleapis.com/google.rpc.BadRequest` indicating an error in request values. The second example with type `type.googleapis.com/google.firebase.fcm.v1.FcmError` has an FCM specific error. For many errors, the details array contains the information you'll need to debug and find a resolution.

The following table lists the FCM v1 REST API error codes and their descriptions.  Error Code | Description and Resolution Steps  
---|---  
`UNSPECIFIED_ERROR` No more information is available about this error. | None.  
`INVALID_ARGUMENT` (HTTP error code = 400) Request parameters were invalid. An extension of type `google.rpc.BadRequest` is returned to specify which field was invalid. | Potential causes include invalid registration, invalid package name, message too big, invalid data key, invalid TTL, or other invalid parameters.  
**Invalid registration** : Check the format of the registration token you pass to the server. Make sure it matches the registration token the client app receives from registering with FCM. Do not truncate the token or add additional characters.  
**Invalid package name** : Make sure the message was addressed to a registration token whose package name matches the value passed in the request.  
**Message too big** : Check that the total size of the payload data included in a message does not exceed FCM limits: 4096 bytes for most messages, or 2048 bytes in the case of messages to topics. This includes both the keys and the values.  
**Invalid data key** : Check that the payload data does not contain a key (such as from, or gcm, or any value prefixed by google) that is used internally by FCM. Note that some words (such as collapse_key) are also used by FCM but are allowed in the payload, in which case the payload value will be overridden by the FCM value.  
**Invalid TTL** : Check that the value used in ttl is an integer representing a duration in seconds between 0 and 2,419,200 (4 weeks).  
**Invalid parameters** : Check that the provided parameters have the right name and type.  
`UNREGISTERED` (HTTP error code = 404) App instance was unregistered from FCM. This usually means that the token used is no longer valid and a new one must be used. | This error can be caused by missing registration tokens, or unregistered tokens.  
**Missing Registration** : If the message's target is a `token` value, check that the request contains a registration token.  
**Not registered** : An existing registration token may cease to be valid in a number of scenarios, including:  
\- If the client app unregisters with FCM.  
\- If the client app is automatically unregistered, which can happen if the user uninstalls the application. For example, on iOS, if the APNs Feedback Service reported the APNs token as invalid.  
\- If the registration token expires (for example, Google might decide to refresh registration tokens, or the APNs token has expired for iOS devices).  
\- If the client app is updated but the new version is not configured to receive messages.  
For all these cases, remove this registration token from the app server and stop using it to send messages.  
`SENDER_ID_MISMATCH` (HTTP error code = 403) The authenticated sender ID is different from the sender ID for the registration token. | A registration token is tied to a certain group of senders. When a client app registers for FCM, it must specify which senders are allowed to send messages. You should use one of those sender IDs when sending messages to the client app. If you switch to a different sender, the existing registration tokens won't work.  
`QUOTA_EXCEEDED` (HTTP error code = 429) Sending limit exceeded for the message target. An extension of type `google.rpc.QuotaFailure` is returned to specify which quota was exceeded. | This error can be caused by exceeded message rate quota, exceeded device message rate quota, or exceeded topic message rate quota.  
**Message rate exceeded** : The sending rate of messages is too high. You must reduce the overall rate at which you send messages. Use exponential backoff with a minimum initial delay of 1 minute to retry rejected messages.  
**Device message rate exceeded** : The rate of messages to a particular device is too high. See [message rate limit to a single device. Reduce the number of messages sent to this device and use exponential backoff to retry sending.  
**Topic message rate exceeded** : The rate of messages to subscribers to a particular topic is too high. Reduce the number of messages sent for this topic and use exponential backoff with a minimum initial delay of 1 minute to retry sending.](https://firebase.google.com/docs/cloud-messaging/throttling-and-quotas#device_throttling)  
`UNAVAILABLE` (HTTP error code = 503) The server is overloaded. | The server couldn't process the request in time. Retry the same request, but you must:  
\- Honor the Retry-After header if it is included in the response from the FCM Connection Server.  
\- Implement exponential backoff in your retry mechanism. (e.g. if you waited one second before the first retry, wait at least two seconds before the next one, then 4 seconds and so on). If you're sending multiple messages, consider applying jittering. For more information, see [Handling retries, or check the [FCM status dashboard](https://status.firebase.google.com/cloud-messaging/) to identify if there are any ongoing service disruptions affecting FCM. Senders that cause problems risk being denylisted.](https://firebase.google.com/docs/cloud-messaging/scale-fcm#exponential_backoff)  
`INTERNAL` (HTTP error code = 500) An unknown internal error occurred. | The server encountered an error while trying to process the request. You could retry the same request following suggestions in [Handling retries or checking the [FCM status dashboard](https://status.firebase.google.com/cloud-messaging/). to identify if there are any ongoing service disruptions affecting FCM. If the error persists, please contact Firebase support.](https://firebase.google.com/docs/cloud-messaging/scale-fcm#exponential_backoff)  
`THIRD_PARTY_AUTH_ERROR` (HTTP error code = 401) APNs certificate or web push auth key was invalid or missing. | A message targeted to an iOS device or a web push registration could not be sent. Check the validity of your development and production credentials.  
  
## Admin SDK error codes

The following table lists the Firebase Admin FCM API error codes and their descriptions, including recommended resolution steps.

Error Code | Description and Resolution Steps  
---|---  
`messaging/invalid-argument` |  An invalid argument was provided to an FCM method. The error message should contain additional information.   
`messaging/invalid-recipient` |  The intended message recipient is invalid. The error message should contain additional information.   
`messaging/invalid-payload` |  An invalid message payload object was provided. The error message should contain additional information.   
`messaging/invalid-data-payload-key` |  The data message payload contains an invalid key. See the reference documentation for [ `DataMessagePayload`](/docs/reference/admin/node/firebase-admin.messaging.datamessagepayload) for restricted keys.   
`messaging/payload-size-limit-exceeded` |  The provided message payload exceeds the FCM size limits. The limit is 4096 bytes for most messages. For messages sent to topics, the limit is 2048 bytes. The total payload size includes both keys and values.   
`messaging/invalid-options` |  An invalid message options object was provided. The error message should contain additional information.   
`messaging/invalid-registration-token` |  Invalid registration token provided. Make sure it matches the registration token the client app receives from registering with FCM. Don't truncate or add additional characters to it.   
`messaging/registration-token-not-registered` |  The provided registration token is not registered. A previously valid registration token can be unregistered for a variety of reasons, including: 

  * The client app unregistered itself from FCM. 
  * The client app was automatically unregistered. This can happen if the user uninstalls the application or, on Apple platforms, if the APNs Feedback Service reported the APNs token as invalid. 
  * The registration token expired. For example, Google might decide to refresh registration tokens or the APNs token may have expired for Apple devices. 
  * The client app was updated, but the new version is not configured to receive messages. 

For all these cases, remove this registration token and stop using it to send messages.   
`messaging/invalid-package-name` |  The message was addressed to a registration token whose package name does not match the provided [ `restrictedPackageName`](/docs/reference/admin/node/firebase-admin.messaging.messagingoptions#messagingoptionsrestrictedpackagename) option.   
`messaging/message-rate-exceeded` |  The rate of messages to a particular target is too high. Reduce the number of messages sent to this device or topic and don't immediately retry sending to this target.   
`messaging/device-message-rate-exceeded` |  The rate of messages to a particular device is too high. Reduce the number of messages sent to this device and don't immediately retry sending to this device.   
`messaging/topics-message-rate-exceeded` |  The rate of messages to subscribers to a particular topic is too high. Reduce the number of messages sent for that topic, and don't immediately retry sending to that topic.   
`messaging/topics-subscription-rate-exceeded` |  The rate of subscription management requests to a particular topic is too high. Reduce the number of requests sent for that topic, and don't immediately retry the request.   
`messaging/too-many-topics` |  A registration token has been subscribed to the maximum number of topics and cannot be subscribed to any more.   
`messaging/invalid-apns-credentials` |  A message targeted to an Apple device couldn't be sent because the required APNs SSL certificate was not uploaded or has expired. Check the validity of your development and production certificates.   
`messaging/mismatched-credential` |  The credential used to authenticate this SDK does not have permission to send messages to the device corresponding to the provided registration token. Make sure the credential and registration token both belong to the same Firebase project. See [Add Firebase to your app](/docs/admin/setup#prerequisites) for documentation on how to authenticate the Firebase Admin SDKs.   
`messaging/authentication-error` |  The SDK couldn't authenticate to the FCM servers. Make sure you authenticate the Firebase Admin SDK with a credential which has the proper permissions to send FCM messages. See [Add Firebase to your app](/docs/admin/setup#prerequisites) for documentation on how to authenticate the Firebase Admin SDKs.   
`messaging/server-unavailable` |  The FCM server couldn't process the request in time. You should retry the same request, but you must: 

  * Honor the `Retry-After` header if it is included in the response from the FCM Connection Server. 
  * Implement exponential back-off in your retry mechanism. For example, if you waited one second before the first retry, wait at least two seconds before the next one, then four seconds, and continue to raise the seconds interval. If you're sending multiple messages, delay each one independently by an additional random amount to avoid issuing a new request for all messages at the same time. 

Senders that cause problems risk being blocklisted.   
`messaging/internal-error` |  The FCM server encountered an error while trying to process the request. You could retry the same request following the requirements listed in the earlier `messaging/server-unavailable` row. If the error persists, please report the problem to our [Bug Report](/support/contact/bugs-features) support channel.   
`messaging/unknown-error` |  An unknown server error was returned. See the raw server response in the error message for more details. If you receive this error, please report the full error message to our [Bug Report](/support/contact/bugs-features) support channel.   
  
Send feedback 
