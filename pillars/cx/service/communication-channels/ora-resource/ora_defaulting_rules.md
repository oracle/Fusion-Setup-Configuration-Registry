# Defaulting Rules

## Standard Defaults

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | ChannelShortName | Uppercase AccountName with spaces removed | Creating a new channel | No | resolve_email_channel_by_code |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | DisplayName | AccountName | Creating a new channel and DisplayName is not provided | Yes |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | PrivatePToPAllowedFlag, EnabledFlag | Y | Creating a new channel | Yes |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | OriginalSystemReference, EndPoint, Port, APIVersion, APIId, APIPassword, AuthenticationURL, AuthorizationURL, TokenRequestURL, TokenAccessURL, AccessToken, RefreshToken, AuthToken, OpenSrCount, ChannelTypeCdLovSwitcher, BusinessUnitName, BusinessUnitNameTransientForLOV, ObjectAttributes | blank | Creating a new channel unless the contract explicitly supplies a value | Yes |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | CollabChannelCreateFlag | false | Creating a new Slack channel | No |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | BusinessUnitIdFK | BUOrgId | Creating or changing a channel after BUOrgId resolution | No |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | UpdateFlag, DeleteFlag | TRUE | Creating a new channel | No |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | CustomerTypeCd | ORA_SVC_BOTH | Creating a new channel | Yes |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | MultipleMatchesActionCd | ORA_SVC_NONE | Creating a new channel | Yes |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | NoMatchActionCd | ORA_SVC_NO_ACTION | Creating a new channel | Yes |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | IncludeSenderNameFlag, IncludeSenderEmailFlag | N | Creating a new channel | Yes |  |
| ORA_SVC_MANAGE_COMM_CHANNELS | Manage Communication Channels | SourceCd | ORA_SVC_ADMIN_UI | Creating a new channel | No |  |
| ORA_MANAGE_EMAIL_PROFILE_OPTIONS | Manage Email Profile Options | FND_APP_PROFILE_VALUE.LevelName | SITE | No supported level is supplied for a task-owned profile-value row | Yes | get_profile_option_definition |
| ORA_MANAGE_EMAIL_PROFILE_OPTIONS | Manage Email Profile Options | FND_APP_PROFILE_VALUE.LevelValue | SITE | LevelName defaults to SITE and no level value is supplied | Yes | get_profile_option_definition |
| ORA_SVC_MANAGE_INBOUND_EMAIL_PROFILE_OPTS | Manage Inbound E-Mail Profile Options | FND_APP_PROFILE_VALUE.LevelName | SITE | The task-owned exported row supports SITE and no supported level is supplied | Yes |  |
| ORA_SVC_MANAGE_INBOUND_EMAIL_PROFILE_OPTS | Manage Inbound E-Mail Profile Options | FND_APP_PROFILE_VALUE.LevelValue | SITE | LevelName defaults to SITE and no level value is supplied | Yes |  |
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTS | Manage Outbound E-Mail Profile Options | FND_APP_PROFILE_VALUE.LevelName | SITE | The task-owned exported row supports SITE and no supported level is supplied | Yes |  |
| ORA_SVC_MANAGE_OUTBOUND_EMAIL_PROFILE_OPTS | Manage Outbound E-Mail Profile Options | FND_APP_PROFILE_VALUE.LevelValue | SITE | LevelName defaults to SITE and no level value is supplied | Yes |  |
| ORA_SVC_MANAGE_OMNI_CHANNEL_PROFILE_OPTS | Manage Omnichannel Profile Options | SVC_ENABLE_OMNI | Yes | User asks for documented suggested Omnichannel enablement value | Yes | get_profile_option_definition |
| ORA_SVC_MANAGE_OMNI_CHANNEL_PROFILE_OPTS | Manage Omnichannel Profile Options | ORA_SVC_ENABLE_DEC_WITH_LIVEWINDOW | No | Redwood user experience agents are in scope | Yes | get_profile_option_definition |
| ORA_MANAGE_MCA_PROFILE_OPTIONS | Manage MCA Profile Options | SVC_MCA_RT_CHECK_EVENT_DISPATCH_INTERVAL_MS | TBD | User asks to change reverse-lookup timing without Oracle Support instruction | No | get_profile_option_definition |
| ORA_SVC_INTERACTION_PROFILE_OPTIONS | Manage Interaction Profile Options | SVC_INTERACTION_RETENTION_DAYS | TBD | User asks to configure purge retention but does not provide a retention policy | No | get_profile_option_definition |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
