# Running within FSCR on Windows and macOS

Use this repository's shared security skill in its selected implementation workflow.
Python 3.10 or newer is required; bundled analysis uses the standard library.
Do not install a second personal copy as an execution fallback.

Environment configuration follows [FSCR context](../SKILL.md#fscr-environment-and-authentication-context):
`core/auth/fusionEnv.properties` supplies the selected environment and base URL.
No host-prefix or application-username arguments are accepted. Optional
`--properties` selects the already approved workflow profile, just like the core
clients; never use it to silently switch targets.

Run from the skill folder with quoted native paths, or use repository-relative
script paths from the repository root. Use `python`, `py -3` on Windows, or
`python3` on macOS as available.

## Normalize only

```powershell
python scripts/run_from_zip.py --zip "<source.zip>" --output-directory "<project-request-directory>" --normalize-only
```

Alternatively, normalize directly:

```powershell
python scripts/normalize_job_roles_zip.py --zip "<source.zip>" --output "<project-request-directory>/calling_request.json"
```

Use a new request directory under the selected project's declared artifact
path. The source ZIP stays under the project's exports directory when produced
by an FSCR export workflow. Normalization does not log in or call Fusion.

## Assessment and Core handoff

`run_checkup.py --input <request.json> --output <result.json>` binds the selected
FSCR environment and writes the next GET-only Core request plan. It returns
exit code `2` while Core results are needed. The active workflow executes those
requests through the core REST skill and resumes with repeated
`--core-response "<request-id>=<core-result.json>"` options for every result.
Only completed retrieval produces the runtime tree, rules, and assessment.
See [the response contract](runtime-metadata-execution.md) for the envelope.

`extract_tree.py --input <request.json> --output <runtime_tree.json>` provides
the same interface for a tree-only extraction. `--request-plan-output` selects
a separate same-run plan path; `--dry-run` prints the next plan without writing
artifacts or calling Fusion. No host or login username argument is needed.

Use `--help` for supported options. Record sanitized errors and follow
[recovery](execution-recovery.md); preserve completed artifacts and do not
restart a running process. A CLI handoff alone does not execute the Core reads.
