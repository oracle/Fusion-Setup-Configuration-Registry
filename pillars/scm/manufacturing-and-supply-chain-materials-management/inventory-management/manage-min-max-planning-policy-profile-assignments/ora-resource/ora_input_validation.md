# Manage Min-Max Planning Policy Profile Assignments Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Calculate policy parameters selection | IncludeInCal as Yes or No | Preserve a blank value; do not apply the Redwood UI default during Data Loader preparation | Provide Yes or No when the selection is intended | IncludeInCal is supplied for a REST/Data Loader request | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| IncludeInCal route-aware normalization | Yes writes IncludeInCal 1. No writes IncludeInCal 2. Reject any other friendly representation before Data Loader handoff. | IncludeInCal is supplied for the selected REST/Data Loader route | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MIN_MAX_POLICY_ASSIGNMENTS.VALIDATE_INCLUDE_IN_CAL | step | 10 | validate_input | valid->MIN_MAX_POLICY_ASSIGNMENTS.PREFLIGHT_DATALOADER_METADATA;invalid->RETURN_ISSUES | none | stop | IncludeInCal is supplied for a REST/Data Loader request. |
