# Microsoft-graph-api
1. Register Your Application
Before you can use the Microsoft Graph API, you need to register your application in Azure Active Directory (AAD) to get credentials.

Go to the Azure Portal: Azure Portal

Register an Application:

Navigate to Azure Active Directory -> App registrations.
Click New registration.
Enter a name for your app.
Set the Redirect URI (for web apps, this is where Azure AD will send tokens after authentication; for now, you can leave it empty).
Click Register.
Get Application (Client) ID and Directory (Tenant) ID:

After registration, go to your app’s Overview page to find the Application (client) ID and Directory (tenant) ID.
Create a Client Secret:

Go to Certificates & secrets -> New client secret.
Add a description and set an expiration period.
Click Add and copy the value of the client secret.
2. Set Up API Permissions
Configure API Permissions:

Go to API permissions -> Add a permission.
Select Microsoft Graph.
Choose Delegated permissions (if the app is accessing data on behalf of a user) or Application permissions (if the app is accessing data directly).
For reading emails, select permissions such as Mail.Read or Mail.ReadWrite.
Click Add.
Grant Admin Consent (if required):

In the API permissions section, click Grant admin consent for [Your Organization].
3. Authenticate and Get an Access Token
You need to authenticate and obtain an OAuth 2.0 access token to make API requests. You can use the OAuth 2.0 authorization code flow for user delegation or the client credentials flow for app-only access.

Here’s an example using the client credentials flow:

Using curl for Client Credentials Flow


Get Access Token:

bash
Copy code
curl -X POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope=https://graph.microsoft.com/.default"
Replace {tenant}, {client_id}, and {client_secret} with your Azure AD tenant ID, application (client) ID, and client secret.

Parse the Response to get the access token from the response JSON.

4. Read Emails via Microsoft Graph API
With the access token, you can now make requests to the Microsoft Graph API.

Example Request Using curl
Get Messages:

bash
Copy code
curl -X GET https://graph.microsoft.com/v1.0/me/messages \
  -H "Authorization: Bearer {access_token}"
Replace {access_token} with the token you obtained earlier.

To get messages from a specific folder or user, modify the endpoint accordingly.
