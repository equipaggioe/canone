# Complying with DMARC authentication protocol in Amazon SES  
  
Domain-based Message Authentication, Reporting and Conformance (DMARC) is an email authentication protocol that uses Sender Policy Framework (SPF) and DomainKeys Identified Mail (DKIM) to detect email spoofing and phishing. In order to comply with DMARC, messages must be authenticated through either SPF or DKIM, but ideally, when both are used with DMARC, you'll be ensuring the highest level of protection possible for your email sending.

Let's briefly review which each does and how DMARC ties them all together:

  * SPF – Identifies which mail servers are allowed to send mail on behalf of your custom MAIL FROM domain through a DNS TXT record that is used by DNS. Recipient mail systems refer to the SPF TXT record to determine whether a message from your custom domain comes from an authorized messaging server. Basically, SPF is designed to help prevent spoofing, but there are spoofing techniques that SPF is susceptible to in practice and this is why you need to also use DKIM along with DMARC.

  * DKIM – Adds a digital signature to your outbound messages in the email header. Receiving email systems can use this digital signature to help verify whether incoming email is signed by a key owned by the domain. However, when a receiving email system forwards a message, the message's envelope is changed in a way that invalidates SPF authentication. Since the digital signature stays with the email message because it's part of the email header, DKIM works even when a message has been forwarded between mail servers (as long as the message content has not been modified).

  * DMARC – Ensures that there is domain alignment with at least one of SPF and DKIM. Using SPF and DKIM alone does nothing to insure that the From address is authenticated (this is the email address your recipient sees in their email client). SPF only checks the domain specified in the MAIL FROM address (not seen by your recipient). DKIM only checks the domain specified in the DKIM signature (also, not seen by your recipient). DMARC addresses these two issues by requiring domain alignment to be correct on either SPF or DKIM:

    * For SPF to pass DMARC alignment the domain in the From address must match the domain in the MAIL FROM address (also referred to as Return-Path and Envelope-from address). This is rarely possible with forwarded mail because it gets stripped away or when sending mail through third-party bulk email providers because the Return-Path (MAIL FROM) is used for bounces and complaints that the provider (SES) tracks using an address they own.

    * For DKIM to pass DMARC alignment, the domain specified in the DKIM signature must match the domain in the From address. If you use third-party senders or services that send mail on your behalf, this can be accomplished by ensuring the third-party sender is properly configured for DKIM signing and you have added the appropriate DNS records within your domain. Receiving mail servers will then be able to verify email sent to them by your third-party as if it was email sent by someone authorized to use an address within the domain.




###### Putting it all together with DMARC

The DMARC alignment checks we discussed above show how SPF, DKIM, and DMARC all work together to increase trust of your domain and delivery of your email to inboxes. DMARC accomplishes this by ensuring that the From address, seen by the recipient, is authenticated by either SPF or DKIM: 

  * A message passes DMARC if one or both of the described SPF or DKIM checks pass.

  * A message fails DMARC if both of the described SPF or DKIM checks fail.




Therefore, both SPF and DKIM are necessary for DMARC to have the best chance at achieving authentication for your sent email, and by utilizing all three, you'll help to ensure you have a fully protected sending domain.

DMARC also allows you to instruct email servers how to handle emails when they fail DMARC authentication through policies that you set. This will be explained in the following section, Setting up the DMARC policy on your domain, that contains information on how to configure your SES domains so that the emails you send comply with the DMARC authentication protocol through both SPF and DKIM. 

## Setting up the DMARC policy on your domain

To set up DMARC, you have to modify the DNS settings for your domain. The DNS settings for your domain should include a TXT record that specifies the domain's DMARC settings. The procedures for adding TXT records to your DNS configuration depend on which DNS or hosting provider you use. If you use Route 53, see [Working with Records](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/rrsets-working-with.html) in the _Amazon Route 53 Developer Guide_. If you use another provider, see the DNS configuration documentation for your provider.

The name of the TXT record you create should be `_dmarc.`example.com``, where ``example.com`` is your domain. The value of the TXT record contains the DMARC policy that applies to your domain. The following is an example of a TXT record that contains a DMARC policy:

Name | Type | Value  
---|---|---  
`_dmarc.example.com` | `TXT` | `"v=DMARC1;p=quarantine;rua=mailto:my_dmarc_report@example.com"`  
  
In the preceding DMARC policy example, this policy tells email providers to do the following: 

  * For any messages that fail authentication, send them to the Spam folder as specified by the policy parameter, `p=quarantine`. Other options include doing nothing by using `p=none`, or reject the message outright by using `p=reject`.

    * The next section discusses how and when to use these three policy settings— _using the wrong one at the wrong time can cause your email to not be delivered,_ see Best practices for implementing DMARC. 

  * Send reports about all emails that failed authentication in a digest (that is, a report that aggregates the data for a certain time period, rather than sending individual reports for each event) as specified by the reporting parameter, `rua=mailto:my_dmarc_report@example.com` (_rua_ stands for Reporting URI for Aggregate reports). Email providers typically send these aggregated reports once per day, although these policies differ from provider to provider.




