# OAuth client setup for FSCR 26D

Use the [26D OAuth setup document](../assets/oauth-setup-fscr-26d.docx) and these
steps to guide IAM client setup and `core/auth/fusionEnv.properties` configuration.
Show the relevant screenshots as you explain each step. The user or Identity Domain
administrator performs the console actions; source instructions do not authorize
agent execution or bypass the active workflow.

## 1. Select the Fusion Applications Identity Domain

Sign in to OCI IAM as an Identity Administrator. Navigate to **Identity & Security
> Domains**, open the Identity Domain associated with the intended Fusion
Applications instance, and select **Integrated applications**. Click **Add
application**.

![Fusion Identity Domain and Integrated applications](../assets/oauth-setup-26d/01-integrated-applications.png)

## 2. Create a Mobile Application

Select **Mobile Application** and click **Launch workflow**. This is the
public-client route used with FSCR's default PKCE login.

![Mobile Application and Launch workflow](../assets/oauth-setup-26d/02-mobile-application.png)

Enter a name and description, for example the document's `FSCR` and `OAuth client
for FSCR`. The name is a display label, not the OAuth Client ID. The source says
no other entries are required on this page apart from the optional access
restriction below. Click **Submit**.

![Mobile application name and description](../assets/oauth-setup-26d/03-application-details.png)

### Optional restriction to assigned users or groups

Enable **Enforce grants as authorization** only when access should be restricted
to specific users or groups. If enabled, add the intended FSCR users or groups
through the application's **Users** or **Groups** tab after submitting. Without
those assignments, their FSCR login will not work. This optional flag is described
in the document's text; it is not visible in the supplied application-details
screenshot. IAM application assignments do not replace Fusion roles or data access.

## 3. Open OAuth configuration

Open the created application and select **OAuth configuration**. The application
**Details** tab displays an Application ID; do not use that value for `clientId`.
Obtain the OAuth Client ID from **OAuth configuration > General Information**.

![Application Details and OAuth configuration, Users, and Groups tabs](../assets/oauth-setup-26d/04-application-tabs.png)

Click **Edit OAuth configuration**.

![OAuth Client ID location and Edit OAuth configuration](../assets/oauth-setup-26d/05-edit-oauth-configuration.png)

## 4. Configure authorization code and callback

Enable the **Authorization code** grant type. Enable **Allow non-HTTPS URLs** for
the documented local callback listener and register exactly:

```text
http://127.0.0.1:8765/oauth/callback
```

Use the same value for `redirectUrl` in the local properties file. The HTTP setting
applies to this loopback callback; the Fusion origin and identity endpoints use
HTTPS. Do not enable unrelated grant types merely because they are shown.

![Authorization code grant and loopback callback](../assets/oauth-setup-26d/06-authorization-code-callback.png)

## 5. Add resource scopes

### Mandatory scopes

In **Token issuance policy**, enable **Add resources**. Use **Add scope** to add
all four scopes that the 26D document identifies as mandatory for FSCR setup:

| Resource named in the 26D document | Property |
| --- | --- |
| **Oracle Applications Cloud (Fusion)** or **Fusion Applications Cloud Service** | `scope` |
| **Oracle Fusion AI Cloud (Spectra)** | `ai_scope` |
| **Oracle Boss Cloud (Spectra)** | `boss_scope` |
| **spectra-fusion-common** | `fusion_common_scope` |

Resource names are indicative and may vary by environment. Consult the Fusion
domain administrator when needed to identify the correct resources and enable
their scopes.

![Token issuance policy and mandatory Fusion resource scopes](../assets/oauth-setup-26d/07-resource-scopes.png)

### Optional product properties and scopes

Add the following scopes only when the corresponding products or modules are part
of the FSCR implementation. Field Service and CX Unity also need their own base URLs:

| Optional resource | Properties |
| --- | --- |
| **Risk Cloud** | `rmc_scope` |
| **spectra-knowledge-management** | `km_scope` |
| **Oracle CPQ Applications Cloud (Spectra)** | `cpq_scope` |
| **Field Service** | `fs_scope`, `fs_restBaseUrl` |
| **CDP App** | `cdp_scope`, `cdp_restBaseUrl` |

#### Risk Cloud and Knowledge Management

Add the Risk Cloud scope for `rmc_scope` and the Knowledge Management scope for
`km_scope` when those modules are required.

![Optional Risk Cloud and Knowledge Management scopes](../assets/oauth-setup-26d/09-risk-knowledge-management-scopes.png)

#### CPQ (Configure Price Quote)

If the implementation includes Fusion CPQ, add its scope to the Mobile Application
and record it as `cpq_scope`. The source highlights **Oracle CPQ Applications Cloud
(Spectra)**; the resource name and scope value may differ in your environment.

![Optional CPQ resource scope highlighted in OAuth configuration](../assets/oauth-setup-26d/10-cpq-scope.png)

#### Field Service

If the implementation includes Field Service, add its scope to the Mobile
Application and record `fs_scope`. The source highlights the scope ending in
`field-service-common/`; copy the exact approved value from your environment.
The updated guide specifies that, although Field Service offers multiple scopes,
FSCR uses only this highlighted scope during implementation. Add that scope to the
Mobile Application; the other displayed Field Service scopes are not required
for this setup.

![Field Service scope highlighted in the resource list](../assets/oauth-setup-26d/11-field-service-scope.png)

Find `fs_restBaseUrl` in the **Field Service Resource App** under **Oracle Cloud
Services** in the Fusion Identity Domain console. In **OAuth configuration >
General Information**, the source highlights **Post-logout redirect URL** as the
location of the Field Service base URL. Record the service base URL, not an OAuth
callback or logout endpoint.

![Field Service Resource App showing the base URL in Post-logout redirect URL](../assets/oauth-setup-26d/12-field-service-base-url.png)

#### CX Unity (CDP)

If the implementation includes CX Unity, add its scope to the Mobile Application
and record `cdp_scope`. The source highlights the **CDP App** scope ending in
`unitycxunity`; use your environment's corresponding approved value.
The updated guide specifies that, although CX Unity offers multiple scopes,
FSCR uses only this highlighted scope during implementation. Add that scope to the
Mobile Application; the other displayed CX Unity scopes are not required for
this setup.

![CX Unity scope highlighted in the CDP App resource list](../assets/oauth-setup-26d/13-cx-unity-scope.png)

Find `cdp_restBaseUrl` in the **CDP Resource App** under **Oracle Cloud Services**
in the Fusion Identity Domain console. In **OAuth configuration > General
Information**, the source highlights **Post-logout redirect URL** as the location
of the CX Unity base URL. These resource-app screenshots identify service URLs;
the FSCR client remains the Mobile Application created in step 2.

![CDP Resource App showing the CX Unity base URL in Post-logout redirect URL](../assets/oauth-setup-26d/14-cx-unity-base-url.png)

Once all mandatory and applicable optional scopes are added, click **Submit**.
Record the exact environment-specific scope values, including any trailing `/`
shown in the Mobile Application's **OAuth configuration**. Do not strip an existing
slash or append one to a scope that has none. Do not reconstruct scopes from pod
names or copy identifiers from screenshots. Each login uses the selected service's
scope, not every scope registered on the application.

## 6. Activate and record the Client ID

Choose **Actions > Activate** and record your application's OAuth Client ID.
The screenshot shows where to activate while the status is still **Inactive**;
verify the resulting active status before attempting login.

![Activate in the application Actions menu](../assets/oauth-setup-26d/08-activate-application.png)

## 7. Configure fusionEnv.properties

Populate `core/auth/fusionEnv.properties` using the selected environment's values.
The updated 26D document includes this properties-file screenshot:

![Sample fusionEnv.properties with mandatory and optional scope groups](../assets/oauth-setup-26d/15-fusion-environment-properties.png)

The following synthetic example preserves its property names. Replace the scope
placeholders with exact registered values, retaining trailing `/` where present:

```properties
environment=YOUR_FUSION_ENVIRONMENT_NAME
restBaseUrl=https://fusion.example.invalid
clientId=YOUR_IAM_MOBILE_APPLICATION_CLIENT_ID
redirectUrl=http://127.0.0.1:8765/oauth/callback
# Mandatory FSCR scopes: copy exact values, including trailing / where present
scope=YOUR_FUSION_SCOPE
ai_scope=YOUR_FUSION_AI_SCOPE
boss_scope=YOUR_BOSS_SCOPE
fusion_common_scope=YOUR_FUSION_COMMON_SCOPE
# Optional services: configure when required by the selected workflow
km_scope=
rmc_scope=
cpq_scope=
fs_restBaseUrl=
fs_scope=
cdp_restBaseUrl=
cdp_scope=
# The source lists this proxy setting; confirm support in the selected client
enableProxy=true
```

Use the Fusion HTTPS base URL including `https://`, with no whitespace, UI route,
or REST resource path. For Field Service or Unity, supply that service's base URL
and scope when needed. The source's sample host strings are illustrative, not
literal values to copy.

