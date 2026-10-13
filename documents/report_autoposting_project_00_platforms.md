# Executive Technical Report: Autoposting (Project 00)
## 7-Platform Credential Audit, Root-Cause Diagnosis & Action Plan

**Prepared For:** Muhammad Ali Kabani (MAK) / Executive Leadership  
**Prepared By:** Idrees Qurashi (AI Systems & Automation Engineer)  
**Date:** September 23, 2026  
**Status:** Architecture Structured & Ready • Blocked on Platform Owner Credentials & App Verification  

---

## 1. Executive Summary & Objective

In Autoposting (Project 00), the core pipeline architecture (Queue ➔ Media Prep ➔ 7-Platform Router ➔ Audit/Logging ➔ Gmail Drafts) is fully built and operational. 

During live integration tests, platform connection attempts across all 7 channels surfaced strict external API, developer portal, and identity verification requirements enforced by social media platforms. 

This document details the **exact real-world blockers encountered on each platform**, provides the **definitive technical fixes**, and gives MAK a clear, asynchronous action checklist to resolve credentials in one sitting without back-and-forth calls.

---

## 2. Platform-by-Platform Reality Audit & Root-Cause Diagnosis

```
+---------------------------------------------------------------------------------------------------+
| PLATFORM    | STATUS               | ROOT CAUSE & REAL-WORLD BLOCKER ENCOUNTERED                  |
+---------------------------------------------------------------------------------------------------+
| YouTube     | API Disabled / Scope | Google OAuth connects, but upload fails due to disabled       |
|             |                      | YouTube Data API v3 and unverified OAuth testing status.     |
+---------------------------------------------------------------------------------------------------+
| LinkedIn    | Connection Dropped   | OAuth token exchange fails or drops permissions due to       |
|             |                      | missing Community Management API product access in Developer |
|             |                      | Portal (requires organization page admin linkage).           |
+---------------------------------------------------------------------------------------------------+
| Facebook    | Meta Dev Ban / Lock  | Meta Developer Account flagged/banned; new account creation  |
|             |                      | blocked due to phone/identity checkpoint on Facebook.       |
+---------------------------------------------------------------------------------------------------+
| Instagram   | Meta Graph Ban       | Linked directly to Meta Developer Account; publishing requires|
|             |                      | Instagram Professional connected to verified Meta Page.      |
+---------------------------------------------------------------------------------------------------+
| TikTok      | Legal URLs Required  | TikTok for Developers app creation rejects submission        |
|             |                      | without public Terms of Service (ToS) and Privacy Policy URLs.|
+---------------------------------------------------------------------------------------------------+
| Twitter / X | Ready for Keys       | Requires elevated developer tier or standard OAuth 1.0a User |
|             |                      | context keys (API Key, Secret, Access Token, Token Secret).  |
+---------------------------------------------------------------------------------------------------+
| Pinterest   | Pending Audit        | Unchecked in initial test; requires Pinterest Business App   |
|             |                      | with pins:write and boards:write scopes enabled.             |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Deep Technical Analysis & Definitive Solutions

### 1. YouTube (Google Cloud Console)
* **What Happened:** When testing YouTube OAuth in n8n, the connection either failed to publish videos or threw `403 Access Not Configured`.
* **Root Causes:**
  1. `YouTube Data API v3` is not toggled ON in the Google Cloud Project.
  2. The Google Cloud OAuth consent screen is stuck in **Testing** mode without test user emails, causing tokens to expire after 7 days or throw `400: access_denied`.
* **Definitive Fix:**
  1. Open [Google Cloud Console Library](https://console.cloud.google.com/apis/library), search for **YouTube Data API v3**, and click **Enable**.
  2. In **OAuth consent screen**, set status to **Publish App** (or add your Google email to *Test Users*).
  3. Under Scopes, verify `https://www.googleapis.com/auth/youtube.upload` is added.
* **Where to Enter in n8n:**  
  `Credentials` ➔ `YouTube OAuth2 API` ➔ Enter Client ID & Secret from Google Cloud ➔ Click `Connect my account`.

---

### 2. LinkedIn (Company Pages & Personal Profiles)
* **What Happened:** Encountered connection issues during authentication and scope authorization.
* **Root Causes:**
  1. Standard LinkedIn OAuth only grants personal profile access (`w_member_social`). 
  2. Posting to a Company Page requires the **Community Management API** product enabled inside the LinkedIn Developer Portal (`developer.linkedin.com`), which requires submitting the Company Page for verification.
* **Definitive Fix:**
  1. In the LinkedIn Developer App, click the **Products** tab.
  2. Request access to **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**.
  3. If posting to a Company Page, request **Community Management API** and verify ownership via the company administrator link.
* **Where to Enter in n8n:**  
  `Credentials` ➔ `LinkedIn OAuth2 API` ➔ Enter Client ID, Client Secret, and connect.

---

### 3. Facebook Pages (Meta for Developers)
* **What Happened:** Meta Developer account was banned/restricted, and creating a fresh Facebook account immediately triggered automated identity checkpoints and phone verification blocks.
* **Root Causes:**
  1. Meta's anti-fraud algorithm aggressively flags newly created personal accounts that immediately access `developers.facebook.com`.
  2. Creating developer apps requires an aged, identity-verified personal Facebook account with 2-Factor Authentication enabled.
