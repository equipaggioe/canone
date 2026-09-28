# Using a custom MAIL FROM domain

When an email is sent, it has two addresses that indicate its source: a From address that's displayed to the message recipient, and a MAIL FROM address that indicates where the message originated. The MAIL FROM address is sometimes called the _envelope sender_ , _envelope from_ , _bounce address_ , or _Return Path_ address. Mail servers use the MAIL FROM address to return bounce messages and other error notifications. The MAIL FROM address is usually only viewable by recipients if they view the source code for the message.

Amazon SES sets the MAIL FROM domain for the messages that you send to a default value unless you specify your own (custom) domain. This section discusses the benefits of setting up a custom MAIL FROM domain, and includes setup procedures.

## Why use a custom MAIL FROM domain?

Messages that you send through Amazon SES automatically use a subdomain of `amazonses.com` as the default MAIL FROM domain. Sender Policy Framework (SPF) authentication successfully validates these messages because the default MAIL FROM domain matches the application that sent the email—in this case, SES.

If you don't want to use the SES default MAIL FROM domain, and would rather use a subdomain of a domain that you own, this is referred to in SES as using a _custom_ MAIL FROM domain. To do this, it requires you to publish your own SPF record for your custom MAIL FROM domain. In addition, SES also requires you to set up an MX record so that your domain can receive the bounce and complaint notifications that email providers send you.

By using a custom MAIL FROM domain, you have the flexibility to use SPF, DKIM, or both to achieve [Domain-based Message Authentication, Reporting and Conformance (DMARC)](./send-email-authentication-dmarc.html) validation. DMARC enables a sender's domain to indicate that emails sent from the domain are protected by one or more authentication systems. There are two ways to achieve DMARC validation: [Complying with DMARC through SPF](./send-email-authentication-dmarc.html#send-email-authentication-dmarc-spf) and [Complying with DMARC through DKIM](./send-email-authentication-dmarc.html#send-email-authentication-dmarc-dkim).

## Choosing a custom MAIL FROM domain

In the following, the term _MAIL FROM domain_ always refers to a subdomain of a domain that you own - this subdomain that you use for your custom MAIL FROM domain must not be used for anything else and meet the following requirements:

  * The MAIL FROM domain has to be a subdomain of the parent domain of a verified identity (email address or domain). 

  * The MAIL FROM domain shouldn't be a subdomain that you also use to send email from. 

  * The MAIL FROM domain shouldn't be a subdomain that you use to receive email.




## Using SPF with your custom MAIL FROM domain

_Sender Policy Framework_ (SPF) is an email validation standard that's designed to prevent email spoofing. You can configure your custom MAIL FROM domain with SPF to tell email providers which servers are allowed to send email from your custom MAIL FROM domain. SPF is defined in [RFC 7208](https://tools.ietf.org/html/rfc7208).

To set up SPF, you publish a TXT record to the DNS configuration for your custom MAIL FROM domain. This record contains a list of the servers that you authorize to send email from using your custom MAIL FROM domain. When an email provider receives a message from your custom MAIL FROM domain, it checks the DNS records for that domain to make sure that the email was sent from an authorized server.