The source lists `enableProxy=true` with a comment about Express mode Oracle CDN
proxy support. This entry alone does not establish that a selected client supports
proxy discovery; consult the implementation before recommending proxy changes.
Read the [current property mapping](fusion-environment-configuration.md) for service
selection, PKCE defaults, and the separation of local properties from OAuth trust.
Do not add OAuth endpoint overrides or plaintext secrets to the properties file.

## 8. Test through the authentication workflow

The document's test prompt is **fusion login**. Route that request to
[Fusion OAuth Authentication](../../../auth/fusion-oauth-authentication/SKILL.md)
and follow its declared enrollment, permissions, and browser login steps. On first
use, the user must enroll the Fusion URL, environment name, and OAuth Client ID.
Then complete browser sign-in and wait for the script's successful token-cache
write; a browser callback alone does not prove token acquisition succeeded.

Use [PKCE login and token acquisition](pkce-login-flow.md) for the detailed flow,
commands, cache reuse, and troubleshooting. A login request does not authorize
unrelated Fusion configuration changes. Do not execute this test merely because
it appears in the source document.

## Source and screenshot index

Source: updated user-provided **OAuth Setup for Oracle Fusion Setup and
Configuration Skills Registry (FSCR) Version 26D**, bundled as
[oauth-setup-fscr-26d.docx](../assets/oauth-setup-fscr-26d.docx).
All 15 extracted PNGs preserve the source image bytes. The original eight asset
filenames are retained; seven new assets are numbered 09–15. Source image numbers
below refer to `word/media/imageN.png` within the updated document.
Source SHA-256:
`72017ed6a7bfefd3f5b3a2fe69f27967b316d2b1a449214bce031d887a5ed22b`.

