  * [ Firebase ](https://firebase.google.com/)
  * [ Documentation ](https://firebase.google.com/docs)
  * [ FCM ](https://firebase.google.com/docs/cloud-messaging)
  * [ Run ](https://firebase.google.com/docs/run)



Send feedback 

#  Firebase Cloud Messaging message types Stay organized with collections  Save and categorize content based on your preferences. 

With FCM, you can send two types of messages to your client apps:

  * Notification messages, similar to "display messages", are handled by the FCM SDK automatically.
  * Data messages, which are handled by the client app.



Notification messages contain a predefined set of user-visible keys and can contain an optional data payload. Data messages, by contrast, contain only your user-defined custom key-value pairs. Maximum payload for both message types is 4096 bytes, except when sending messages from the Firebase console, which enforces a 1000 character limit.

| Use scenario | How to send  
---|---|---  
Notification message | FCM SDK displays the message to end-user devices on behalf of the client app when it's running in the background. Otherwise, if the app is running in the foreground when the notification is received, the app's code determines the behavior.  | 

  1. In a trusted environment such as [Cloud Functions](/docs/functions) or your app server, use the [Firebase Admin SDK](/docs/cloud-messaging/send/admin-sdk) or the [HTTP v1 API](/docs/cloud-messaging/send/v1-api). Set the `notification` key. May have optional data payload. Always [collapsible](/docs/cloud-messaging/customize-messages/collapsible-message-types). See some [ examples of display notifications](/docs/cloud-messaging/customize-messages/cross-platform#notification-message-color-icon) and send request payloads. 
  2. Use the [ Notifications composer](//console.firebase.google.com/project/_/notification): Enter the Message Text, Title, etc., and send. Add optional data payload by providing Custom data. 

  
Data message | Client app is responsible for processing data messages. Data messages have only custom key-value pairs with no reserved key names (see below).  | In a trusted environment such as [ Cloud Functions](/docs/functions) or your app server, use the [Firebase Admin SDK](/docs/cloud-messaging/send/admin-sdk) or the [HTTP v1 API](/docs/cloud-messaging/send/v1-api). In the send request, Set the `data` key.   
  
You can use notification messages when you want the FCM SDK to handle displaying a notification automatically when your app is running in the background. FCM can send a notification message with an optional data payload. In such cases, FCM displays the notification payload, and the client app handles the data payload.

You can use data messages when you want to process the messages with your own client app code.

**Note:** To learn more, see the [Message handling and deprioritization on Android](/docs/cloud-messaging/android-message-priority#deprioritize) page to make sure your notifications reach your users on Android

## Notification messages

You can send notification messages using the [Firebase console](/docs/cloud-messaging/send/firebase-console), the [ Firebase Admin SDK](/docs/cloud-messaging/send/admin-sdk), or the [FCM HTTP v1 API](/docs/cloud-messaging/send/v1-api). The Firebase console provides analytics-based [A/B testing](/docs/ab-testing/abtest-with-console) to help you refine and improve your notification messages.

To send notification messages using the Firebase Admin SDK or the FCM HTTP v1 API, set the `notification` key with the predefined set of key-value options of the notification message. You can use the following example to format a notification message in an IM app
    
    
    {
      "message":{
        "token":"bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1...",
        "notification":{
          "title":"Portugal vs. Denmark",
          "body":"great match!"
        }
      }
    }
    

Notification messages are delivered to the notification tray when the app is in the background. For apps in the foreground, messages are handled by a callback function.

You can use the [FCM HTTP v1 API notification object](/docs/reference/fcm/rest/v1/projects.messages#Notification) reference documentation for the full list of predefined keys available for building notification messages.

## Data messages

**Important:** While the connection to FCM is encrypted, it is not end-to-end encrypted. For sensitive data, you should implement your own end-to-end encryption. To learn more, see [Secure Your Message Data with End-to-End Encryption](/docs/cloud-messaging/encryption).

It is up to you how you want to use the FCM payload `data` to implement your encryption scheme of choice. Make sure that you don't use any reserved words in your custom key-value pairs. Reserved words include `from`, `message_type`, or any word starting with `google.`, `gcm.` or `gcm.notification.`.

The following example shows usage of the top-level, or common data field, which is interpreted by clients on all platforms that receive the message. On each platform, the client app receives the data payload in a callback function
    
    
    {
      "message":{
        "token":"bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1...",
        "data":{
          "Nick" : "Mario",
          "body" : "great match!",
          "Room" : "PortugalVSDenmark"
        }
      }
    }
    

## Notification messages with optional data payload

You can send notification messages that contain an optional payload of custom key-value pairs programmatically or using the Firebase console. In the [Notifications composer](//console.firebase.google.com/project/_/notification), use the **Custom data** fields in **Advanced options**.

App behavior when receiving messages that include both notification and data payloads depends on whether the app is in the background or the foreground—essentially, whether or not it is active at the time of receipt.

  * **When in the background** , apps receive the notification payload in the notification tray, and only handle the data payload when the user taps on the notification.
  * **When in the foreground** , your app receives a message object with both payloads available.



Here is a JSON-formatted message containing both the `notification` key and the `data` key:
    
    
    {
      "message":{
        "token":"bk3RNwTe3H0:CI2k_HHwgIpoDKCIZvvDMExUdFQ3P1...",
        "notification":{
          "title":"Portugal vs. Denmark",
          "body":"great match!"
        },
        "data" : {
          "Nick" : "Mario",
          "Room" : "PortugalVSDenmark"
        }
      }
    }
    

Send feedback 
