# Error Handling

## Error Situations

| Task Code | Task Name | Situation | What Should Happen |
|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | A targeted locale does not resolve to one FSM locale-state record | Stop and ask for a valid locale record ID or locale code, then complete a fresh FSM export |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | A requested locale is absent from the FSM export | Check the requested code against the `Available Knowledge Locales` section in `manage-knowledge-locales.md` to determine whether it is supported, then use the FSM export/import workflow as the tenant setup-data source; do not treat a REST response as the complete supported-locale catalog |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | A locale mutation lacks the exact exported FSM package contract | Stop before preview and request the exported package member, headers, keys, and required parent-definition rows |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | A locale mutation has a missing or blank preferred locale and the customer has not approved a supported value | Stop before preview; obtain the preferred-value choice required by design enforcement. Do not auto-fill, remove package files, or use null markers |
| ORA_CSO_FILE_ATTACHMENTS_MGMT | Manage Knowledge Files and Images | The package changes the attachment property key or creates a Files and Images row | Stop before preview; retain IMCONTENT_FILE_UPLOAD_FORMAT and existing exported Files and Images rows only |
| ORA_CSO_ARTICLE_STATUS_MGMT | Manage Knowledge Article Statuses | The package uses an invalid feature property or value, changes retained status fields, or has an unresolved active locale or orphan localized row | Stop before preview; use KM_ARTICLE_STATUS_ENABLED with TRUE or FALSE only, retain export-derived fields, and resolve the localized row's active locale and parent referenceKey from the completed task exports |
| ORA_CSO_USER_GROUPS_MGMT | Manage Knowledge User Groups | The package omits the root user-group row, uses an unapproved stripeCd, or has a localized row without the exact root referenceKey linkage | Stop before preview; restore the same-task export's root and child row shape, node sequence, retained values, and parent linkage. For a new or updated group, use only ORA_SVC_CRM, ORA_SVC_HRHD, or ORA_SVC_ISR. |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | The completed FSM export does not resolve one existing profile definition, supported level, and value row | Stop before preview; do not construct a package row or substitute an unverified profile level |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | An approved FSM import has an uncertain outcome | Do not retry the import; reconcile with one fresh export and report the result |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | The completed FSM export does not resolve one existing profile definition, supported level, and value row | Stop before preview; do not construct a package row or substitute an unverified profile level |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | An approved FSM import has an uncertain outcome | Do not retry the import; reconcile with one fresh export and report the result |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | Profile definition, Site-level flags, or Site value cannot be resolved exactly | Stop before preview; do not construct an FSM row or substitute an unverified profile level |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | Profile definition, Site-level flags, or Site value cannot be resolved exactly | Stop before preview; do not construct an FSM row or substitute an unverified profile level |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | An approved FSM import has an uncertain outcome | Do not retry the import; reconcile with one fresh task export and report the result |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | An approved FSM import has an uncertain outcome | Do not retry the import; reconcile with one fresh task export and report the result |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | The completed FSM export does not resolve one existing profile definition, supported level, and value row | Stop before preview; do not construct a package row or substitute an unverified profile level |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | An approved FSM import has an uncertain outcome | Do not retry the import; reconcile with one fresh export and report the result |
| ORA_CSO_CONTENT_TYPES_MGMT | Manage Knowledge Content Types Classic | A request bypasses the routed Redwood content-type skill | Stop before package preparation and route the request to Manage Knowledge Content Types Redwood |
| ORA_CSO_SEARCH_DICT_MGMT | Manage Knowledge Search Dictionary | A search-dictionary request lacks a completed same-task export or approved change | Stop before preview and obtain the missing package baseline or approval |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | Workflow prerequisites or approver privileges cannot be verified | Stop before configuration and identify the missing activity, lookup code, content type, or access evidence |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | A required new-workflow version, duration mapping, content-type linkage, or package member remains unresolved, or Fusion rejects an import | Stop; preserve sanitized validation or process details and do not retry the write automatically |

## Error Classifications