| Source image | Source context | Reference step |
| --- | --- | --- |
| 1 | Integrated applications | 1 |
| 2 | Add application / Mobile Application | 2 |
| 3 | Application name and description | 2 |
| 4 | Application details and tabs | 3 |
| 5 | Edit OAuth configuration | 3 |
| 6 | Authorization code and callback | 4 |
| 7 | Token issuance policy / mandatory scopes (`07-resource-scopes.png`) | 5 |
| 8 | Risk and Knowledge Management scopes (`09-risk-knowledge-management-scopes.png`) | 5 |
| 9 | CPQ scope (`10-cpq-scope.png`) | 5 |
| 10 | Field Service scope (`11-field-service-scope.png`) | 5 |
| 11 | Field Service base URL (`12-field-service-base-url.png`) | 5 |
| 12 | CX Unity scope (`13-cx-unity-scope.png`) | 5 |
| 13 | CX Unity base URL (`14-cx-unity-base-url.png`) | 5 |
| 14 | Activate application (`08-activate-application.png`) | 6 |
| 15 | Properties file (`15-fusion-environment-properties.png`) | 7 |

The screenshots contain source example identifiers, with some values masked.
They are navigation aids, not configuration values for another environment.
The supplied document governs the illustrated IAM setup. The current auth skill
and its code govern enrollment, PKCE, and token handling. The explanatory PKCE
notes and implementation caveats here supplement the document; they are not
claims that those details appear in its screenshots. If source instructions and
current implementation differ, explain the difference rather than silently
changing the authentication route.
