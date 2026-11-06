# Failure handling

For failures before a command starts, including `helper_unknown_error: setup refresh had errors`, read [execution startup recovery](execution-recovery.md). Classify these as local execution setup failures, separately from Python, input, and Fusion failures. The no-retry rule for unsuccessful API/metadata requests below does not prohibit bounded harmless execution startup probes before a process starts.

Classify failures as unreadable source, missing/ambiguous input, invalid normalized request, invalid runtime metadata/catalog, API lookup mismatch, authentication, transport/environment, or artifact persistence. Preserve or generate a request ID before reporting failure. Identify the affected set, reference code, or source location and the concrete missing information/action needed.

Never invent missing values, treat blank privileges as confirmed no access, partially parse a document and call it complete, or return a clean assessment after failure. Unknown caller codes are coverage limitations, not extraction failures. Evaluate recognized codes and retain known findings with the exact coverage message.

Every assessment needs fresh environment-specific metadata. Stop on unsuccessful requests, lookups not returning exactly one record, invalid pagination, missing algorithms, invalid entitlement dimensions, or empty entitlement accesses. Do not repeatedly retry or fall back to an old catalog. Temporary metadata is cleaned on success and failure; no incomplete catalog is published. Do not include credentials, bearer tokens, authentication headers, or secret-bearing responses in diagnostics.
