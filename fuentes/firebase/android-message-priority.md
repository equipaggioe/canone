  * [ Firebase ](https://firebase.google.com/)
  * [ Documentation ](https://firebase.google.com/docs)
  * [ FCM ](https://firebase.google.com/docs/cloud-messaging)
  * [ Run ](https://firebase.google.com/docs/run)



#  Set and manage Android message priority Stay organized with collections  Save and categorize content based on your preferences. 

You have two options for assigning delivery priority to downstream messages on Android: normal and high priority. Delivery of normal and high priority messages works like this:

  * **Normal priority.** This is the default priority for data and notification messages. Normal priority messages are delivered immediately when the device is not sleeping. When the device is in [Doze mode](//developer.android.com/training/monitoring-device-state/doze-standby#understand_doze), delivery may be delayed to conserve battery until the device exits doze. For less time-sensitive messages, such as notifications of new email, keeping your UI in sync, or syncing app data in the background, choose normal delivery priority. 

  * **High priority.** FCM attempts to deliver high priority messages immediately, allowing FCM to wake a sleeping device when necessary and to run some limited processing (including very limited network access). High priority messages generally should result in user interaction with your app or its notifications.




## Deciding between high and normal priority messages

While normal priority messages are suitable for general updates, choose high priority when you need to ensure immediate delivery for urgent matters or actions. Since the delivery time for normal priority messages can be impacted by Doze mode, setting most of your user visible notifications to high priority will ensure they are delivered promptly. For example, notifications such as, chat messages, problems with an account, or food delivery updates, should be set to high priority.

### Message processing for high and normal priority messages

For both high priority and normal priority messages received on an Android device, several seconds are given to process the message payload in the `onMessageReceived` handler, with slightly more time allocated for high priority messages than normal priority ones. This time is only expected to be long enough to immediately render a notification. If you have to do any additional work such as loading an image from device storage or calling your servers to collect additional content you will need to take additional steps.

The `onMessageReceived` method is called on a separate worker thread. As best practice, you should process the message payload and display a notification immediately within the `onMessageReceived` method. You shouldn't be making additional asynchronous network calls or doing payload processing on a separate thread within the `onMessageReceived` method, doing so can cause your application to be outside of a [valid process lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle) before the payload is fully processed. If this happens, you may see that certain FCM messages that are sent result in delayed or missing notifications.

If you do need additional time to process for your message, for example to fetch an `imageUrl` contained in your message payload, you will need to use a construct such as `WorkManager` or foreground service to extend the application lifecycle. You should use the following guidance when you [override the `onMessageReceived` method](/docs/cloud-messaging/android/receive#override-onmessagereceived) to verify your notifications are fully processed.

  * **For high priority notifications:** Start an [expedited job](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) using the Android `WorkManager` to verify that your high priority notification gets prioritized processing time to verify your notification rendering runs to completion. The good news is that if you're worried about exhausting [expedited job quotas](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work#quotas) as a result of high priority FCM processing, you don't need to be. There is a brief exemption for expedited jobs scheduled immediately after a high priority FCM `onMessageReceived` is dispatched.
  * **For normal priority notifications:** Start a [regular `WorkRequest`](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work#Overview) using the Android `WorkManager` instead. This will verify that the additional work required to process your notification gets processed eventually, without utilizing prioritized processing and causing unneeded battery usage issues.



## Setting priority for messages

You can send notifications to your users using the Admin SDK, the FCM REST API, and the Firebase console. To change your priority setting from the Admin SDK and FCM REST API, you have to update the message JSON payload. You can use the following code sample to see how to set the priority to high. For notifications sent from the console, setting Android-specific notification fields isn't supported.
    
    
     {
      "message": {
          "notification": {
              "body": "Purchase exceeding $500 detected",
              "title": "Credit card purchase"
          },
          "data": {
              "purchaser": "Your child",
              "items": "Gravity Defier Sneakers"
          },
          "android": {
              "priority": "high"
          },
          "apns": {
              "headers": {
                  "apns-priority": "5"
              }
          }
      }
    }
    

### Test your high priority notifications in Doze mode

To make sure your high priority notifications are being received and processed correctly when received by a user, follow these instructions to test your notifications:

  1. Set your device to Doze mode using the instructions in [Test your app with Doze](https://developer.android.com/training/monitoring-device-state/doze-standby#testing_doze).
  2. Access your FCM registration token from your app on the test device. For more information on how to access the token, see [Send a test message to a background app](/docs/cloud-messaging/android/get-started#access-fcm-registration-token).
  3. Once you have the FCM token, send your high priority notification to the test device using your FCM notification sending code or a [cURL command](https://firebaseopensource.com/projects/firebase/quickstart-js/messaging/readme) that has configuration parameters matching your high priority notification.



## Deprioritization of high priority FCM on Android

High priority messages on Android are meant for time sensitive, user visible content, and should result in user-facing notifications. If FCM detects a pattern in which messages don't result in user-facing notifications, your messages may be deprioritized to normal priority or delegated for handling by Google Play services.

FCM uses 7 days of message behavior when determining whether to deprioritize or proxy messages; it makes this determination independently for every instance of your application. If, in response to high priority messages, notifications are displayed in a way that is visible to the user, then your future high-priority messages won't be affected.

### Notification delegation with Google Play services

High priority notification messages that meet certain criteria are proxied by Google Play services instead of being deprioritized. This means that the notifications are displayed by Google Play services on behalf of the app, without any need to start the app. This is done to provide a better overall user experience on Android devices.

Note that proxied notification messages introduce changes in how analytics related to messages being received are reported:

  * In order for analytics for proxied notifications to be reported, your app must use FCM SDK version 24.0.0 or higher.
  * You may notice delays or drops in the number of messages received versus the number prior to the introduction of proxied notifications. This is because analytics for proxied notifications are only reported once your app starts, and might not be reported at all if the notification doesn't result in the app opening.



Proxying notification messages in this way is the default behavior for apps using Android Q+ and Google Play services version 19054000 or later. Messages sent through HTTP v1 API are proxied, but messages sent through the Firebase console or legacy APIs _will not be proxied_. Note that this feature is currently in Beta, and is subject to change.

Though we strongly recommend leaving delegation enabled for its benefits to device battery and memory, you can opt out of this behavior in any of these ways:

  * On an app-level basis: in your app manifest, add the directive `<meta-data android:name= "delivery_metrics_exported_to_big_query_enabled" android:value="false"/>`.
  * On an app instance basis: For the app instance, set `fun setNotificationDelegationEnabled(disable: Boolean): Task<Void!>` in the UI flow for your app, depending on the specific use case.
  * On a per-message basis: Set the `proxy` key to `DENY` in the `AndroidNotification` object for the send request.



### Measuring message deprioritization on Android

  * **Individual Messages.** On delivery, you can determine whether an individual message was deprioritized or not by comparing its delivered priority, from [getPriority()](/docs/reference/android/com/google/firebase/messaging/RemoteMessage#getPriority\(\)), with its original priority, from [getOriginalPriority()](/docs/reference/android/com/google/firebase/messaging/RemoteMessage#getOriginalPriority\(\)).

  * **All Messages.** The [FCM Aggregate Delivery Data API](/docs/cloud-messaging/understand-delivery#aggregated-delivery-data) can report what percentage of all your messages to Android are being deprioritized. Some messages may be omitted from the aggregate data reports, but overall they should give a global view of message deprioritization rates. See our article on [aggregated delivery data](https://medium.com/firebase-developers/what-is-fcm-aggregated-delivery-data-d6d68396b83b) for more information and sample code for querying the API; it can also be explored from the [API explorer](/docs/reference/fcmdata/rest/v1beta1/projects.androidApps.deliveryData/list).

  * **Proxied Notifications.** Proxied notifications won't be counted in current FCM or GA delivery metrics, so you may experience a drop of up to 15% in notification delivery metrics. For reporting on proxied messages, use the [FCM Aggregate Delivery Data API](/docs/cloud-messaging/understand-delivery#aggregated-delivery-data). `ProxyNotificationInsightPercents` reports the percentage of successfully proxied notifications as well as details for messages that can't be successfully proxied.




### Troubleshooting Notification Delays

  * **Ensure that your app instance has notifications enabled.** If the user has disabled the notification permission for your app, none of your notifications will be posted, as a result, your messages will be deprioritized. You should [verify that notifications are enabled](https://developer.android.com/reference/androidx/core/app/NotificationManagerCompat#areNotificationsEnabled\(\)) before sending high priority messages to an application instance.

  * **Avoid making additional network calls when processing your notification.** Because a small portion of the Android mobile population are on high latency networks, avoid opening a connection to your servers before displaying a notification. Calling back to the server before the end of the allowed processing time may be risky for users on high latency networks.

Instead, include the notification content in the FCM message and display it immediately. If you need to sync for additional in-app content on Android, you can schedule a task with [ WorkManager](//developer.android.com/topic/libraries/architecture/workmanager) to handle that in the background.



