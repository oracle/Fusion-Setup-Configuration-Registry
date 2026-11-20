# Defaulting Rules

## Standard Defaults

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | Default Knowledge locale | English, United States locale set automatically | No default locale has been changed by the organization | Yes |  |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | User knowledge locale | User language and territory preference | The user has not set a preferred locale and no default preferred Knowledge locale is set | Yes |  |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | LevelName | SITE | No supported profile level is supplied for a task-owned profile-value row | No | resolve_fsm_service_requests_profile_option_export |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | LevelValue | SITE | LevelName defaults to SITE and no level value is supplied | No | resolve_fsm_service_requests_profile_option_export |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | ProfileOptionValue (CSO_AUTO_PDF_TITLE_DISCOVERY) | Y | Seed baseline for CSO_AUTO_PDF_TITLE_DISCOVERY. Enable automatic discovery of visual PDF titles for search. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | ProfileOptionValue (CSO_ENABLE_AUTO_PRODUCT_CONCEPT_GENERATION) | N | Seed baseline for CSO_ENABLE_AUTO_PRODUCT_CONCEPT_GENERATION. Generate search dictionary concepts from the product hierarchy. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | ProfileOptionValue (CSO_ENABLE_INDEX_ARTICLE_ATTACHMENTS) | Y | Seed baseline for CSO_ENABLE_INDEX_ARTICLE_ATTACHMENTS. Enable processing of article attachment contents for search. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | ProfileOptionValue (CSO_EXTENSIONS_NOT_TO_INDEX) | .xls,.xlsx | Seed baseline for CSO_EXTENSIONS_NOT_TO_INDEX. Specify a comma-separated list of file extensions to skip during content processing. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | ProfileOptionValue (CSO_FILE_SIZE_LIMIT) | 10 | Seed baseline for CSO_FILE_SIZE_LIMIT. Specify the raw file-size limit in MB used during content processing. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | ProfileOptionValue (ORA_CSO_ENABLE_KNOWLEDGE_INSERT_AS_TEXT) | Y | Supplied seed baseline for ORA_CSO_ENABLE_KNOWLEDGE_INSERT_AS_TEXT. Enable users in Service Center with the Classic User Experience to insert article text into a message. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | ProfileOptionValue (CSO_ENABLE_CATEGORY_FILTER) | Y | Supplied seed baseline for CSO_ENABLE_CATEGORY_FILTER. Enable the category filter for Search and Recommended results. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | ProfileOptionValue (CSO_ENABLE_KNOWLEDGE_LINKING) | Y | Supplied seed baseline for CSO_ENABLE_KNOWLEDGE_LINKING. Enable linking a Knowledge article to a Service Request. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | ProfileOptionValue (CSO_ENABLE_LOCALE_FILTER) | Y | Supplied seed baseline for CSO_ENABLE_LOCALE_FILTER. Enable the locale filter for Search results. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | ProfileOptionValue (CSO_ENABLE_PRODUCT_FILTER) | Y | Supplied seed baseline for CSO_ENABLE_PRODUCT_FILTER. Enable the product filter for Search and Recommended results. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | ProfileOptionValue (CSO_SHOW_ARTICLE_SNIPPET) | Y | Supplied seed baseline for CSO_SHOW_ARTICLE_SNIPPET. Show article snippets in Search and Recommended results. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | ProfileOptionValue (CSO_TYPEAHEAD_CATEGORY_LOV_ENABLED) | N | Supplied seed baseline for CSO_TYPEAHEAD_CATEGORY_LOV_ENABLED. Enable the type-ahead category picker for My Knowledge. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | ProfileOptionValue (CSO_ENABLE_HCM_KMHOME) | N | Supplied seed baseline for CSO_ENABLE_HCM_KMHOME. Enable the My Knowledge menu for Help Desk. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | ProfileOptionValue (CSO_ENABLE_SVC_KMHOME) | N | Supplied seed baseline for CSO_ENABLE_SVC_KMHOME. Enable the My Knowledge menu for Service. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | ProfileOptionValue (CSO_RECENTLY_UPDATED_TIME_PERIOD) | 30 | Supplied seed baseline for CSO_RECENTLY_UPDATED_TIME_PERIOD. Specify the time period in days for displaying recently published articles. Use only as reference when reviewing the selected option; an update still requires an explicitly approved value. | No |  |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | KNOWLEDGESEARCHPROFILE.DEFAULTS | step | 3 | apply_default | ok->KNOWLEDGESEARCHPROFILE.DESIGN;failure->KNOWLEDGESEARCHPROFILE.FAILED | KNOWLEDGESEARCHPROFILE.LOOKUP | stop | After resolving the existing profile, report its listed seed baseline when applicable and retain the explicit approved ProfileOptionValue. Never fill a missing update value, overwrite an existing configured value, or infer a seed default for an unlisted profile. |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | KNOWLEDGEPANELPROFILE.DEFAULTS | step | 3 | apply_default | ok->KNOWLEDGEPANELPROFILE.DESIGN;failure->KNOWLEDGEPANELPROFILE.FAILED | KNOWLEDGEPANELPROFILE.LOOKUP | stop | After resolving the existing profile, report its listed supplied seed baseline when applicable and retain the explicit approved ProfileOptionValue. Never fill a missing update value, overwrite an existing configured value, or infer a seed default for an unlisted profile. |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | MYKNOWLEDGEPROFILE.DEFAULTS | step | 3 | apply_default | ok->MYKNOWLEDGEPROFILE.DESIGN;failure->MYKNOWLEDGEPROFILE.FAILED | MYKNOWLEDGEPROFILE.LOOKUP | stop | After resolving the existing profile, report its listed supplied seed baseline when applicable and retain the explicit approved ProfileOptionValue. Never fill a missing update value, overwrite an existing configured value, or infer a seed default for an unlisted profile. |

## Knowledge Panel Source Notes

The six Knowledge Panel seed baselines above are supplied authoring guidance,
not observed tenant values or automatic update values. They do not limit the
task to those six codes; resolve any selected existing profile through the
completed task export.

Oracle's [Configure Knowledge in Service Requests](https://docs.oracle.com/en/cloud/saas/fusion-service/faeik/configure-knowledge-in-service-requests.html)
corroborates the category, linking, locale, product, and snippet descriptions.
It says most new implementations enable these features, without guaranteeing
every seed value. The insert-as-text profile and its seed value remain supplied
guidance, not independently verified Oracle-documented facts. Release-specific
26D, 26C, 26B, and 26A topic URLs could not be retrieved on 2026-11-04; the cited
page is unversioned, so latest-release verification remains a documentation gap.

## My Knowledge Source Notes

The four My Knowledge seed baselines above are supplied authoring guidance,
not observed tenant values or automatic update values. They do not limit the
task to those four codes; resolve a selected existing profile through the
completed task export and preserve the explicitly approved update value.

Oracle's [Configure My Knowledge Features](https://docs.oracle.com/en/cloud/saas/fusion-service/faeik/configure-my-knowledge-features.html)
corroborates the Help Desk and Service menu purposes and the 30-day recent-article
default. Its statement that most new implementations enable the menus differs
from the supplied N seed baselines. Do not use either source to infer a tenant's
current menu values. The type-ahead category profile and its supplied N seed
value were not independently verified in that public guide. The 26D topic
could not be retrieved on 2026-11-04; the cited page is unversioned, so
latest-release verification remains a documentation gap.
