  * [ Firebase ](https://firebase.google.com/)
  * [ Documentation ](https://firebase.google.com/docs)
  * [ FCM ](https://firebase.google.com/docs/cloud-messaging)
  * [ Run ](https://firebase.google.com/docs/run)



#  Your server environment and FCM Stay organized with collections  Save and categorize content based on your preferences. 

The server side of Firebase Cloud Messaging consists of two components:

  * The **FCM backend** provided by Google.
  * Your **app server** or other **trusted server environment** where your server logic runs, such as [Cloud Functions for Firebase](/docs/functions) or other cloud environments managed by Google.

**Tip:** If you need to configure your enterprise network or VPN to allow traffic to and from FCM servers, see [Configure your Network for FCM](/docs/cloud-messaging/network-configuration).

Your app server or trusted server environment sends message requests to the FCM backend, which then routes messages to client apps running on users' devices.

Using the Firebase Admin SDK or FCM app server protocols, you can build message requests and send them to these types of targets:

  * Topic name
  * Condition
  * FCM registration token
  * Device group name ([deprecated](/docs/cloud-messaging/troubleshooting#fcm-26-deprecation), will be removed on September 29, 2027)



You can send messages with a notification payload made up of predefined fields, a data payload of your own user-defined fields, or a message containing both types of payload. See [Message types](/docs/cloud-messaging/customize-messages/set-message-type) for more information.

## Requirements for the trusted server environment

Your app server environment must meet the following criteria:

  * Able to send properly formatted message requests to the FCM backend.
  * Able to handle requests and resend them using [exponential back-off.](https://developers.google.com/api-client-library/java/google-http-java-client/backoff)
  * Able to securely store server authorization credentials and client registration tokens.



## Required credentials for Firebase project

Depending on which FCM features you implement, you may need the following credentials from your Firebase project:

Credential | Description  
---|---  
Project ID  | A unique identifier for your Firebase project, used in requests to the FCM v1 HTTP endpoint. This value is available in the [Firebase console **Settings**](//console.firebase.google.com/project/_/settings/general) pane.  
Registration token  | A unique token string that identifies each client app instance. The registration token is required for single app instance and device group messaging. Note that registration tokens must be kept secret.  
Sender ID  | A unique numerical value created when you create your Firebase project, available in the [Cloud Messaging](//console.firebase.google.com/project/_/settings/cloudmessaging/) tab of the Firebase console **Settings** pane. The sender ID is the same as the project number. The sender ID is used to identify each sender that can send messages to the client app.  
Access token  | A short-lived OAuth 2.0 token that authorizes requests to the HTTP v1 API. This token is associated with a service account that belongs to your Firebase project. To create and rotate access tokens, follow the steps described in [Authorize Send Requests](/docs/cloud-messaging/send/v1-api#authorize-http-v1-send-requests).  
**Important:** Send requests for both the Firebase Admin SDK and v1 HTTP protocol must contain the project ID of the Firebase project for your app, available in the [General project settings](https://console.firebase.google.com/project/_/settings/general/) tab of the Firebase console. Also, both methods of sending messages require you to [authorize send requests](/docs/cloud-messaging/send/v1-api#authorize-http-v1-send-requests).

## Choose a server option

You'll need to decide on a way to interact with FCM servers: either using the Firebase Admin SDK or the FCM HTTP v1 API. Because of its support across popular programming languages and its convenience methods for handling authentication and authorization, the Firebase Admin SDK is the recommended method.

Options for interacting with FCM servers include the following:

  * The Firebase Admin SDK, which has support for [Node](/docs/reference/admin/node/firebase-admin.messaging), [Java](/docs/reference/admin/java/reference/com/google/firebase/messaging/package-summary), [Python](/docs/reference/admin/python/firebase_admin.messaging), [C#](/docs/reference/admin/dotnet/namespace/firebase-admin/messaging), and [Go](//godoc.org/firebase.google.com/go/messaging).

  * The [FCM HTTP v1 API](/docs/reference/fcm/rest/v1/projects.messages), a REST API with secure authorization and flexible [cross-platform messaging capabilities](/docs/cloud-messaging/customize-messages/cross-platform) (the Firebase Admin SDK is based on this protocol and provides all of its inherent advantages).




### Firebase Admin SDK

The Firebase Admin SDK handles authenticating with the backend and facilitates sending messages and managing topic subscriptions. With the Firebase Admin SDK, you can:

  * Send messages to individual app instances
  * Send messages to topics and condition statements that match one or more topics
  * Send messages to device groups
  * Subscribe and unsubscribe app instances to and from topics
  * Construct message payloads tailored to different target platforms



To set up the Firebase Admin SDK, see [Add the Firebase Admin SDK to Your Server](/docs/admin/setup). If you already have a Firebase project, start with [Add the SDK](/docs/admin/setup#add-sdk). Also, make sure to enable the Firebase Cloud Messaging API (V1) in the [Cloud Messaging settings page](//console.firebase.google.com/project/_/settings/cloudmessaging/) for your project. Then, once the Firebase Admin SDK is installed, you can start writing logic to [build send requests](/docs/cloud-messaging/send/admin-sdk).

### FCM HTTP v1 API

FCM provides the [FCM HTTP v1 API](/docs/reference/fcm/rest/v1/projects.messages) for developers who prefer a raw server protocol.

To send a message, the app server issues a POST request with an HTTP header and an HTTP body comprised of JSON key value pairs. For details on the header and body options, see [Send a Message using FCM HTTP v1 API](/docs/cloud-messaging/send/v1-api).
