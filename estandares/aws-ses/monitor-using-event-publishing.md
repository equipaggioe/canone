# Monitor email sending using Amazon SES event publishing

To enable you to track your email sending at a granular level, you can set up Amazon SES to publish _email sending events_ to Amazon CloudWatch, Amazon Data Firehose, Amazon Pinpoint, Amazon Simple Notification Service, or Amazon EventBridge based on characteristics that you define.

You can track several types of email sending events, including sends, deliveries, opens, clicks, bounces, complaints, rejections, rendering failures, and delivery delays. This information can be useful for operational and analytical purposes. For example, you can publish your email sending data to CloudWatch and create dashboards that track the performance of your email campaigns, or you can use Amazon SNS to send you notifications when certain events occur.

## How event publishing works with configuration sets and message tags

To use event publishing, you first set up one or more _configuration sets_. A configuration set specifies where to publish your events and which events to publish. Then, each time you send an email, you provide the name of the configuration set and one or more _message tags_ , in the form of name/value pairs, to categorize the email. For example, if you advertise books, you could name a message tag _genre_ , and assign a value of _sci-fi_ or _western_ , when you send an email for the associated campaign.

Depending on which email sending interface you use, you either provide the message tag as a parameter to the [`EmailTags`](https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_SendEmail.html#SES-SendEmail-request-EmailTags) field of the [`SendEmail`](https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_SendEmail.html) API operation or add the message tag to the SES-specific email header [`X-SES-MESSAGE-TAGS`](https://docs.aws.amazon.com/ses/latest/dg/event-publishing-send-email.html#event-publishing-using-ses-headers). For more information about configuration sets, see [Using configuration sets in Amazon SES](./using-configuration-sets.html).

In addition to the message tags that you specify, SES also adds _auto-tags_ to the messages you send. You do not need to perform any additional steps to use auto-tags.

The following table lists the auto-tags that are automatically applied to messages you send using SES.

SES Auto-Tags Auto-tag name | Description  
---|---  
`ses:caller-identity` | The IAM identity of the SES user who sent the email.  
`ses:configuration-set` | The name of the Configuration Set associated with the email.  
`ses:from-domain` | The domain of the "From" address.  
`ses:outgoing-ip` | The IP address that SES used to send the email.  
`ses:source-ip` | The IP address that the caller used to send the email.  
`ses:source-tls-version` | The TLS protocol version the caller used to send the email.  
`ses:outgoing-tls-version` | The TLS protocol version that SES used to send the email.  
  
## Fine-grained feedback for email campaigns

The `ses:feedback-id-<`a` or `b`>` tag is an optional message tag that you can think of as a hybrid or semi-automatic tag—while it's similar to the auto-tags discussed in the previous section, the difference is that you must manually add it and use the `ses:` prefix key. You can use up to two of these tags defined as `ses:feedback-id-a` and `ses:feedback-id-b`.

When you specify these tags, SES automatically appends them to the standard `Feedback-ID` header which is used in providing delivery statistics, such as complaint and spam rates, as part of a feedback loop (FBL), see [Feedback loops](./faqs-enforcement.html#cm-feedback-loop). The `Feedback-ID` header is comprised of the identifier, _SESInternalID_ , used by SES for collecting complaint information, and the static tag, _AmazonSES_ , identifying SES as the sending platform such as:

`FeedBackId:feedback-id-a:feedback-id-b:((SESInternalID):(AmazonSES))`

These optional feedback ID tags are offered as a way for you to generate fine-grained feedback, such as for messages you send as part of an email campaign. You can use `ses:feedback-id-<`a` or `b`>` by specifying it as a message tag in the [`EmailTags`](https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_SendEmail.html#SES-SendEmail-request-EmailTags) field of the [`SendEmail`](https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_SendEmail.html) operation request as shown in the following example:
    
    
    {
      "FromEmailAddress": "noreply@example.com",
      "Destination": {
        "ToAddresses": [
          "customer@example.net"
        ]
      },
      "Content": {
        "Simple": {
          "Subject": {
            "Data": "Hello and welcome"
          },
          "Body": {
            "Text": {
              "Data": "Lorem ipsum dolor sit amet."
            },
            "Html": {
              "Data": "Lorem ipsum dolor sit amet."
            }
          }
        }
      },
      "EmailTags": [
        {
          "Name": "ses:feedback-id-a",
          "Value": "new-members-campaign"
        },
        {
          "Name": "ses:feedback-id-b",
          "Value": "football-campaign"
        }
      ],
      "ConfigurationSetName": "football-club"
    }

If sending in raw format, you would add `ses:feedback-id-<`a` or `b`>` as a message tag to the SES-specific header [X-SES-MESSAGE-TAGS](./event-publishing-send-email.html#event-publishing-using-ses-headers).

The `ses:feedback-id-<`a` or `b`>` message tag can also be tracked in Amazon CloudWatch by specifying it as a CloudWatch value source just like any other message tag, see [Adding a CloudWatch Event Destination](./event-publishing-add-event-destination-cloudwatch.html#event-publishing-add-event-destination-cloudwatch-add) _(Additional charges apply, see[Price per metric for CloudWatch](./event-publishing-add-event-destination-cloudwatch.html#cw-add-pricing).)_

## How to use event publishing

The following sections contain the information you need to set up and use SES event publishing.

  * [Setting up event publishing](./monitor-sending-using-event-publishing-setup.html)

  * [Working with event data](./working-with-event-data.html)




## Event publishing terminology

The following list defines terms related to SES event publishing.

**Email sending event**
    

Information associated with the outcome of an email you submit to SES. Sending events include the following:

  * **Send** – The send request was successful and Amazon SES will attempt to deliver the message to the recipient’s mail server. (If account-level or global suppression is being used, SES will still count it as a send, but delivery is suppressed.)

  * **RenderingFailure** – The email wasn't sent because of a template rendering issue. This event type can occur when template data is missing, or when there is a mismatch between template parameters and data. (This event type only occurs when you send email using the [`SendTemplatedEmail`](https://docs.aws.amazon.com/ses/latest/APIReference/API_SendTemplatedEmail.html) or [`SendBulkTemplatedEmail`](https://docs.aws.amazon.com/ses/latest/APIReference/API_SendBulkTemplatedEmail.html) API operations.)

  * **Reject** – Amazon SES accepted the email, but determined that it contained a virus and didn’t attempt to deliver it to the recipient’s mail server.

  * **Delivery** – Amazon SES successfully delivered the email to the recipient's mail server.

  * **Bounce** – A _hard bounce_ that the recipient's mail server permanently rejected the email. (_Soft bounces_ are only included when SES is no longer retrying to deliver the email. Generally these soft bounces indicate a delivery failure, although in some cases a soft bounce can be returned even when the mail reaches the recipient inbox successfully. This typically occurs when the recipient sends an out-of-office automatic reply. Learn more about soft bounces in this [AWS re:Post article](https://repost.aws/knowledge-center/ses-understand-soft-bounces).)

  * **Complaint** – The email was successfully delivered to the recipient’s mail server, but the recipient marked it as spam.

  * **DeliveryDelay** – The email couldn't be delivered to the recipient’s mail server because a temporary issue occurred. Delivery delays can occur, for example, when the recipient's inbox is full, or when the receiving email server experiences a transient issue.

  * **Subscription** – The email was successfully delivered, but the recipient updated the subscription preferences by clicking `List-Unsubscribe` in the email header or the `Unsubscribe` link in the footer.

  * **Open** – The recipient received the message and opened it in their email client.

  * **Click** – The recipient clicked one or more links in the email.




**Configuration set**
    

A set of rules that defines the destination that SES publishes email sending events to, and the types of email sending events that you want to publish. When you send an email that you want to use with event publishing, you specify the configuration set to associate with the email.

**Event destination**
    

An AWS service that you publish SES email sending events to. Each event destination that you set up belongs to one, and only one, configuration set.

**Message tag**
    

A name/value pair that you use to categorize an email for the purpose of event publishing. Examples are _campaign/book_ and _campaign/clothing_. When you send an email, you either specify the message tag as a parameter to the API call or as an SES-specific email header.

**Auto-tag**
    

Message tags that are automatically included in event publishing reports. There is an auto-tag for the configuration set name, the domain of the "From" address, the caller's outgoing IP address, the SES outgoing IP address, and the IAM identity of the caller.