To learn more about configuring DMARC for your domain, see the [Overview](https://dmarc.org/overview/) on the DMARC website.

For complete specifications of the DMARC system, see [Internet Engineering Task Force (IETF) DMARC Draft](https://datatracker.ietf.org/doc/draft-ietf-dmarc-dmarcbis/). 

## Best practices for implementing DMARC

It's best to implement your DMARC policy enforcement in a gradual and phased approach so that it doesn't interrupt the rest of your mail flow. Create and implement a roll-out plan that follows these steps. Do each of these steps first with each of your sub-domains, and finally with the top-level domain in your organization before moving on to the next step.

  1. Monitor the impact of implementing DMARC (p=none).

     * Start with a simple monitoring-mode record for a sub-domain or domain that requests that mail receiving organizations send you statistics about messages that they see using that domain. A monitoring-mode record is a DMARC TXT record that has its policy set to none `p=none`.

     * Reports generated through DMARC will give the numbers and sources of messages that pass these checks, versus those that don't. You can easily see how much of your legitimate traffic is or isn't covered by them. You'll see signs of forwarding, since forwarded messages will fail SPF and DKIM if the content is modified. You'll also begin to see how many fraudulent messages are being sent, and where they're sent from.

     * The goals of this step are to learn what emails will be impacted when you implement one of the next two steps, and to have any third-party or authorized senders get their SPF or DKIM policies into alignment.

     * Best for existing domains.

  2. Request that external mail systems quarantine mail that fails DMARC (p=quarantine).

     * When you believe that all or most of your legitimate traffic is sending domain-aligned with either SPF or DKIM, and you understand the impact of implementing DMARC, you can implement a quarantine policy. A quarantine policy is a DMARC TXT record that has its policy set to quarantine `p=quarantine`. By doing this, you're asking DMARC receivers to put messages from your domain that fail DMARC into the local equivalent of a spam folder instead of your customers' inboxes.

     * Best for transitioning domains that have analyzed DMARC reports during Step 1.

  3. Request that external mail systems not accept messages that fail DMARC (p=reject).

     * Implementing a reject policy is usually the final step. A reject policy is a DMARC TXT record that has its policy set to reject `p=reject`. When you do this, you're asking DMARC receivers not to accept messages that fail the DMARC checks—this means they won't even be quarantined to a spam or junk folder, but will be rejected outright.

     * When using a reject policy, you'll know exactly which messages are failing the DMARC policy as the rejection will result in a SMTP bounce. With quarantine, the aggregate data provides information about the percentages of email passing or failing SPF, DKIM, and DMARC checks.

     * Best for new domains or existing domains that have gone through the prior two steps.




## Complying with DMARC through SPF

For an email to comply with DMARC based on SPF, both of the following conditions must be met:

  * The message must pass an SPF check based on having a valid SPF (type TXT) record that you've to published to your custom MAIL FROM domain's DNS configuration.

  * The domain in the From address of the email header must align (match) with the domain, or a subdomain of, that's specified in the MAIL FROM address. In order to achieve SPF alignment with SES, the domain's DMARC policy must not specify a strict SPF policy (aspf=s).




To comply with these requirements, complete the following steps:

  * Set up a custom MAIL FROM domain by completing the procedures in [Using a custom MAIL FROM domain](./mail-from.html).

  * Ensure that your sending domain uses a relaxed policy for SPF. If you haven't changed your domain's policy alignment, it uses a relaxed policy by default as does SES.

###### Note

You can determine your domain's DMARC alignment for SPF by typing the following command at the command line, replacing ``example.com`` with your domain:
        
        dig TXT _dmarc.example.com

In the output of this command, under **Non-authoritative answer** , look for a record that begins with `v=DMARC1`. If this record includes the string `aspf=r`, or if the `aspf` string is not present at all, then your domain uses relaxed alignment for SPF. If the record includes the string `aspf=s`, then your domain uses strict alignment for SPF. Your system administrator will need to remove this tag from the DMARC TXT record in your domain's DNS configuration.

Alternatively, you can use a web-based DMARC lookup tool, such as the [DMARC Inspector](https://dmarcian.com/dmarc-inspector/) from the dmarcian website or the [DMARC Check Tool](https://mxtoolbox.com/dmarc.aspx) tool from the MxToolBox website, to determine your domain's policy alignment for SPF.




## Complying with DMARC through DKIM

For an email to comply with DMARC based on DKIM, both of the following conditions must be met:

  * The message must have a valid DKIM signature and passes the DKIM check.

  * The domain specified in the DKIM signature must align (match) with the domain in the From address. If the domain's DMARC policy specifies strict alignment for DKIM, these domains must match exactly (SES uses a strict DKIM policy by default). 




To comply with these requirements, complete the following steps:

  * Set up Easy DKIM by completing the procedures in [Easy DKIM in Amazon SES](./send-email-authentication-dkim-easy.html). When you use Easy DKIM, Amazon SES automatically signs your emails.

###### Note

Rather than use Easy DKIM, you can also [manually sign your messages](./send-email-authentication-dkim-manual.html). However, use caution if you choose to do so, because Amazon SES does not validate the DKIM signature that you construct. For this reason, we highly recommend using Easy DKIM.

  * Ensure the domain specified in the DKIM signature is aligned to the domain in the From address. Or, if sending from a subdomain of the domain in the From address, ensure that your DMARC policy is set to relaxed alignment. 

###### Note

You can determine your domain's DMARC alignment for DKIM by typing the following command at the command line, replacing ``example.com`` with your domain:
        
        dig TXT _dmarc.example.com

In the output of this command, under **Non-authoritative answer** , look for a record that begins with `v=DMARC1`. If this record includes the string `adkim=r`, or if the `adkim` string is not present at all, then your domain uses relaxed alignment for DKIM. If the record includes the string `adkim=s`, then your domain uses strict alignment for DKIM. Your system administrator will need to remove this tag from the DMARC TXT record in your domain's DNS configuration.

Alternatively, you can use a web-based DMARC lookup tool, such as the [DMARC Inspector](https://dmarcian.com/dmarc-inspector/) from the dmarcian website or the [DMARC Check Tool](https://mxtoolbox.com/dmarc.aspx) tool from the MxToolBox website, to determine your domain's policy alignment for DKIM.