If you want to use this SPF record as a way to comply with DMARC, the domain in the From address must match the MAIL FROM domain. See [Complying with DMARC through SPF](./send-email-authentication-dmarc.html#send-email-authentication-dmarc-spf).

The next section, Configuring your custom MAIL FROM domain, explains how to set up SPF for your custom MAIL FROM domain.

## Configuring your custom MAIL FROM domain

The process of setting up a custom MAIL FROM domain requires you to add records to the DNS configuration for the domain. SES requires you to publish an MX record so that your domain can receive the bounce and complaint notifications that email providers send you. You also have to publish an SPF (type TXT) record in order to prove that Amazon SES is authorized to send email from your domain.

You can set up a custom MAIL FROM domain for an entire domain or subdomain, as well as for individual email addresses. The following procedures show how to use the Amazon SES console to configure a custom MAIL FROM domain. You can also configure a custom MAIL FROM domain using the [SetIdentityMailFromDomain](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) API operation.

These procedures show you how to configure a custom MAIL FROM domain for an entire domain or subdomain so that all messages sent from addresses on that domain will use the this custom MAIL FROM domain.

###### To configure a verified domain to use a specified custom MAIL FROM domain

  1. Open the Amazon SES console at [https://console.aws.amazon.com/ses/](https://console.aws.amazon.com/ses/).

  2. In the left navigation panel, under **Configuration** , choose **Identities**.

  3. In the list of identities, choose the identity you want to configure where the **Identity type** is **Domain** and **Status** is _Verified_.

     1. If the **Status** is _Unverified_ , complete the procedures at [Verifying a DKIM domain identity with your DNS provider](./creating-identities.html#just-verify-domain-proc) to verify the email address's domain. 

  4. At the bottom of the screen in the **Custom MAIL FROM domain** pane, choose **Edit** .

  5. In the **General details** pane, do the following:

     1. Select the **Use a custom MAIL FROM domain** checkbox.

     2. For **MAIL FROM domain** , enter the subdomain that you want to use as the MAIL FROM domain.

     3. For **Behavior on MX failure** , choose one of the following options:

        * **Use default MAIL FROM domain** – If the custom MAIL FROM domain's MX record is not set up correctly, Amazon SES uses a subdomain of `amazonses.com`. The subdomain varies based on the AWS Region that you use Amazon SES in.

        * Reject message – If the custom MAIL FROM domain's MX record is not set up correctly, Amazon SES returns a `MailFromDomainNotVerified` error. Emails that you attempt to send from this domain are automatically rejected.

     4. Choose **Save changes** \- you'll be returned to the previous screen.

  6. Publish the MX and SPF (type TXT) records to the DNS server of the custom MAIL FROM domain:

In the **Custom MAIL FROM domain** pane, the **Publish DNS records** table now displays the MX and SPF (type TXT) records in that you have to publish (add) to your domain's DNS configuration. These records use the formats shown in the following table. 

Name | Type | Value  
---|---|---  
`subdomain`.`domain`.`com` | MX |  10 feedback-smtp.`region`.amazonses.com   
`subdomain`.`domain`.`com` | TXT | "v=spf1 include:amazonses.com ~all"  
  
In the preceding records,

     * `subdomain`.`domain`.`com` will be populated with your MAIL FROM subdomain

     * `region` will be populated with the name of the AWS Region where you want to verify the MAIL FROM domain (such as `us-west-2`, `us-east-1`, or `eu-west-1`, etc.)

     * The number _10_ listed along with the MX value is the preference order for the mail server and will need to be entered into a separate value field as specified by your DNS provider's GUI

     * The SPF's TXT record value usually has to include the quotation marks, but some DNS providers don't require them.

From the **Publish DNS records** table, copy the MX and SPF (type TXT) records by choosing the copy icon next to each value and paste them into the corresponding fields in your DNS provider's GUI. Alternatively, you can choose **Download .csv record set** to save a copy of the records to your computer.

###### Important

     * The specific procedures for publishing the MX and SPF (type TXT) records depend on your DNS or hosting provider. See your provider's documentation or contact them for information about adding these records to the DNS configuration for your domain.

     * To successfully set up a custom MAIL FROM domain with Amazon SES, you must publish exactly one MX record to the DNS server of your MAIL FROM domain. If the MAIL FROM domain has multiple MX records, the custom MAIL FROM setup with Amazon SES will fail.

If Route 53 provides the DNS service for your MAIL FROM domain, and you're signed in to the AWS Management Console under the same account that you use for Route 53, then choose **Publish Records Using Route 53**. The DNS records are automatically applied to your domain's DNS configuration.

If you use a different DNS provider, you have to publish the DNS records to the MAIL FROM domain's DNS server manually. The procedure for adding DNS records to your domain's DNS server varies based on your web hosting service or DNS provider. 

The procedures for publishing DNS records for your domain depend on which DNS provider you use. The following table includes links to the documentation for a few widely used DNS providers. This list isn't exhaustive and doesn't signify endorsement; likewise, if your DNS provider isn't listed, it doesn't imply they don't support MAIL FROM domain configuration.

DNS/Hosting provider name | Documentation link  
---|---  
GoDaddy | 
     * MX: [Add an MX record](https://www.godaddy.com/help/add-an-mx-record-19234) (external link)
     * TXT: [Add a TXT record](https://www.godaddy.com/help/add-a-txt-record-19232) (external link)  
DreamHost | 
     * MX: [How do I change my MX records?](https://help.dreamhost.com/hc/en-us/articles/215035328) (external link)
     * TXT: [How do I add custom DNS records?](https://help.dreamhost.com/hc/en-us/articles/215414867-How-do-I-add-custom-DNS-records-) (external link)  
Cloudflare | 
     * MX: [How do I add or edit mail or MX records? ](https://support.cloudflare.com/hc/en-us/articles/218069617-How-do-I-add-or-edit-mail-or-MX-records-) (external link)
     * TXT: [Managing DNS records in Cloudflare](https://support.cloudflare.com/hc/en-us/articles/360019093151) (external link)  
HostGator | 
     * MX: [Set up MX Records](https://www.hostgator.com/help/article/mail-exchange-record-what-to-put-for-your-mx-record) (external link)
     * TXT: [Manage DNS Records with HostGator/eNom](https://www.hostgator.com/help/article/manage-dns-records-with-hostgatorenom) (external link)  
Namecheap | 
     * MX: [How can I set up MX records required for mail service? ](https://www.namecheap.com/support/knowledgebase/article.aspx/322/2237/how-can-i-set-up-mx-records-required-for-mail-service) (external link)
     * TXT: [How do I add TXT/SPF/DKIM/DMARC records for my domain? ](https://www.namecheap.com/support/knowledgebase/article.aspx/317/2237/how-do-i-add-txtspfdkimdmarc-records-for-my-domain) (external link)  
Names.co.uk | 
     * MX: [Changing your domain's DNS settings](https://www.names.co.uk/support/domains/1156-changing_your_domains_dns_settings.html) (external link)
     * TXT: [Changing your domains DNS Settings](https://www.names.co.uk/support/1156-changing_your_domains_dns_settings.html) (external link)  
Wix | 
     * MX: [Adding or Updating MX Records in Your Wix Account](https://support.wix.com/en/article/adding-or-updating-mx-records-in-your-wix-account) (external link)
     * TXT: [Adding or Updating TXT Records in Your Wix Account](https://support.wix.com/en/article/adding-or-updating-txt-records-in-your-wix-account) (external link)  
  
When Amazon SES detects that the records are in place, you receive an email informing you that your custom MAIL FROM domain was set up successfully. Depending on your DNS provider, there might be a delay of up to 72 hours before Amazon SES detects the MX record.




You can also set up a custom MAIL FROM domain for a specific email address. In order to set up a custom MAIL FROM domain for an email address, you must modify the DNS records for the domain that the email address is associated with.

###### Note

You can't set up a custom MAIL FROM domain for addresses on a domain that you don't own (for example, you can't create a custom MAIL FROM domain for an address on the `gmail.com` domain, because you can't add the necessary DNS records to the domain).

###### To configure a verified email address to use a specified MAIL FROM domain

  1. Open the Amazon SES console at [https://console.aws.amazon.com/ses/](https://console.aws.amazon.com/ses/).

  2. In the left navigation panel, under **Configuration** , choose **Identities**.

  3. In the list of identities, choose the identity you want to configure where the **Identity type** is **Email address** and **Status** is _Verified_.

     1. If the **Status** is _Unverified_ , complete the procedures at [Verifying an email address identity](./creating-identities.html#just-verify-email-proc) to verify the email address's domain. 

  4. Under the **MAIL FROM Domain** tab, choose **Edit** in the **Custom MAIL FROM domain** pane.

  5. In the **General details** pane, do the following:

     1. Select the **Use a custom MAIL FROM domain** checkbox.

     2. For **MAIL FROM domain** , enter the subdomain that you want to use as the MAIL FROM domain.

     3. For **Behavior on MX failure** , choose one of the following options:

        * **Use default MAIL FROM domain** – If the custom MAIL FROM domain's MX record is not set up correctly, Amazon SES uses a subdomain of `amazonses.com`. The subdomain varies based on the AWS Region that you use Amazon SES in.

        * Reject message – If the custom MAIL FROM domain's MX record is not set up correctly, Amazon SES returns a `MailFromDomainNotVerified` error. Emails that you attempt to send from this email address are automatically rejected.

     4. Choose **Save changes** \- you'll be returned to the previous screen.

  6. Publish the MX and SPF (type TXT) records to the DNS server of the custom MAIL FROM domain:

In the **Custom MAIL FROM domain** pane, the **Publish DNS records** table now displays the MX and SPF (type TXT) records in that you have to publish (add) to your domain's DNS configuration. These records use the formats shown in the following table. 

Name | Type | Value  
---|---|---  
`subdomain`.`domain`.`com` | MX |  10 feedback-smtp.`region`.amazonses.com   
`subdomain`.`domain`.`com` | TXT | "v=spf1 include:amazonses.com ~all"  
  
In the preceding records,

     * `subdomain`.`domain`.`com` will be populated with your MAIL FROM subdomain

     * `region` will be populated with the name of the AWS Region where you want to verify the MAIL FROM domain (such as `us-west-2`, `us-east-1`, or `eu-west-1`, etc.)

     * The number _10_ listed along with the MX value is the preference order for the mail server and will need to be entered into a separate value field as specified by your DNS provider's GUI

     * The SPF's TXT record value has to include the quotation marks

From the **Publish DNS records** table, copy the MX and SPF (type TXT) records by choosing the copy icon next to each value and paste them into the corresponding fields in your DNS provider's GUI. Alternatively, you can choose **Download .csv record set** to save a copy of the records to your computer.

###### Important

To successfully set up a custom MAIL FROM domain with Amazon SES, you must publish exactly one MX record to the DNS server of your MAIL FROM domain. If the MAIL FROM domain has multiple MX records, the custom MAIL FROM setup with Amazon SES will fail.

If Route 53 provides the DNS service for your MAIL FROM domain, and you're signed in to the AWS Management Console under the same account that you use for Route 53, then choose **Publish Records Using Route 53**. The DNS records are automatically applied to your domain's DNS configuration.

If you use a different DNS provider, you have to publish the DNS records to the MAIL FROM domain's DNS server manually. The procedure for adding DNS records to your domain's DNS server varies based on your web hosting service or DNS provider. 

The procedures for publishing DNS records for your domain depend on which DNS provider you use. The following table includes links to the documentation for a few widely used DNS providers. This list isn't exhaustive and doesn't signify endorsement; likewise, if your DNS provider isn't listed, it doesn't imply they don't support MAIL FROM domain configuration.

DNS/Hosting provider name | Documentation link  
---|---  
GoDaddy | 
     * MX: [Add an MX record](https://www.godaddy.com/help/add-an-mx-record-19234) (external link)
     * TXT: [Add a TXT record](https://www.godaddy.com/help/add-a-txt-record-19232) (external link)  
DreamHost | 
     * MX: [How do I change my MX records?](https://help.dreamhost.com/hc/en-us/articles/215035328) (external link)
     * TXT: [How do I add custom DNS records?](https://help.dreamhost.com/hc/en-us/articles/215414867-How-do-I-add-custom-DNS-records-) (external link)  
Cloudflare | 
     * MX: [How do I add or edit mail or MX records? ](https://support.cloudflare.com/hc/en-us/articles/218069617-How-do-I-add-or-edit-mail-or-MX-records-) (external link)
     * TXT: [Managing DNS records in Cloudflare](https://support.cloudflare.com/hc/en-us/articles/360019093151) (external link)  
HostGator | 
     * MX: [Changing MX records - Windows](https://www.hostgator.com/help/article/changing-mx-records-windows) (external link)
     * TXT: [Manage DNS Records with HostGator/eNom](https://www.hostgator.com/help/article/manage-dns-records-with-hostgatorenom) (external link)  
Namecheap | 
     * MX: [How can I set up MX records required for mail service? ](https://www.namecheap.com/support/knowledgebase/article.aspx/322/2237/how-can-i-set-up-mx-records-required-for-mail-service) (external link)
     * TXT: [How do I add TXT/SPF/DKIM/DMARC records for my domain? ](https://www.namecheap.com/support/knowledgebase/article.aspx/317/2237/how-do-i-add-txtspfdkimdmarc-records-for-my-domain) (external link)  
Names.co.uk | 
     * MX: [Changing your domain's DNS settings](https://www.names.co.uk/support/domains/1156-changing_your_domains_dns_settings.html) (external link)
     * TXT: [Changing your domains DNS Settings](https://www.names.co.uk/support/1156-changing_your_domains_dns_settings.html) (external link)  
Wix | 
     * MX: [Adding or Updating MX Records in Your Wix Account](https://support.wix.com/en/article/adding-or-updating-mx-records-in-your-wix-account) (external link)
     * TXT: [Adding or Updating TXT Records in Your Wix Account](https://support.wix.com/en/article/adding-or-updating-txt-records-in-your-wix-account) (external link)  
  
When Amazon SES detects that the records are in place, you receive an email informing you that your custom MAIL FROM domain was set up successfully. Depending on your DNS provider, there might be a delay of up to 72 hours before Amazon SES detects the MX record.




## Custom MAIL FROM domain setup states with Amazon SES

After you configure an identity to use a custom MAIL FROM domain, the state of the setup is "pending" while Amazon SES attempts to detect the required MX record in your DNS settings. The state then changes depending on whether Amazon SES detects the MX record. The following table describes the email-sending behavior, and the Amazon SES actions associated with each state. Each time the state changes, Amazon SES sends a notification to the email address associated with your AWS account.

State | Email sending behavior | Amazon SES actions  
---|---|---  
Pending |  Uses custom MAIL FROM fallback setting |  Amazon SES attempts to detect the required MX record for 72 hours. If unsuccessful, the state changes to "Failed".  
Success |  Uses custom MAIL FROM domain |  Amazon SES continuously checks that the required MX record is in place.   
TemporaryFailure |  Uses custom MAIL FROM fallback setting |  Amazon SES attempts to detect the required MX record for 72 hours. If unsuccessful, the state changes to "Failed"; if successful, the state changes to "Success".  
Failed |  Uses custom MAIL FROM fallback setting |  Amazon SES no longer attempts to detect the required MX record. To use a custom MAIL FROM domain, you have to restart the setup process in Configuring your custom MAIL FROM domain. 