| Task Code | Task Name | Result Category | When Used | Next Action |
|---|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | input validation | Locale selection is missing or does not resolve to exactly one Locale object | Ask for a precise locale record ID or locale code |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | dependency readiness | A default-locale or FSM package prerequisite is not satisfied | Resolve the documented prerequisite before a mutation preview |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | artifact persistence | The completed FSM export is unavailable, ambiguous, or cannot be read | Preserve sanitized export context and stop before artifact preparation |
| ORA_CSO_FILE_ATTACHMENTS_MGMT | Manage Knowledge Files and Images | input validation | The attachment property key differs from IMCONTENT_FILE_UPLOAD_FORMAT, the extension list is not approved, or a Files and Images row is created | Restore the export-derived property key and row scope before preview |
| ORA_CSO_ARTICLE_STATUS_MGMT | Manage Knowledge Article Statuses | input validation | The package uses an invalid feature property or value, changes retained fields, or has an unresolved active locale or parent linkage | Restore the same-task export contract; use KM_ARTICLE_STATUS_ENABLED with TRUE or FALSE only; resolve the active locale before preview |
| ORA_CSO_USER_GROUPS_MGMT | Manage Knowledge User Groups | input validation | The package changes the root or localized-object contract, uses an unapproved stripeCd, or breaks root-to-localized referenceKey linkage | Restore the exact same-task export structure and retain unapproved values. For a new or updated group, use only ORA_SVC_CRM, ORA_SVC_HRHD, or ORA_SVC_ISR before preview |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | input validation | The completed export, existing profile option, supported level, or approved value is missing or ambiguous | Correct the request and resolve the FSM package contract |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | process failed | FSM validation, import, or verification export fails | Preserve sanitized diagnostics and stop without retrying the import |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | input validation | The completed export, existing profile option, supported level, or approved value is missing or ambiguous | Correct the request and resolve the FSM package contract |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | process failed | FSM validation, import, or verification export fails | Preserve sanitized diagnostics and stop without retrying the import |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | input validation | The requested code or value is missing, Site is disabled or non-updateable, or the value is not accepted | Correct the supplied profile update request or resolve the live profile contract |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | input validation | The requested code or value is missing, Site is disabled or non-updateable, or the value is not accepted | Correct the supplied profile update request or resolve the live profile contract |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | process failed | FSM validation, import, or verification export fails | Preserve sanitized diagnostics and stop without retrying the import |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | process failed | FSM validation, import, or verification export fails | Preserve sanitized diagnostics and stop without retrying the import |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | input validation | The completed export, existing profile option, supported level, or approved value is missing or ambiguous | Correct the request and resolve the FSM package contract |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | process failed | FSM validation, import, or verification export fails | Preserve sanitized diagnostics and stop without retrying the import |
| ORA_CSO_CONTENT_TYPES_MGMT | Manage Knowledge Content Types Classic | input validation | The request is not routed to the Redwood content-type skill | Route the request before preparing an FSM package |
| ORA_CSO_SEARCH_DICT_MGMT | Manage Knowledge Search Dictionary | input validation | The same-task export baseline or approved requested change is missing | Complete the export and provide the approved change before preview |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | input validation | Workflow design is incomplete or a required FSM value or relationship is unresolved | Complete approved design inputs and reconcile the four exported CSV objects before preview |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | Fusion API or process failed | Fusion rejects or fails a submitted workflow change | Preserve safe status and process log, then investigate before a new approved attempt |

## Disclosure Rules

| Task Code | Task Name | Gate | What Must Be Shown |
|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | Before a locale mutation | Exact FSM import artifact, target environment, operation, expected impact, and current explicit approval |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | Before filling a missing or blank preferred locale | Proposed preferred value, effective defaultLocale, impact on users without a personal preference, and explicit customer approval; retain the separate final Data Loader approval |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | Before an FSM package is imported | Exact approved ZIP, existing profile option, supported level, current and requested value, target environment, and current explicit approval |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | Before an FSM package is imported | Exact approved ZIP, existing profile option, supported level, current and requested value, target environment, and current explicit approval |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | Before an FSM package is imported | Profile option code, Site level, current value, exact requested value, target environment, and current explicit approval |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | Before an FSM package is imported | Profile option code, Site level, current value, exact requested value, target environment, and current explicit approval |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | Before an FSM package is imported | Exact approved ZIP, existing profile option, supported level, current and requested value, target environment, and current explicit approval |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | Before a workflow change | Show target environment, workflow name, steps, optional duration, publication choice, content types, approver policy, and any unresolved package value or relationship |

