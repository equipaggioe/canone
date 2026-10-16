  * [ Firebase ](https://firebase.google.com/)
  * [ Documentation ](https://firebase.google.com/docs)
  * [ FCM ](https://firebase.google.com/docs/cloud-messaging)
  * [ Run ](https://firebase.google.com/docs/run)



#  Receive messages in Android apps Stay organized with collections  Save and categorize content based on your preferences. 

**Select platform:** |  [iOS+](/docs/cloud-messaging/ios/receive-messages) [Android](/docs/cloud-messaging/android/receive-messages) [Web](/docs/cloud-messaging/web/receive-messages) [Flutter](/docs/cloud-messaging/flutter/receive-messages) [Unity](/docs/cloud-messaging/unity/receive-messages) [C++](/docs/cloud-messaging/cpp/receive-messages)  
---|---  
  
  


To receive messages, you can use a service that extends [`FirebaseMessagingService`](/docs/reference/android/com/google/firebase/messaging/FirebaseMessagingService). Your service should override the `onMessageReceived` and `onDeletedMessages` callbacks. For a complete example, see the [Firebase Cloud Messaging quickstart sample](https://github.com/firebase/quickstart-android/tree/master/messaging).

`onMessageReceived` is provided for most message types, with the following exceptions:

  * **Notification messages delivered when your app is in the background**. In this case, the notification is delivered to the device's system tray. A user tap on a notification opens the app launcher by default.

  * **Messages with both notification and data payload, when received in the background**. In this case, the notification is delivered to the device's system tray, and the data payload is delivered in the extras of the intent of your launcher Activity.




In summary:

App state | Notification | Data | Both  
---|---|---|---  
Foreground | `onMessageReceived` | `onMessageReceived` | `onMessageReceived`  
Background | System tray | `onMessageReceived` | Notification: system tray Data: in extras of the intent.  
  
For more information about message types, see [Notifications and data messages](/docs/cloud-messaging/customize-messages/set-message-type).

The `onMessageReceived` callback has a short execution window. Many factors can affect how long this window is, including OS delays, app startup time, the main thread being blocked by other operations, or previous `onMessageReceived` calls taking too long.

**Caution:** If processing of the message payload takes longer than a few seconds, you should make sure that the processing continues in a valid [process lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle). If you don't make sure this occurs, [background execution limits](https://developer.android.com/about/versions/oreo/background) may cause processing to be paused or terminated before the task completes, which can result in delayed or missing user notifications.

For this reason, you should avoid long-running tasks (such as fetching images from a server to display in a notification) in `onMessageReceived` and instead schedule a task using `WorkManager` to handle any tasks that might take more than a couple of seconds to complete. For more information on message priority and how it impacts processing, see [Message processing for high and normal priority messages](/docs/cloud-messaging/android-message-priority#message-processing).

### Edit the app manifest

To use `FirebaseMessagingService`, you need to add the following in your app manifest:
    
    
    <service
        android:name=".java.MyFirebaseMessagingService"
        android:exported="false">
        <intent-filter>
            <action android:name="com.google.firebase.MESSAGING_EVENT" />
        </intent-filter>
    </service>
    
    [AndroidManifest.xml](https://github.com/firebase/quickstart-android/blob/b255031255c8d3e1788b0e73d53b16bf690682a9/messaging/app/src/main/AndroidManifest.xml#L55-L61)
    
    
    

It's recommended to set default values to customize the appearance of notifications. You can specify a custom default icon and a custom default color that are applied whenever equivalent values aren't set in the notification payload.

Add these lines inside the `application` tag to set the custom default icon and custom color:
    
    
    <!-- Set custom default icon. This is used when no icon is set for incoming notification messages.
         See README(https://goo.gl/l4GJaQ) for more. -->
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_icon"
        android:resource="@drawable/ic_stat_ic_notification" />
    <!-- Set color used with incoming notification messages. This is used when no color is set for the incoming
         notification message. See README(https://goo.gl/6BKBk7) for more. -->
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_color"
        android:resource="@color/colorAccent" />
    
    [AndroidManifest.xml](https://github.com/firebase/quickstart-android/blob/b255031255c8d3e1788b0e73d53b16bf690682a9/messaging/app/src/main/AndroidManifest.xml#L12-L21)
    
    
    

Android displays and uses the custom default icon for

  * All notification messages sent from [the Notifications composer](https://console.firebase.google.com/project/_/notification) in the Firebase console.

  * Any notification message that doesn't explicitly set the icon in the notification payload.




If a custom default icon isn't set and an icon isn't set in the notification payload, Android displays the application icon rendered in white.

### Override `onMessageReceived`

By overriding the method `FirebaseMessagingService.onMessageReceived`, you can perform actions based on the received [RemoteMessage](/docs/reference/android/com/google/firebase/messaging/RemoteMessage) object and get the message data:

###  Kotlin
    
    
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // TODO(developer): Handle FCM messages here.
        // Not getting messages here? See why this may be: https://goo.gl/39bRNJ
        Log.d(TAG, "From: ${remoteMessage.from}")
    
        // Check if message contains a data payload.
        if (remoteMessage.data.isNotEmpty()) {
            Log.d(TAG, "Message data payload: ${remoteMessage.data}")
    
            // Check if data needs to be processed by long running job
            if (needsToBeScheduled()) {
                // For long-running tasks (10 seconds or more) use WorkManager.
                scheduleJob()
            } else {
                // Handle message within 10 seconds
                handleNow()
            }
        }
    
        // Check if message contains a notification payload.
        remoteMessage.notification?.let {
            Log.d(TAG, "Message Notification Body: ${it.body}")
        }
    
        // Also if you intend on generating your own notifications as a result of a received FCM
        // message, here is where that should be initiated. See sendNotification method below.
    }
    
    [MyFirebaseMessagingService.kt](https://github.com/firebase/snippets-android/blob/12ec906c9ccba5acf8d47009fd4f00370b186b9b/messaging/app/src/main/java/com/google/firebase/example/messaging/kotlin/MyFirebaseMessagingService.kt#L23-L49)

###  Java
    
    
    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        // TODO(developer): Handle FCM messages here.
        // Not getting messages here? See why this may be: https://goo.gl/39bRNJ
        Log.d(TAG, "From: " + remoteMessage.getFrom());
    
        // Check if message contains a data payload.
        if (remoteMessage.getData().size() > 0) {
            Log.d(TAG, "Message data payload: " + remoteMessage.getData());
    
            if (/* Check if data needs to be processed by long running job */ true) {
                // For long-running tasks (10 seconds or more) use WorkManager.
                scheduleJob();
            } else {
                // Handle message within 10 seconds
                handleNow();
            }
    
        }
    
        // Check if message contains a notification payload.
        if (remoteMessage.getNotification() != null) {
            Log.d(TAG, "Message Notification Body: " + remoteMessage.getNotification().getBody());
        }
    
        // Also if you intend on generating your own notifications as a result of a received FCM
        // message, here is where that should be initiated. See sendNotification method below.
    }
    
    [MyFirebaseMessagingService.java](https://github.com/firebase/snippets-android/blob/12ec906c9ccba5acf8d47009fd4f00370b186b9b/messaging/app/src/main/java/com/google/firebase/example/messaging/MyFirebaseMessagingService.java#L28-L55)

### Override `onDeletedMessages`

In some situations, FCM may not deliver a message. This happens when there are too many messages (>100) pending for your app on a particular device at the time it connects or if the device hasn't connected to FCM in more than one month. In these cases, you may receive a callback to `FirebaseMessagingService.onDeletedMessages()`. When the app instance receives this callback, it should perform a full sync with your app server. If you haven't sent a message to the app on that device within the last 4 weeks, FCM won't call `onDeletedMessages()`.

### Handle notification messages in a backgrounded app

When your app is in the background, Android directs notification messages to the system tray. A user tap on the notification opens the app launcher by default.

This includes messages that contain both notification and data payload (and all messages sent from the Notifications composer in the Firebase console). In these cases, the notification is delivered to the device's system tray, and the data payload is delivered in the extras of the intent of your launcher Activity.

For insight into message delivery to your app, go to the **DevOps & Engagement** > **Messaging** > [**Reports** dashboard](https://console.firebase.google.com/project/_/notification/reporting) in the Firebase console. This dashboard records the number of messages sent and opened on Apple and Android devices, along with data for "impressions" (notifications seen by users) for Android apps.
