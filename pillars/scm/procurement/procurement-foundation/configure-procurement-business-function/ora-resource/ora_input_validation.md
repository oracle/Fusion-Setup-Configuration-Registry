# Input Validation

Validate supplied configuration values before they are submitted through the
owning setup workflow. These rules do not query Fusion, resolve LOVs, or make
REST calls.


## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Maximum File Size Megabytes is numeric and greater than or equal to 0 | Reject a negative or nonnumeric value with the documented field-level positive-number message | Saving Purchasing settings | |
| Receipt Close Tolerance Percent and Invoice Close Tolerance Percent are numbers from 0 through 100 with no more than 3 decimal places | Reject values outside the range or with more than 3 decimal places | Saving Purchasing settings | |
| Aging Period Days is a positive number when supplied | Reject zero, negative, or nonnumeric values | Saving Consignment Terms | |
| Maximum Requirement Score is a positive integer when supplied | Reject zero, negative, decimal, or nonnumeric values | Saving Sourcing settings | |
| Logo URL is an HTTP or HTTPS URL no longer than 240 characters when supplied | Reject an invalid scheme, malformed value, or overlength value | Saving abstract-listing settings | |
| Logo Width and Logo Height are nonnegative numbers when supplied | Reject negative or nonnumeric values | Saving abstract-listing settings | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PBF.VALIDATE_INPUT | step | 1 | validate_input | valid->PBF.READY;invalid->PBF.BLOCKED | none | stop | Before configuration values are submitted |