## Refusal Rules

| Task Code | Task Name | Situation | What Must Not Happen |
|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | A locale deactivation or disable operation is requested | Show: Locale deactivation is not supported. Stop before preparing, validating, or submitting a deactivation artifact; do not use an alternate execution route |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | The exact FSM package contract is not available | Do not prepare or submit a locale mutation |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | An inactive locale is needed for a review | Do not use an FSM export as the sole source of truth |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | An FSM export is header-only or lacks the required profile rows | Do not infer definition, level, or value rows; complete a usable export before preparing a package |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | An FSM import is uncertain or fails verification | Do not retry the import or issue another write |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | An FSM export is header-only or lacks the required profile rows | Do not infer definition, level, or value rows; complete a usable export before preparing a package |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | An FSM import is uncertain or fails verification | Do not retry the import or issue another write |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | An FSM export is header-only | Stop before package preparation and obtain a usable same-task export; do not infer profile rows or substitute a REST mutation |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | An FSM export is header-only | Stop before package preparation and obtain a usable same-task export; do not infer profile rows or substitute a REST mutation |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | An FSM export is header-only or lacks the required profile rows | Do not infer definition, level, or value rows; complete a usable export before preparing a package |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | An FSM import is uncertain or fails verification | Do not retry the import or issue another write |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | An FSM import is uncertain or fails verification | Do not retry the import or issue another write |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | An FSM import is uncertain or fails verification | Do not retry the import or issue another write |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | A required new-workflow value, duration mapping, content-type link, or prerequisite verification route is TBD | Do not claim import readiness or submit a generated package |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_CSO_ARTICLE_STATUS_MGMT | Manage Knowledge Article Statuses | ARTICLESTATUS.READY | terminal | 5 | terminal | none | ARTICLESTATUS.DESIGN | stop | Article Statuses guidance is ready for preview handoff |
| ORA_CSO_ARTICLE_STATUS_MGMT | Manage Knowledge Article Statuses | ARTICLESTATUS.FAILED | terminal | 6 | terminal | none | none | stop | Any Article Statuses validation, lookup, dependency, or design gate fails |
| ORA_CSO_FILE_ATTACHMENTS_MGMT | Manage Knowledge Files and Images | FILEATTACHMENTS.READY | terminal | 2 | terminal | none | FILEATTACHMENTS.VALIDATE | stop | File attachment guidance is ready for preview handoff |
| ORA_CSO_FILE_ATTACHMENTS_MGMT | Manage Knowledge Files and Images | FILEATTACHMENTS.FAILED | terminal | 3 | terminal | none | none | stop | File attachment input validation fails |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | KNOWLEDGELOCALES.READY | terminal | 5 | terminal | none | KNOWLEDGELOCALES.DESIGN | stop | Locale guidance is ready for preview handoff |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | KNOWLEDGELOCALES.FAILED | terminal | 6 | terminal | none | none | stop | Any validation, lookup, dependency, or design gate fails |
| ORA_CSO_USER_GROUPS_MGMT | Manage Knowledge User Groups | USERGROUPS.READY | terminal | 6 | terminal | none | USERGROUPS.DESIGN | stop | User group guidance is ready for preview handoff |
| ORA_CSO_USER_GROUPS_MGMT | Manage Knowledge User Groups | USERGROUPS.FAILED | terminal | 7 | terminal | none | none | stop | Any user group validation, lookup, or design gate fails |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | KNOWLEDGEPANELPROFILE.READY | terminal | 5 | terminal | none | KNOWLEDGEPANELPROFILE.DESIGN | stop | Knowledge Panel profile option guidance is ready for approval handoff |
| ORA_CSO_KNOWLEDGE_PANEL_PROFILE_MGMT | Manage Knowledge Panel Profile Options | KNOWLEDGEPANELPROFILE.FAILED | terminal | 6 | terminal | none | none | stop | Any Knowledge Panel profile option validation, lookup, or design gate fails |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | KNOWLEDGESEARCHPROFILE.READY | terminal | 5 | terminal | none | KNOWLEDGESEARCHPROFILE.DESIGN | stop | Knowledge Search profile option guidance is ready for approval handoff |
| ORA_CSO_KNOWLEDGE_SEARCH_PROFILE_MGMT | Manage Knowledge Search Profile Options | KNOWLEDGESEARCHPROFILE.FAILED | terminal | 6 | terminal | none | none | stop | Any Knowledge Search profile option validation, lookup, or design gate fails |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | MYKNOWLEDGEPROFILE.READY | terminal | 5 | terminal | none | MYKNOWLEDGEPROFILE.DESIGN | stop | My Knowledge profile option guidance is ready for approval handoff |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | KNOWLEDGECOMMONPROFILE.READY | terminal | 4 | terminal | none | KNOWLEDGECOMMONPROFILE.DESIGN | stop | Knowledge Common profile option guidance is ready for approval handoff |
| ORA_CSO_MY_KNOWLEDGE_PROFILE_MGMT | Manage My Knowledge Profile Options | MYKNOWLEDGEPROFILE.FAILED | terminal | 6 | terminal | none | none | stop | Any My Knowledge profile option validation, lookup, or design gate fails |
| ORA_MANAGE_KNOWLEDGE_COMMON_PROFILE_OPTION | Manage Knowledge Common Profile Options | KNOWLEDGECOMMONPROFILE.FAILED | terminal | 5 | terminal | none | none | stop | Any Knowledge Common profile option validation, lookup, or design gate fails |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | SERVICEREQUESTSPROFILE.READY | terminal | 5 | terminal | none | SERVICEREQUESTSPROFILE.DESIGN | stop | Knowledge for Service Requests profile option guidance is ready for approval handoff |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | SERVICEREQUESTSPROFILE.FAILED | terminal | 6 | terminal | none | none | stop | Any Knowledge for Service Requests profile option validation, lookup, dependency, or design gate fails |
| ORA_CSO_CONTENT_TYPES_MGMT | Manage Knowledge Content Types Classic | CONTENTTYPESCLASSIC.READY | terminal | 2 | terminal | none | CONTENTTYPESCLASSIC.VALIDATE | stop | Return only assisted router/Run Book handoff instructions for the exact Redwood task. The local ready plan retains Classic identity with no redirectTarget; it authorizes no Classic export, package preparation, preview or import. The destination requires its own selected context and approval. |
| ORA_CSO_CONTENT_TYPES_MGMT | Manage Knowledge Content Types Classic | CONTENTTYPESCLASSIC.FAILED | terminal | 3 | terminal | none | none | stop | Classic content-type routing validation fails |
| ORA_CSO_SEARCH_DICT_MGMT | Manage Knowledge Search Dictionary | SEARCHDICTIONARY.READY | terminal | 2 | terminal | none | SEARCHDICTIONARY.VALIDATE | stop | Search-dictionary guidance is ready for preview handoff |
| ORA_CSO_SEARCH_DICT_MGMT | Manage Knowledge Search Dictionary | SEARCHDICTIONARY.FAILED | terminal | 3 | terminal | none | none | stop | Search-dictionary input validation fails |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | KNOWLEDGEWORKFLOWS.READY | terminal | 5 | terminal | none | KNOWLEDGEWORKFLOWS.DESIGN | stop | Knowledge workflow guidance is ready for preview handoff |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | KNOWLEDGEWORKFLOWS.FAILED | terminal | 6 | terminal | none | none | stop | A Knowledge workflow validation, lookup, dependency, or design gate fails |