* **Definitive Fix:**
  1. **Do not create new dummy Facebook accounts** (Meta will continue banning them via browser fingerprinting).
  2. Use MAK's existing, verified personal Facebook profile (or an established team member's account) that already has admin access to the target Facebook Page.
  3. In `developers.facebook.com`, create a business app, add the **Facebook Login for Business** and **Pages API** products.
* **Where to Enter in n8n:**  
  `Credentials` ➔ `Facebook Graph API` ➔ Paste App ID, App Secret, and click `Connect my account` using the verified owner login.

---

### 4. Instagram Professional / Business
* **What Happened:** Blocked under the same Meta Developer restriction as Facebook.
* **Root Causes:**
  1. Instagram content publishing cannot be done with a standard personal account. It requires an **Instagram Professional / Creator / Business** account linked directly to a Facebook Page.
  2. Meta App permissions require `instagram_basic` and `instagram_content_publish`.
* **Definitive Fix:**
  1. Ensure the Instagram account is converted to a Professional account in the Instagram mobile app settings.
  2. Link the Instagram Professional account to the official Facebook Page under `Page Settings > Linked Accounts > Instagram`.
  3. Once the Meta Developer App is set up under the verified profile, authenticate via `Facebook Graph API` in n8n (this grants access to both Facebook and Instagram simultaneously).
* **Where to Enter in n8n:**  
  Handled through the verified `Facebook Graph API` credential in n8n.

---

### 5. TikTok (TikTok for Developers)
* **What Happened:** Developer registration and app submission were blocked because the portal mandates live, public URLs for legal documentation.
* **Root Causes:**
  1. TikTok for Developers requires a **Terms of Service URL** and a **Privacy Policy URL** before approving app status or generating production client keys for the Content Posting API.
* **Definitive Fix:**
  1. Host two basic compliance landing pages (e.g. `https://kabani.com/terms` and `https://kabani.com/privacy`, or use a free Notion / GitHub Pages public link).
  2. In the TikTok Developer Portal, create an App under the Business Account, paste the public Terms and Privacy URLs, and select the **Content Posting API** scope.
* **Where to Enter in n8n:**  
  `Credentials` ➔ `TikTok OAuth2 API` ➔ Paste Client Key and Client Secret.

---

### 6. Twitter / X (Developer Portal)
* **What Happened:** Not fully configured due to credential key requirements.
* **Root Causes:**
  1. Twitter v2 API requires an App created inside the X Developer Portal with **Read and Write** permissions enabled.
  2. By default, n8n's Twitter node uses OAuth 1.0a User Context, which requires 4 distinct strings: API Key, API Key Secret, Access Token, and Access Token Secret.
* **Definitive Fix:**
  1. Log into [X Developer Portal](https://developer.x.com).
  2. Under User Authentication Settings, toggle **Read and Write** permissions and select **Web App**.
  3. Generate and copy all 4 credentials:
     * API Key (Consumer Key)
     * API Secret (Consumer Secret)
     * Access Token
     * Access Token Secret
* **Where to Enter in n8n:**  
  `Credentials` ➔ `Twitter OAuth1 API` ➔ Paste all 4 keys.

---

### 7. Pinterest (Pinterest for Developers)
* **What Happened:** Unchecked during initial run.
* **Root Causes:**
  1. Requires a Pinterest Business account converted to developer status at `developers.pinterest.com`.
  2. Needs an app with scopes: `boards:read, boards:write, pins:read, pins:write`.
* **Definitive Fix:**
  1. Log into [Pinterest Developers](https://developers.pinterest.com) with the business account.
  2. Create an App named `Autoposting Bot`.
  3. Set redirect URI to n8n's OAuth callback URL: `https://[your-n8n-url]/rest/oauth2-credential/callback`.
* **Where to Enter in n8n:**  
  `Credentials` ➔ `Pinterest OAuth2 API` ➔ Paste App ID, App Secret, and authenticate.

---

## 4. Canvas Cleanup Completed on Idrees's n8n Instance

In accordance with MAK's direct review notes, the following maintenance actions were executed:
1. **Disconnected Nodes Removed:** Deleted the two unattached floating nodes (`Drive upload` and `"Upload a video"`) from the canvas.
2. **Public Endpoint Swapped:** Removed the public `webhook.site` test endpoint from the HTTP Request node to protect internal tokens and media URLs.
3. **Trigger Upgraded:** Replaced the manual test trigger with a scheduled cron trigger (`Schedule Trigger`).

---

## 5. Master Asynchronous Action Checklist for MAK

To complete the setup in one sitting without back-and-forth calls, MAK can complete the following credentials in n8n:

- [ ] **1. YouTube:** Enable `YouTube Data API v3` in Google Cloud Console; connect account via `Credentials > YouTube OAuth2 API`.
- [ ] **2. Facebook & Instagram:** Log in with established personal Facebook profile managing the business page; connect via `Credentials > Facebook Graph API`.
- [ ] **3. LinkedIn:** Request *Share on LinkedIn* in Developer Portal; connect via `Credentials > LinkedIn OAuth2 API`.
- [ ] **4. Twitter / X:** Generate Read/Write tokens in X Developer Portal; paste 4 keys in `Credentials > Twitter OAuth1 API`.
- [ ] **5. TikTok:** Provide public Terms/Privacy URLs in Developer Portal; connect via `Credentials > TikTok OAuth2 API`.
- [ ] **6. Pinterest:** Create App in Pinterest Developer Portal; connect via `Credentials > Pinterest OAuth2 API`.

Once credentials are saved, Idrees will execute single live post tests across each branch to confirm end-to-end publishing.
