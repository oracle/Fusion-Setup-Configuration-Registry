# Manifest labels and HTTPS origins

## Source manifests

`manifest --environment <source-environment> --base-url <source-https-origin>`
describes the source ZIP. The environment label must be a nonblank string that
matches the ZIP's ProcessEnv after surrounding spaces are trimmed; control
characters are rejected. The emitted environment comes from the ZIP metadata.
A destination environment is not a replacement label for a source export. Keep
migration source and target context separate.

`--template-only true` asserts that the ZIP contains no data rows. A populated
package cannot receive that label. `false` is valid for a current export even
when it contains no rows. Python callers must pass an actual boolean.

Both manifests and governed post-import observations use the same origin parser.
An origin consists of HTTPS, a DNS host, and an optional valid port. Credentials,
API paths, queries, fragments, malformed ports, invalid DNS-label syntax and
whitespace are rejected. An optional trailing slash is removed; host/scheme case
and default port 443 are canonicalized. Other valid ports remain significant.
For example, `https://EXAMPLE.TEST:443/` becomes `https://example.test`, while
`https://example.test/fscmRestApi` is rejected.

## Post-import observations

The independently selected target origin and each import/export observation's
origin must be valid and match after canonicalization. A shared malformed value
cannot become valid just because all three strings are identical. Invalid or
mismatched origins leave reconciliation PENDING; they cannot establish persisted
changes. Invoice Options interest verification applies the same rule.

Explicit `--compare-only` continues to compare files with persistence verification
NOT_PERFORMED. It does not claim a live import or validate a live destination.

These are offline syntax and metadata-consistency checks. A ZIP does not provide
a verifiable source URL, so the manifest cannot prove that the supplied origin
belongs to its environment or that a live export occurred. Supply source and
target information from the selected routed workflow; do not infer a deployment
destination from a source manifest.
