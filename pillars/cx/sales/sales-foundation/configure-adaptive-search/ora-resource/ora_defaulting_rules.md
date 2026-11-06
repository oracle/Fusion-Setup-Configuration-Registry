# Adaptive Search Publish Defaults

ABO initialization defaults are fixed and separately approved; see
[ora_abo_initialization.md](ora_abo_initialization.md). Clear optional workbook
`publishType` explicitly; Full REST body has only the existing nine-object
`entities` array. Do not broaden the default selective companion scope or
automatically submit Full Publish. Standalone defaults remain unchanged.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? |
|---|---|---|---|
| API version for publish | latest | The approved target-release contract confirms this version | No |
| API version for status | latest | Status is queried | No |
| publish scheduling | Immediate | Version-one scope | No; scheduled publishing is out of scope |
| publish type | selective | A nonempty document-object catalog validates the requested selection | No; add `publishType: selective` with mapped `entities` |
| publish type | full | The user explicitly requests Full Publish | Yes; collect and validate the requested object list, ask whether to retain current active objects, then use the selected mapped internal-entity array without `publishType` |
| publish type | full | Entities returns HTTP 400 `Could not find active meta model`, the response is null, `items` is null, or `items` is empty (new environment), and the user confirms the OOTB list | Yes; use the defined OOTB internal-entity array without `publishType` |
| publish type | full | The user declines the new-environment OOTB list, then supplies and validates a replacement object list | Yes; use the validated internal-entity array without `publishType` |
| live execution | false | Always before approval | No; only explicit approval can enable live execution |
| automatic post-submission polling | disabled | Every accepted POST | No; Data Loader status requires an explicit request. An ABO parent may repeat exact-job checks every 15 seconds only after verified load success and a current keep-checking choice; later status requests check once. |
