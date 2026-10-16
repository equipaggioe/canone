  * [ Firebase ](https://firebase.google.com/)
  * [ Documentation ](https://firebase.google.com/docs)
  * [ FCM ](https://firebase.google.com/docs/cloud-messaging)
  * [ Run ](https://firebase.google.com/docs/run)



Send feedback 

#  Send a message using Firebase Admin SDK Stay organized with collections  Save and categorize content based on your preferences. 

If you haven't set up Firebase Admin SDK already, follow the [guide](https://firebase.google.com/docs/admin/setup) to set up Firebase Admin SDK on your server.

## Enable the FCM HTTP v1 API

  1. In the Firebase console, go to settings **Settings** > **General**. Then, click the [**Cloud Messaging** tab](https://console.firebase.google.com/project/_/settings/cloudmessaging).

  2. Enable the Cloud Messaging API.




## Authorize a service account from a different project

You can send messages for one project, the "target project", while using a service account in a different project, the "sender project". This lets you centralize service account management in one project while sending messages on behalf of others. To learn how to do this, use the following steps:

  1. In the sender project, make sure the Firebase Cloud Messaging API is enabled. Check for its enablement in the Firebase console by going to settings **Settings** > **General**. Then, click the [**Cloud Messaging** tab](https://console.firebase.google.com/project/_/settings/cloudmessaging).

  2. In the sender project, create a [service account](https://cloud.google.com/iam/docs/service-accounts-create).

  3. In the target project, assign the [_Firebase Cloud Messaging API Admin_ role](https://cloud.google.com/iam/docs/roles-permissions/firebasecloudmessaging#firebasecloudmessaging.admin) to the email address for the service account. You do this in the **IAM & Admin** > [**IAM** page](https://console.cloud.google.com/iam-admin/iam) of the Google Cloud console. This role allows the service account from the sender project to send messages to the target project.

  4. Initialize your SDK with the sender project's [service account key file](/docs/cloud-messaging/send/v1-api#provide-credentials-manually) and the target project's project ID.

### Node.js
         
         import { initializeApp, applicationDefault } from 'firebase-admin/app';
         
         initializeApp({
           // The credential is configured to be the sender project's service
           // account key via the environment variable GOOGLE_APPLICATION_CREDENTIALS
           credential: applicationDefault(),
           projectId: '<TARGET_PROJECT_ID>',
         });
         

### Java
         
         FirebaseOptions options = FirebaseOptions.builder()
             // The credential is configured to be the sender project's service
             // account key via the environment variable GOOGLE_APPLICATION_CREDENTIALS
             .setCredentials(GoogleCredentials.getApplicationDefault())
             .setProjectId("<TARGET_PROJECT_ID>")
             .build();
         
         FirebaseApp.initializeApp(options);
         

### Python
         
         import firebase_admin
         
         app_options = {'projectId': '<TARGET_PROJECT_ID>'}
         # Initialize with the default credential, i.e. the sender project's service
         # account key, stored in GOOGLE_APPLICATION_CREDENTIALS
         default_app = firebase_admin.initialize_app(options=app_options)
         

### Go
         
         config := &firebase.Config{ProjectID: "<TARGET_PROJECT_ID>"}
         // Initialize with the default credential, i.e. the sender project's service
         // account key, stored in GOOGLE_APPLICATION_CREDENTIALS
         app, err := firebase.NewApp(context.Background(), config)
         if err != nil {
                 log.Fatalf("error initializing app: %v\n", err)
         }
         

### C#
         
         FirebaseApp.Create(new AppOptions()
         {
             // The credential is configured to be the sender project's service
             // account key via the environment variable GOOGLE_APPLICATION_CREDENTIALS
             Credential = GoogleCredential.GetApplicationDefault(),
             ProjectId = "<TARGET_PROJECT_ID>",
         });
         




## Send messages to specific devices

To send to a single, specific device, you can target either its [Firebase Installation ID (FID)](/docs/cloud-messaging/android/get-started#access-firebase-installation-id) or its registration token.

**Note:** During the migration period, the `token` field also accepts FIDs. However, since the `token` field is deprecated and will be removed, we recommend using the `fid` field once your clients are registered using Firebase Installation IDs.

### Node.js

**Using FID (Recommended)** :
    
    
    // This installation ID comes from the client FCM SDKs.
    const fid = 'YOUR_REGISTERED_FID';
    
    const message = {
      data: {
        score: '850',
        time: '2:45'
      },
      fid: fid
    };
    
    // Send a message to the device corresponding to the provided FID.
    getMessaging().send(message)
      .then((response) => {
        // Response is a message ID string.
        console.log('Successfully sent message:', response);
      })
      .catch((error) => {
        console.log('Error sending message:', error);
      });
    

**Using registration token (Deprecated)** :
    
    
    // This registration token comes from the client FCM SDKs.
    const registrationToken = 'YOUR_REGISTRATION_TOKEN';
    
    const message = {
      data: {
        score: '850',
        time: '2:45'
      },
      token: registrationToken
    };
    
    // Send a message to the device corresponding to the provided
    // registration token.
    getMessaging().send(message)
      .then((response) => {
        // Response is a message ID string.
        console.log('Successfully sent message:', response);
      })
      .catch((error) => {
        console.log('Error sending message:', error);
      });
    

### Java

**Using FID (Recommended)** :
    
    
    // This installation ID comes from the client FCM SDKs.
    String fid = "YOUR_REGISTERED_FID";
    
    // See documentation on defining a message payload.
    Message message = Message.builder()
        .putData("score", "850")
        .putData("time", "2:45")
        .setFid(fid)
        .build();
    
    // Send a message to the device corresponding to the provided FID.
    String response = FirebaseMessaging.getInstance().send(message);
    // Response is a message ID string.
    System.out.println("Successfully sent message: " + response);
    

**Using registration token (Deprecated)** :
    
    
    // This registration token comes from the client FCM SDKs.
    String registrationToken = "YOUR_REGISTRATION_TOKEN";
    
    // See documentation on defining a message payload.
    Message message = Message.builder()
        .putData("score", "850")
        .putData("time", "2:45")
        .setToken(registrationToken)
        .build();
    
    // Send a message to the device corresponding to the provided
    // registration token.
    String response = FirebaseMessaging.getInstance().sendAsync(message).get();
    // Response is a message ID string.
    System.out.println("Successfully sent message: " + response);
    
    [FirebaseMessagingSnippets.java](https://github.com/firebase/snippets-java/blob/7051da2745f8f95b176c9c6347e0bb0db3de1112/admin/src/main/java/com/google/firebase/example/FirebaseMessagingSnippets.java#L47-L61)
    
    
    

### Python

**Using FID (Recommended)** :
    
    
    # This installation ID comes from the client FCM SDKs.
    fid = 'YOUR_REGISTERED_FID'
    
    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        fid=fid,
    )
    
    # Send a message to the device corresponding to the provided FID.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    

**Using registration token (Deprecated)** :
    
    
    # This registration token comes from the client FCM SDKs.
    registration_token = 'YOUR_REGISTRATION_TOKEN'
    
    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'score': '850',
            'time': '2:45',
        },
        token=registration_token,
    )
    
    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    
    [cloud_messaging.py](https://github.com/firebase/firebase-admin-python/blob/de456071dc7450a6d7715667debf6049f38fd85d/snippets/messaging/cloud_messaging.py#L24-L40)
    
    
    

### Go

**Using FID (Recommended)** :
    
    
    // Obtain a messaging.Client from the App.
    ctx := context.Background()
    client, err := app.Messaging(ctx)
    if err != nil {
        log.Fatalf("error getting Messaging client: %v\n", err)
    }
    
    // This installation ID comes from the client FCM SDKs.
    fid := "YOUR_REGISTERED_FID"
    
    // See documentation on defining a message payload.
    message := &messaging.Message{
        Data: map[string]string{
            "score": "850",
            "time":  "2:45",
        },
        Fid: fid,
    }
    
    // Send a message to the device corresponding to the provided FID.
    response, err := client.Send(ctx, message)
    if err != nil {
        log.Fatalln(err)
    }
    // Response is a message ID string.
    fmt.Println("Successfully sent message:", response)
    

**Using registration token (Deprecated)** :
    
    
    // Obtain a messaging.Client from the App.
    ctx := context.Background()
    client, err := app.Messaging(ctx)
    if err != nil {
    	log.Fatalf("error getting Messaging client: %v\n", err)
    }
    
    // This registration token comes from the client FCM SDKs.
    registrationToken := "YOUR_REGISTRATION_TOKEN"
    
    // See documentation on defining a message payload.
    message := &messaging.Message{
    	Data: map[string]string{
    		"score": "850",
    		"time":  "2:45",
    	},
    	Token: registrationToken,
    }
    
    // Send a message to the device corresponding to the provided
    // registration token.
    response, err := client.Send(ctx, message)
    if err != nil {
    	log.Fatalln(err)
    }
    // Response is a message ID string.
    fmt.Println("Successfully sent message:", response)
    
    [messaging.go](https://github.com/firebase/firebase-admin-go/blob/66a72c371b4dbc592317ab7e7f99ce00d76c62ae/snippets/messaging.go#L29-L55)
    
    
    

### C#

**Using FID (Recommended)** :
    
    
    // This installation ID comes from the client FCM SDKs.
    var fid = "YOUR_REGISTERED_FID";
    
    var message = new Message()
    {
        Data = new Dictionary<string, string>()
        {
            { "score", "850" },
            { "time", "2:45" },
        },
        Fid = fid,
    };
    
    // Send a message to the device corresponding to the provided FID.
    string response = await FirebaseMessaging.DefaultInstance.SendAsync(message);
    // Response is a message ID string.
    Console.WriteLine("Successfully sent message: " + response);
    

**Using registration token (Deprecated)** :
    
    
                // This registration token comes from the client FCM SDKs.
                var registrationToken = "YOUR_REGISTRATION_TOKEN";
    
                // See documentation on defining a message payload.
                var message = new Message()
                {
                    Data = new Dictionary<string, string>()
                    {
                        { "score", "850" },
                        { "time", "2:45" },
                    },
    #pragma warning disable CS0618
                    Token = registrationToken,
    #pragma warning restore CS0618
                };
    
                // Send a message to the device corresponding to the provided
                // registration token.
                string response = await FirebaseMessaging.DefaultInstance.SendAsync(message);
                // Response is a message ID string.
                Console.WriteLine("Successfully sent message: " + response);
    

On success, each send method returns a message ID. The Firebase Admin SDK returns the ID string in the format `projects/{project_id}/messages/{message_id}`.

## Send one message to multiple devices

The Admin FCM SDKs allow you to multicast a message to a list of [Firebase Installation IDs (FIDs)](/docs/cloud-messaging/android/get-started#access-firebase-installation-id) or device registration tokens. You can use this feature when you need to send the same message to a large number of devices. You can specify up to 500 FIDs and/or tokens per invocation.

**Note:** During the migration period, the `tokens` field also accepts FIDs. However, since the `token` field is deprecated and will be removed, we recommend using the `fid` field once your clients are registered using Firebase Installation IDs.

The return value includes a list of responses that corresponds to the order of the input targets, FIDs and/or tokens. This is useful when you want to check which targets resulted in [errors](/docs/reference/fcm/rest/v1/ErrorCode). If both tokens and FIDs are provided, tokens are processed first, followed by FIDs.

### Node.js

**Using FIDs (Recommended)** :
    
    
    // These Firebase Installation IDs (FIDs) come from the client FCM SDKs.
    const fids = [
      'YOUR_REGISTERED_FID_1',
      // ...
      'YOUR_REGISTERED_FID_N'
    ];
    
    const message = {
      data: {score: '850', time: '2:45'},
      fids: fids,
    };
    
    getMessaging().sendEachForMulticast(message)
      .then((response) => {
        console.log(response.successCount + ' messages were sent successfully');
        if (response.failureCount > 0) {
          const failedFids = [];
          response.responses.forEach((resp, idx) => {
            if (!resp.success) {
              failedFids.push(fids[idx]);
            }
          });
          console.log('List of FIDs that caused failures: ' + failedFids);
        }
      });
    

**Using registration tokens (Deprecated)** :
    
    
    // These registration tokens come from the client FCM SDKs.
    const registrationTokens = [
      'YOUR_REGISTRATION_TOKEN_1',
      // …
      'YOUR_REGISTRATION_TOKEN_N',
    ];
    
    const message = {
      data: {score: '850', time: '2:45'},
      tokens: registrationTokens,
    };
    
    getMessaging().sendEachForMulticast(message)
      .then((response) => {
        if (response.failureCount > 0) {
          const failedTokens = [];
          response.responses.forEach((resp, idx) => {
            if (!resp.success) {
              failedTokens.push(registrationTokens[idx]);
            }
          });
          console.log('List of tokens that caused failures: ' + failedTokens);
        }
      });
    

### Java

**Using FIDs (Recommended)** :
    
    
    // These Firebase Installation IDs (FIDs) come from the client FCM SDKs.
    List<String> fids = Arrays.asList(
        "YOUR_REGISTERED_FID_1",
        // ...
        "YOUR_REGISTERED_FID_N"
    );
    
    MulticastMessage message = MulticastMessage.builder()
        .putData("score", "850")
        .putData("time", "2:45")
        .addAllFids(fids)
        .build();
    
    BatchResponse response = FirebaseMessaging.getInstance().sendEachForMulticast(message);
    if (response.getFailureCount() > 0) {
      List<SendResponse> responses = response.getResponses();
      List<String> failedFids = new ArrayList<>();
      for (int i = 0; i < responses.size(); i++) {
        if (!responses.get(i).isSuccessful()) {
          // The order of responses corresponds to the order of the destination FIDs.
          failedFids.add(fids.get(i));
        }
      }
      System.out.println("List of FIDs that caused failures: " + failedFids);
    }
    

**Using registration tokens (Deprecated)** :
    
    
    // These registration tokens come from the client FCM SDKs.
    List<String> registrationTokens = Arrays.asList(
        "YOUR_REGISTRATION_TOKEN_1",
        // ...
        "YOUR_REGISTRATION_TOKEN_n"
    );
    
    MulticastMessage message = MulticastMessage.builder()
        .putData("score", "850")
        .putData("time", "2:45")
        .addAllTokens(registrationTokens)
        .build();
    BatchResponse response = FirebaseMessaging.getInstance().sendEachForMulticast(message);
    if (response.getFailureCount() > 0) {
      List<SendResponse> responses = response.getResponses();
      List<String> failedTokens = new ArrayList<>();
      for (int i = 0; i < responses.size(); i++) {
        if (!responses.get(i).isSuccessful()) {
          // The order of responses corresponds to the order of the registration tokens.
          failedTokens.add(registrationTokens.get(i));
        }
      }
    
      System.out.println("List of tokens that caused failures: " + failedTokens);
    }
    
    [FirebaseMessagingSnippets.java](https://github.com/firebase/firebase-admin-java/blob/e79eafb8ff0ad704bf4bc4d37b1e98788f702537/src/test/java/com/google/firebase/snippets/FirebaseMessagingSnippets.java#L236-L260)
    
    
    

### Python

**Using FIDs (Recommended)** :
    
    
    # These Firebase Installation IDs (FIDs) come from the client FCM SDKs.
    fids = [
        'YOUR_REGISTERED_FID_1',
        # ...
        'YOUR_REGISTERED_FID_N',
    ]
    
    message = messaging.MulticastMessage(
        data={'score': '850', 'time': '2:45'},
        fids=fids,
    )
    response = messaging.send_each_for_multicast(message)
    if response.failure_count > 0:
        responses = response.responses
        failed_fids = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the destination FIDs.
                failed_fids.append(fids[idx])
        print('List of FIDs that caused failures: {0}'.format(failed_fids))
    

**Using registration tokens (Deprecated)** :
    
    
    # These registration tokens come from the client FCM SDKs.
    registration_tokens = [
        'YOUR_REGISTRATION_TOKEN_1',
        # ...
        'YOUR_REGISTRATION_TOKEN_N',
    ]
    
    message = messaging.MulticastMessage(
        data={'score': '850', 'time': '2:45'},
        tokens=registration_tokens,
    )
    response = messaging.send_each_for_multicast(message)
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(registration_tokens[idx])
        print(f'List of tokens that caused failures: {failed_tokens}')
    
    [cloud_messaging.py](https://github.com/firebase/firebase-admin-python/blob/de456071dc7450a6d7715667debf6049f38fd85d/snippets/messaging/cloud_messaging.py#L249-L268)
    
    
    

### Go

**Using FIDs (Recommended)** :
    
    
    // Create a list containing up to 500 Firebase Installation IDs (FIDs).
    // These Firebase Installation IDs (FIDs) come from the client FCM SDKs.
    fids := []string{
        "YOUR_REGISTERED_FID_1",
        // ...
        "YOUR_REGISTERED_FID_N",
    }
    
    message := &messaging.MulticastMessage{
        Data: map[string]string{
            "score": "850",
            "time":  "2:45",
        },
        Fids: fids,
    }
    
    br, err := client.SendEachForMulticast(ctx, message)
    if err != nil {
        log.Fatalln(err)
    }
    
    if br.FailureCount > 0 {
        var failedFids []string
        for idx, resp := range br.Responses {
            if !resp.Success {
                // The order of responses corresponds to the order of the destination FIDs.
                failedFids = append(failedFids, fids[idx])
            }
        }
        fmt.Printf("List of FIDs that caused failures: %v\n", failedFids)
    }
    

**Using registration tokens (Deprecated)** :
    
    
    // Create a list containing up to 500 registration tokens.
    // This registration tokens come from the client FCM SDKs.
    registrationTokens := []string{
    	"YOUR_REGISTRATION_TOKEN_1",
    	// ...
    	"YOUR_REGISTRATION_TOKEN_n",
    }
    message := &messaging.MulticastMessage{
    	Data: map[string]string{
    		"score": "850",
    		"time":  "2:45",
    	},
    	Tokens: registrationTokens,
    }
    
    br, err := client.SendEachForMulticast(context.Background(), message)
    if err != nil {
    	log.Fatalln(err)
    }
    
    if br.FailureCount > 0 {
    	var failedTokens []string
    	for idx, resp := range br.Responses {
    		if !resp.Success {
    			// The order of responses corresponds to the order of the registration tokens.
    			failedTokens = append(failedTokens, registrationTokens[idx])
    		}
    	}
    
    	fmt.Printf("List of tokens that caused failures: %v\n", failedTokens)
    }
    
    [messaging.go](https://github.com/firebase/firebase-admin-go/blob/66a72c371b4dbc592317ab7e7f99ce00d76c62ae/snippets/messaging.go#L241-L271)
    
    
    

### C#

**Using FIDs (Recommended)** :
    
    
    // These Firebase Installation IDs (FIDs) come from the client FCM SDKs.
    var fids = new List<string>()
    {
        "YOUR_REGISTERED_FID_1",
        // ...
        "YOUR_REGISTERED_FID_N",
    };
    
    var message = new MulticastMessage()
    {
        Data = new Dictionary<string, string>()
        {
            { "score", "850" },
            { "time", "2:45" },
        },
        Fids = fids,
    };
    
    var response = await FirebaseMessaging.DefaultInstance.SendEachForMulticastAsync(message);
    
    if (response.FailureCount > 0)
    {
        var failedFids = new List<string>();
        for (var i = 0; i < response.Responses.Count; i++)
        {
            if (!response.Responses[i].IsSuccess)
            {
                // The order of responses corresponds to the order of the destination FIDs.
                failedFids.add(fids[i]);
            }
        }
        Console.WriteLine($"List of FIDs that caused failures: {string.Join(", ", failedFids)}");
    }
    

**Using registration tokens (Deprecated)** :
    
    
                // These registration tokens come from the client FCM SDKs.
                var registrationTokens = new List<string>()
                {
                    "YOUR_REGISTRATION_TOKEN_1",
                    // ...
                    "YOUR_REGISTRATION_TOKEN_n",
                };
                var message = new MulticastMessage()
                {
    #pragma warning disable CS0618
                    Tokens = registrationTokens,
    #pragma warning restore CS0618
                    Data = new Dictionary<string, string>()
                    {
                        { "score", "850" },
                        { "time", "2:45" },
                    },
                };
    
                var response = await FirebaseMessaging.DefaultInstance.SendEachForMulticastAsync(message);
                if (response.FailureCount > 0)
                {
                    var failedTokens = new List<string>();
                    for (var i = 0; i < response.Responses.Count; i++)
                    {
                        if (!response.Responses[i].IsSuccess)
                        {
                            // The order of responses corresponds to the order of the registration tokens.
                            failedTokens.Add(registrationTokens[i]);
                        }
                    }
    
                    Console.WriteLine($"List of tokens that caused failures: {failedTokens}");
                }
    
    
    [FirebaseMessagingSnippets.cs](https://github.com/firebase/firebase-admin-dotnet/blob/38b816d09bc4fd4fb68644bee24742a05c807d70/FirebaseAdmin/FirebaseAdmin.Snippets/FirebaseMessagingSnippets.cs#L193-L227)
    
    
    

## Send a list of messages

The Admin SDKs support sending a list of up to 500 messages. This feature can be used to build a customized set of messages and send them to different recipients, including topics, [Firebase Installation IDs (FIDs)](/docs/cloud-messaging/android/get-started#access-firebase-installation-id) or device registration tokens. For example, you can use this feature when you need to send varying messages to different audiences.

**Note:** During the migration period, the `token` field also accepts FIDs. However, since the `token` field is deprecated and will be removed, we recommend using the `fid` field once your clients are registered using Firebase Installation IDs.

### Node.js

**Using mixed targets (Recommended)** :
    
    
    // Create a list containing up to 500 messages.
    const messages = [
      {
        notification: { title: 'Price drop', body: '5% off all electronics' },
        fid: 'YOUR_REGISTERED_FID', // Using FID (Recommended)
      },
      {
        notification: { title: 'Price drop', body: '2% off all books' },
        token: 'YOUR_REGISTRATION_TOKEN', // Using token (Deprecated)
      },
      {
        notification: { title: 'Price drop', body: '10% off all shoes' },
        topic: 'readers-club',
      }
    ];
    
    getMessaging().sendEach(messages)
      .then((response) => {
        console.log(response.successCount + ' messages were sent successfully');
      });
    

**Using registration tokens (Deprecated)** :
    
    
    // Create a list containing up to 500 messages.
    const messages = [];
    messages.push({
      notification: { title: 'Price drop', body: '5% off all electronics' },
      token: registrationToken,
    });
    messages.push({
      notification: { title: 'Price drop', body: '2% off all books' },
      topic: 'readers-club',
    });
    
    getMessaging().sendEach(messages)
      .then((response) => {
        console.log(response.successCount + ' messages were sent successfully');
      });
    

### Java

**Using mixed targets (Recommended)** :
    
    
    // Create a list containing up to 500 messages.
    List<Message> messages = new ArrayList<>();
    messages.add(Message.builder()
        .setNotification(Notification.builder()
            .setTitle("Price drop")
            .setBody("5% off all electronics")
            .build())
        .setFid("YOUR_REGISTERED_FID") // Using FID (Recommended)
        .build());
    messages.add(Message.builder()
        .setNotification(Notification.builder()
            .setTitle("Price drop")
            .setBody("2% off all books")
            .build())
        .setToken("YOUR_REGISTRATION_TOKEN") // Using token (Deprecated)
        .build());
    messages.add(Message.builder()
        .setNotification(Notification.builder()
            .setTitle("Price drop")
            .setBody("10% off all shoes")
            .build())
        .setTopic("readers-club")
        .build());
    
    BatchResponse response = FirebaseMessaging.getInstance().sendEach(messages);
    // See the BatchResponse reference documentation
    // for the contents of response.
    System.out.println(response.getSuccessCount() + " messages were sent successfully");
    

**Using registration tokens (Deprecated)** :
    
    
    // Create a list containing up to 500 messages.
    List<Message> messages = Arrays.asList(
        Message.builder()
            .setNotification(Notification.builder()
                .setTitle("Price drop")
                .setBody("5% off all electronics")
                .build())
            .setToken(registrationToken)
            .build(),
        // ...
        Message.builder()
            .setNotification(Notification.builder()
                .setTitle("Price drop")
                .setBody("2% off all books")
                .build())
            .setTopic("readers-club")
            .build()
    );
    
    BatchResponse response = FirebaseMessaging.getInstance().sendEach(messages);
    // See the BatchResponse reference documentation
    // for the contents of response.
    System.out.println(response.getSuccessCount() + " messages were sent successfully");
    
    [FirebaseMessagingSnippets.java](https://github.com/firebase/firebase-admin-java/blob/e79eafb8ff0ad704bf4bc4d37b1e98788f702537/src/test/java/com/google/firebase/snippets/FirebaseMessagingSnippets.java#L156-L178)
    
    
    

### Python

**Using mixed targets (Recommended)** :
    
    
    # Create a list containing up to 500 messages.
    messages = [
        messaging.Message(
            notification=messaging.Notification('Price drop', '5% off all electronics'),
            fid='YOUR_REGISTERED_FID', # Using FID (Recommended)
        ),
        messaging.Message(
            notification=messaging.Notification('Price drop', '2% off all books'),
            token='YOUR_REGISTRATION_TOKEN', # Using token (Deprecated)
        ),
        messaging.Message(
            notification=messaging.Notification('Price drop', '10% off all shoes'),
            topic='readers-club',
        ),
    ]
    
    response = messaging.send_each(messages)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print('{0} messages were sent successfully'.format(response.success_count))
    

**Using registration tokens (Deprecated)** :
    
    
    # Create a list containing up to 500 messages.
    messages = [
        messaging.Message(
            notification=messaging.Notification('Price drop', '5% off all electronics'),
            token=registration_token,
        ),
        # ...
        messaging.Message(
            notification=messaging.Notification('Price drop', '2% off all books'),
            topic='readers-club',
        ),
    ]
    
    response = messaging.send_each(messages)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print(f'{response.success_count} messages were sent successfully')
    
    [cloud_messaging.py](https://github.com/firebase/firebase-admin-python/blob/de456071dc7450a6d7715667debf6049f38fd85d/snippets/messaging/cloud_messaging.py#L228-L244)
    
    
    

### Go

**Using mixed targets (Recommended)** :
    
    
    // Create a list containing up to 500 messages.
    messages := []*messaging.Message{
        {
            Notification: &messaging.Notification{
                Title: "Price drop",
                Body:  "5% off all electronics",
            },
            Fid: "YOUR_REGISTERED_FID", // Using FID (Recommended)
        },
        {
            Notification: &messaging.Notification{
                Title: "Price drop",
                Body:  "2% off all books",
            },
            Token: "YOUR_REGISTRATION_TOKEN", // Using token (Deprecated)
        },
        {
            Notification: &messaging.Notification{
                Title: "Price drop",
                Body:  "10% off all shoes",
            },
            Topic: "readers-club",
        },
    }
    
    br, err := client.SendEach(ctx, messages)
    if err != nil {
        log.Fatalln(err)
    }
    // See the BatchResponse reference documentation
    // for the contents of response.
    fmt.Printf("%d messages were sent successfully\n", br.SuccessCount)
    

**Using registration tokens (Deprecated)** :
    
    
    // Create a list containing up to 500 messages.
    messages := []*messaging.Message{
    	{
    		Notification: &messaging.Notification{
    			Title: "Price drop",
    			Body:  "5% off all electronics",
    		},
    		Token: registrationToken,
    	},
    	{
    		Notification: &messaging.Notification{
    			Title: "Price drop",
    			Body:  "2% off all books",
    		},
    		Topic: "readers-club",
    	},
    }
    
    br, err := client.SendEach(context.Background(), messages)
    if err != nil {
    	log.Fatalln(err)
    }
    
    // See the BatchResponse reference documentation
    // for the contents of response.
    fmt.Printf("%d messages were sent successfully\n", br.SuccessCount)
    
    [messaging.go](https://github.com/firebase/firebase-admin-go/blob/66a72c371b4dbc592317ab7e7f99ce00d76c62ae/snippets/messaging.go#L148-L173)
    
    
    

### C#

**Using mixed targets (Recommended)** :
    
    
    // Create a list containing up to 500 messages.
    var messages = new List<Message>()
    {
        new Message()
        {
            Notification = new Notification()
            {
                Title = "Price drop",
                Body = "5% off all electronics",
            },
            Fid = "YOUR_REGISTERED_FID", // Using FID (Recommended)
        },
        new Message()
        {
            Notification = new Notification()
            {
                Title = "Price drop",
                Body = "2% off all books",
            },
            Token = "YOUR_REGISTRATION_TOKEN", // Using token (Deprecated)
        },
        new Message()
        {
            Notification = new Notification()
            {
                Title = "Price drop",
                Body = "10% off all shoes",
            },
            Topic = "readers-club",
        },
    };
    
    var response = await FirebaseMessaging.DefaultInstance.SendEachAsync(messages);
    // See the BatchResponse reference documentation
    // for the contents of response.
    Console.WriteLine($"{response.SuccessCount} messages were sent successfully");
    

**Using registration tokens (Deprecated)** :
    
    
                // Create a list containing up to 500 messages.
                var messages = new List<Message>()
                {
                    new Message()
                    {
                        Notification = new Notification()
                        {
                            Title = "Price drop",
                            Body = "5% off all electronics",
                        },
    #pragma warning disable CS0618
                        Token = registrationToken,
    #pragma warning restore CS0618
                    },
                    new Message()
                    {
                        Notification = new Notification()
                        {
                            Title = "Price drop",
                            Body = "2% off all books",
                        },
                        Topic = "readers-club",
                    },
                };
    
                var response = await FirebaseMessaging.DefaultInstance.SendEachAsync(messages);
                // See the BatchResponse reference documentation
                // for the contents of response.
                Console.WriteLine($"{response.SuccessCount} messages were sent successfully");
    
    [FirebaseMessagingSnippets.cs](https://github.com/firebase/firebase-admin-dotnet/blob/38b816d09bc4fd4fb68644bee24742a05c807d70/FirebaseAdmin/FirebaseAdmin.Snippets/FirebaseMessagingSnippets.cs#L128-L156)
    
    
    

Send feedback 
