  * [ Firebase ](https://firebase.google.com/)
  * [ Documentation ](https://firebase.google.com/docs)
  * [ FCM ](https://firebase.google.com/docs/cloud-messaging)
  * [ Run ](https://firebase.google.com/docs/run)



Send feedback 

#  Best practices for FCM registration management Stay organized with collections  Save and categorize content based on your preferences. 

**Note:** Firebase Cloud Messaging is transitioning from **registration tokens** to a registration system based on [**Firebase Installation IDs (FIDs)**](/docs/projects/manage-installations) to identify and target app instances for per-instance message sends. To ensure a smooth transition, both patterns are fully co-supported, so the best practices in this guide apply to both FID-based registrations and legacy registration tokens (unless clarified). For clarity and future-proofing, the examples and API references in this guide focus on FIDs.

If you use FCM APIs to build send requests programmatically, you may find that, over time, you are wasting resources by sending messages to inactive devices with stale registrations. This situation can affect the message delivery data reported in the Firebase console or data exported to BigQuery, showing up as a dramatic (but not actually valid) drop in delivery rates. This guide discusses some measures you can take to help ensure efficient message targeting and valid delivery reporting.

## Stale and expired registrations

Stale registrations are associated with inactive devices that have not connected to FCM for over a month. As time passes, it becomes less and less likely for the device to ever connect to FCM again. Message sends and topic fanouts for these stale registrations are unlikely to ever be delivered.

There are several reasons why a registration can become stale. For example, the device the registration is associated with may be lost, destroyed, or put into storage and forgotten.

For Android, when a registration has been inactive for 270 days, FCM considers it **expired** and garbage collects it. Once a registration is expired, FCM marks it as invalid and rejects sends to it. Note that Firebase Installation IDs (FIDs) themselves are managed by [the Firebase Installations service](/docs/projects/manage-installations) (FIS), not by FCM. In the rare case that a device connects again and the app is opened after its registration has been garbage collected, the client app registers again with FCM using the FID retrieved from FIS. Note that the FID may change; see [Manage Firebase Installations](/docs/projects/manage-installations#monitor-id-lifecycle) for details on when FIDs are reissued.

For other platforms like iOS, FCM relies on the underlying push service (e.g., APNs), which does not have the same 270-day inactivity-based expiration. We recommend that you proactively maintain registration freshness and remove stale registrations.

## Basic best practices

There are some fundamental practices you should follow in any app that uses FCM APIs to build send requests programmatically. The main best practices are:

  * **[Retrieve Firebase Installation IDs (FIDs)](/docs/cloud-messaging/android/get-started#access-firebase-installation-id) from FCM and store them on your app server.** An important role for the server is to keep track of each client's registered FID and keep an updated list of active FIDs. We strongly recommend implementing a registration timestamp in your database, and updating it whenever a registration is uploaded.
  * **Maintain registration freshness and remove stale registrations.** In addition to removing registrations that FCM no longer considers valid, you may want to monitor other signs that registrations have become stale and remove them proactively. This guide discusses some of your options for achieving this.



## Retrieve and store Firebase Installation IDs

On initial startup of your app, the FCM SDK registers the app instance with FCM and returns a Firebase Installation ID (FID). This is the identifier that you must include in targeted send requests from the API, or use for topic subscriptions.

We strongly recommend saving the FID to your app server alongside a timestamp whenever it is uploaded. By updating the timestamp on every upload request, your server knows when the app instance was last opened and successfully synchronized with the FCM backend.

Depending on whether auto-initialization is enabled or disabled (including not supported), you should handle registration and updates as follows:

  * **(Recommended) When auto-initialization is enabled:** The SDK automatically keeps the registration fresh and monitors changes. The [`onRegistered()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService#onRegistered\(java.lang.String\)) callback is invoked regularly on routine syncs during app startup, as well as when FID changes occur. Simply implement this callback to upload the FID to your server and save the current timestamp.
  * **When auto-initialization is disabled:** The [`onRegistered()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService#onRegistered\(java.lang.String\)) callback won't be automatically invoked at start. To track registrations and keep them fresh, call [`register()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessaging#register\(\)) on app startup; for example, on Android, in the main activity's `onCreate()`. A successful call triggers the FCM registration process using the FID and delivers it to your [`onRegistered()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService#onRegistered\(java.lang.String\)) callback, allowing your app to upload the FID and update the timestamp on your server.



### Example: store FIDs and timestamps in Cloud Firestore

For example, you could use Cloud Firestore to store FIDs in a collection called `fcmRegistrations`. Each document ID in the collection corresponds to a user ID, and the document stores the current FID and its last-updated timestamp. Use the `set` function as shown in this Kotlin example:
    
    
    private fun sendRegistrationToServer(installationId: String?) {
        // If you're running your own server, call API to send registration details and today's date for the user
    
        // Example shown uses Firestore
        // Add FID and timestamp to Firestore for this user
        val deviceFid = hashMapOf(
            "installationId" to installationId,
            "timestamp" to FieldValue.serverTimestamp(),
        )
        // Get user ID from Firebase Auth or your own server
        Firebase.firestore.collection("fcmRegistrations").document("myuserid")
            .set(deviceFid)
    }
    

Whenever a Firebase Installation ID is successfully registered or updated, the [`onRegistered()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService#onRegistered\(java.lang.String\)) callback is invoked. You should implement this callback to upload the FID and update the timestamp:
    
    
    override fun onRegistered(installationId: String) {
        Log.d(TAG, "Registered installation ID: $installationId")
    
        // Send the Firebase Installation ID (FID) to your app server. Your app
        // server should save the FID and update the timestamp upon receipt.
        sendRegistrationToServer(installationId)
    }
    

For instances where auto-initialization is disabled, call [`register()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessaging#register\(\)) on app startup (e.g., in `onCreate()`) to trigger the registration flow and FID delivery through [`onRegistered()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService#onRegistered\(java.lang.String\)):
    
    
    // Trigger manual registration if auto-initialization is turned off.
    FirebaseMessaging.getInstance().register()
        .addOnCompleteListener(this) { task ->
            if (task.isSuccessful) {
                // The registration callback onRegistered() will be invoked with the current FID.
            } else {
                Log.w(TAG, "Failed to register with Firebase Cloud Messaging", task.exception)
            }
        }
    

## Maintain registration freshness and remove stale registrations

Determining whether a registration is fresh or stale is not always straightforward. To cover all cases, you should adopt a threshold for when you consider registrations stale. By default, FCM considers a registration to be stale if its app instance hasn't connected for a month. Any registration older than one month is likely to be an inactive device; an active device would have otherwise refreshed its registration.

Depending on your use case, one month may be too short or too long, so it is up to you to determine the criteria that works for you.

### Detect invalid responses from the FCM backend

Make sure to detect invalid responses from FCM and respond by deleting from your system any registrations that are known to be invalid or have expired. With the HTTP v1 API, these error messages may indicate that your send request targeted invalid or expired registrations:

  * `UNREGISTERED` (HTTP 404)
  * `INVALID_ARGUMENT` (HTTP 400)

**Note:** `INVALID_ARGUMENT` can also be returned in cases of issues in the message payload, so it signals an invalid registration only if the payload is completely valid. See [ErrorCodes](/docs/reference/fcm/rest/v1/ErrorCode) for more information.

If you are certain that the message payload is valid and you receive either of these responses for a targeted registration, it is safe to delete your record of this registration, since it will never again be valid. For example, to delete invalid registrations from Cloud Firestore, you could deploy and run a function like the following:
    
    
            // Firebase Installation ID comes from the client FCM SDKs
            const firebaseInstallationId = 'YOUR_FIREBASE_INSTALLATION_ID';
    
            const message = {
                data: {
                    // Information you want to send inside of notification
                },
                fid: firebaseInstallationId
            };
    
            // Send message to device with provided Firebase Installation ID
            getMessaging().send(message)
            .then((response) => {
                // Response is a message ID string.
            })
            .catch((error) => {
                // Delete registration for user if error code is UNREGISTERED or INVALID_ARGUMENT.
                if (error.errorCode == "messaging/registration-token-not-registered") {
                    // If you're running your own server, call API to delete the registration for the user
                    // Example shown uses Firestore
                    // Get user ID from Firebase Auth or your own server
                    Firebase.firestore.collection("fcmRegistrations").document(user.uid).delete()
                }
            });
    

FCM returns an invalid response if a registration for an Android device has expired after 270 days of inactivity, or if a client explicitly unregistered. If you need to more accurately track staleness according to your own definitions, you can proactively remove stale registrations.

### Update registrations on a regular basis

Regardless of whether your registrations are based on FIDs or legacy registration tokens, your server should always update the registration timestamp in your database on every upload request. This timestamp acts as a signal for the app installation, letting the client has successfully opened the app and synced with the FCM backend. Depending on the APIs you are using, implement the appropriate strategy:

#### The Firebase Installation ID APIs (recommended)

For client apps using the FID APIs, you **do not** need to schedule periodic background jobs in your client app to retrieve or refresh registrations. The SDK automatically takes care of refreshes under auto-initialization, regularly delivering the correct current FID to your [`onRegistered()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService#onRegistered\(java.lang.String\)) callback on routine syncs during app startups.

To keep your server updated, implement the startup upload strategies detailed in Retrieve and store Firebase Installation IDs:

  * **Auto-initialization enabled:** The SDK automatically ensures that the latest FID is sent to your server on routine syncs during app starts.
  * **Auto-initialization disabled or not supported:** Call [`register()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessaging#register\(\)) on app startup (for example, on Android, in the main activity's `onCreate()`) to force the registration sequence and trigger FID delivery to your [`onRegistered()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService#onRegistered\(java.lang.String\)) callback.



These strategies guarantee your server always has the latest active FID and can recover from failed uploads automatically, making the application highly resilient.

#### The deprecated registration token APIs

If you are using legacy registration tokens, the client SDK does not automatically manage refreshes on routine syncs. Therefore, we recommend that you periodically retrieve and update all registration tokens on your server. This requires you to:

  * Add app logic in your client app to retrieve the current token using the appropriate API call (such as [`token(completion):`](/docs/reference/swift/firebasemessaging/api/reference/Classes/Messaging) for Apple platforms or [`getToken()`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessaging#getToken\(\)) for Android) and then send the current token to your app server for storage (with a timestamp). This could be a monthly job configured to cover all clients or tokens.
  * Add server logic to update the token's timestamp at regular intervals, regardless of whether or not the token has changed.



For an example of Android logic for updating legacy tokens using [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager), see [Managing Cloud Messaging Tokens](https://firebase.blog/posts/2023/04/managing-cloud-messaging-tokens/#updating-registration-tokens) on the Firebase blog.

Whatever timing pattern you follow, make sure to update tokens periodically. An update frequency of once per month strikes a good balance between battery impact and detecting inactive registration tokens. By doing this refresh, you also ensure that any device which goes inactive will refresh its registration when it becomes active again. There is no benefit to doing the refresh more frequently than weekly.

### Remove stale registrations

Before sending messages to a device, ensure that the timestamp of the device's registration is within your staleness window period. For example, you could implement Cloud Functions for Firebase to run a daily check to ensure that the timestamp is within a defined staleness window period such as `const EXPIRATION_TIME = 1000 * 60 * 60 * 24 * 30;` and then remove stale registrations:
    
    
    exports.pruneRegistrations = functions.pubsub.schedule('every 24 hours').onRun(async (context) => {
      // Get all documents where the timestamp exceeds is not within the past month
      const staleRegistrationsResult = await admin.firestore().collection('fcmRegistrations')
          .where("timestamp", "<", Date.now() - EXPIRATION_TIME)
          .get();
      // Delete devices with stale registrations
      staleRegistrationsResult.forEach(function(doc) { doc.ref.delete(); });
    });
    

exports.pruneTokens = functions.pubsub.schedule('every 24 hours').onRun(async (context) => { // Get all documents where the timestamp exceeds is not within the past month const staleTokensResult = await admin.firestore().collection('fcmTokens') .where("timestamp", "<", Date.now() - EXPIRATION_TIME) .get(); // Delete devices with stale tokens staleTokensResult.forEach(function(doc) { doc.ref.delete(); }); });

[index.js](https://github.com/firebase/quickstart-android/blob/0b77e46545ef38b040d140f360cfe3f75b54e15d/messaging/functions/index.js#L18-L25)

## Unsubscribe stale registrations from topics

If you use topics, you may also want to unsubscribe stale registrations from the topics to which they are subscribed. This involves two steps:

  1. Your app should resubscribe to topics whenever the Firebase Installation ID (FID) changes. This lets the subscriptions reappear automatically when an app becomes active again.
  2. If an app instance is idle for one month (or your own staleness window) you should unsubscribe it from topics using the [Firebase Admin SDK](/docs/cloud-messaging/manage-topic-subscriptions#manage-topic-subscriptions-admin-sdk) to delete the Firebase Installation ID to topic mapping from the FCM backend.



The benefit of these two steps is that your fanouts will occur faster since there are fewer stale registrations to fan out to, and your stale app instances will automatically resubscribe once they are active again.

## Measure delivery success

To get the most accurate picture of message delivery, it is best to only send messages to actively used app instances. This is especially important if you regularly send messages to topics with large numbers of subscribers; if a portion of those subscribers are actually inactive, the impact on your delivery statistics can be significant over time.

Before targeting messages to an app instance, consider:

  * Do Google Analytics, data captured in BigQuery, or other tracking signals indicate the registration is active?
  * Have previous delivery attempts failed consistently over a period of time?
  * Has the Firebase Installation ID been updated on your servers in the past month?
  * For Android devices, does the [FCM Data API](/docs/reference/fcmdata/rest) report a high percentage of message delivery failures due to [`droppedDeviceInactive`](/docs/reference/fcmdata/rest/v1beta1/projects.androidApps.deliveryData/list#messageoutcomepercents)?



For more information about delivery, see [Understanding message delivery](/docs/cloud-messaging/understand-delivery).

Send feedback 
