#!/usr/bin/env python3
"""Validate sanitized readiness JSON and render HTML; no network or secret reads."""
import argparse
from collections import Counter
from datetime import datetime
from html import escape
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

CATEGORIES = (
    "environment_authentication", "catalog_readiness",
    "offering_functional_area_readiness", "setup_task_readiness",
    "data_loader_readiness", "runbook_read_readiness",
    "privilege_connectivity",
)
STATUSES = ("PASS", "REVIEW NEEDED", "NOT APPLICABLE")
LEGACY_REVIEW_STATUSES = ("FAIL", "BLOCKED", "POTENTIAL BLOCKER")
REVIEW_REASONS = ("confirmed_issue", "verification_incomplete", "framework_limitation")
STAGES = ("pre_runbook", "full_readiness")
FAILURES = {
    "input_validation", "catalog_or_metadata_mismatch", "auth_expired_or_invalid",
    "authorization_or_privilege", "transport_or_environment", "fusion_api_error",
    "process_timeout", "process_failed", "artifact_persistence", "approval_blocker",
}
ARRAYS = ("repository_evidence", "live_environment_evidence", "artifact_references", "external_identifiers")


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")


def check_status(check):
    """Normalize review labels without rewriting historical evidence."""
    return "REVIEW NEEDED" if check["status"] in LEGACY_REVIEW_STATUSES else check["status"]


def report_categories(report):
    """Keep historical write-check reports under their original coverage rules."""
    if any(isinstance(check, dict) and check.get("category") == "runbook_write_verification"
           for check in report.get("checks", [])):
        return CATEGORIES[:-1] + ("runbook_write_verification", CATEGORIES[-1])
    return CATEGORIES


def validate_report(report):
    if not isinstance(report, dict):
        raise ValueError("Report must be an object")
    stage = report.get("assessment_stage", "full_readiness")
    if stage not in STAGES:
        raise ValueError("assessment_stage must be pre_runbook or full_readiness; record skips as decisions")
    for key in ("run_id", "generated_at"):
        require_text(report.get(key), key)
    try:
        generated_at = datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("generated_at must be an ISO-8601 timestamp with a timezone") from error
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must be an ISO-8601 timestamp with a timezone")
    environment = report.get("target_environment")
    scope = report.get("selected_scope")
    if not isinstance(environment, dict) or not isinstance(scope, dict):
        raise ValueError("target_environment and selected_scope must be objects")
    for key in ("name", "base_url", "release"):
        require_text(environment.get(key), f"target_environment.{key}")
    url = urlsplit(environment["base_url"])
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError("base_url must be a credential-free HTTPS URL without query or fragment")
    for key in ("pillar", "offering"):
        require_text(scope.get(key), f"selected_scope.{key}")
    for key in ("functional_areas", "planned_setup_tasks"):
        if not isinstance(scope.get(key), list) or any(not isinstance(x, str) or not x.strip() for x in scope[key]):
            raise ValueError(f"selected_scope.{key} must be a text array")
    if "task_details" in scope:
        details = scope["task_details"]
        if not isinstance(details, list) or len(details) != len(scope["planned_setup_tasks"]):
            raise ValueError("task_details must contain one row per planned setup task occurrence")
        sequences = set()
        for row in details:
            if not isinstance(row, dict):
                raise ValueError("task_details rows must be objects")
            for key in ("functional_area_code", "functional_area_name", "task_code", "task_name", "phase"):
                require_text(row.get(key), f"task_details.{key}")
            if scope["functional_areas"] and row["functional_area_code"] not in scope["functional_areas"]:
                raise ValueError("task_details functional area must belong to selected functional_areas")
            sequence = row.get("sequence")
            if type(sequence) is not int or sequence < 1 or sequence in sequences:
                raise ValueError("task_details sequences must be unique positive integers")
            sequences.add(sequence)
    checks = report.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("checks must be a nonempty array")
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ValueError(f"Check {index} must be an object")
        for key in ("check_name", "recommended_remediation", "notes"):
            require_text(check.get(key), f"Check {index}: {key}")
        if check.get("category") not in report_categories(report) or check.get("status") not in (*STATUSES, *LEGACY_REVIEW_STATUSES):
            raise ValueError(f"Check {index}: invalid category or status")
        if check["status"] == "REVIEW NEEDED" and check.get("review_reason") not in REVIEW_REASONS:
            raise ValueError(f"Check {index}: REVIEW NEEDED requires a valid review_reason")
        for field in ("support_action", "implementation_message"):
            if field in check or check["status"] == "REVIEW NEEDED":
                require_text(check.get(field), f"Check {index}: {field}")
        if type(check.get("required")) is not bool:
            raise ValueError(f"Check {index}: required must be boolean")
        for key in ARRAYS:
            if not isinstance(check.get(key), list) or any(not isinstance(x, str) or not x.strip() for x in check[key]):
                raise ValueError(f"Check {index}: {key} must be a text array")
        if "failure_classification" not in check:
            raise ValueError(f"Check {index}: failure_classification is required")
        failure = check["failure_classification"]
        if check_status(check) == "REVIEW NEEDED":
            if failure not in FAILURES:
                raise ValueError(f"Check {index}: failure classification required")
        elif failure is not None:
            raise ValueError(f"Check {index}: passing/inapplicable checks require null classification")
        if check["status"] == "PASS" and not check["live_environment_evidence"]:
            raise ValueError(f"Check {index}: PASS requires live evidence")
        if stage == "pre_runbook" and check["category"] == "runbook_write_verification":
            if (check["status"] != "NOT APPLICABLE" or not check["required"]
                    or check["live_environment_evidence"] or check["external_identifiers"]):
                raise ValueError("pre_runbook excludes Run Book writes; require NOT APPLICABLE without live write evidence or IDs")
        if stage == "full_readiness" and check["category"] == "runbook_write_verification":
            if check["status"] == "NOT APPLICABLE" or not check["required"]:
                raise ValueError("full_readiness requires Run Book write verification; unavailable or declined writes must be REVIEW NEEDED")
    required = [check for check in checks if check["required"]]
    coverage = {check["category"] for check in required}
    if (coverage != set(report_categories(report))
            or any(check_status(check) == "REVIEW NEEDED" for check in required)
            or not any(check["status"] == "PASS" for check in required)):
        decision = "NOT READY"
    elif any(check_status(check) == "REVIEW NEEDED" for check in checks):
        decision = "READY WITH WARNINGS"
    else:
        decision = "READY"
    if report.get("overall_decision") != decision:
        raise ValueError(f"overall_decision must be {decision}")
    return decision


def e(value):
    return escape(str(value), quote=True)


def lines(values):
    return "<ul>" + "".join(f"<li>{e(value)}</li>" for value in values) + "</ul>" if values else "<span>None recorded</span>"


def summarize_report(report):
    """Derive display metrics without treating planned scope as completed work."""
    decision = validate_report(report)
    checks = report["checks"]
    counts = Counter(check_status(check) for check in checks)
    required = [check for check in checks if check["required"]]
    coverage = {check["category"] for check in required}
    applicable = [check for check in required if check["status"] != "NOT APPLICABLE"]
    scope = report["selected_scope"]
    return {
        "decision": decision,
        "assessment_stage": report.get("assessment_stage", "full_readiness"),
        "recorded_checks": len(checks),
        "status_counts": {status: counts[status] for status in STATUSES},
        "required_categories_recorded": len(coverage),
        "required_categories_expected": len(report_categories(report)),
        "missing_required_categories": [category for category in report_categories(report) if category not in coverage],
        "required_applicable_checks": len(applicable),
        "required_applicable_passes": sum(check["status"] == "PASS" for check in applicable),
        "functional_area_count": len(scope["functional_areas"]) or None,
        "planned_task_count": len(scope["planned_setup_tasks"]) or None,
    }


def metric(label, value, note, tone="neutral"):
    return (f'<div class="metric {tone}"><dt>{e(label)}</dt><dd>{e(value)}</dd>'
            f'<p>{e(note)}</p></div>')


def executive_summary(report, metrics):
    counts = metrics["status_counts"]
    cards = [
        metric("Recorded checks", metrics["recorded_checks"], "Check rows in this assessment; not tasks executed."),
        metric("Passed checks", counts["PASS"], "Recorded evidence supports the stated check.", "pass"),
        metric("Review needed", counts["REVIEW NEEDED"], "Review the finding and choose a next step.", "blocked"),
        metric("Not applicable", counts["NOT APPLICABLE"], "Declared scope or stage exclusions; not passes."),
        metric("Required categories", f'{metrics["required_categories_recorded"]} / {metrics["required_categories_expected"]}',
               "Categories with at least one required result; not a pass rate."),
    ]
    scope_cards = [
        metric("Planned task occurrences", metrics["planned_task_count"] if metrics["planned_task_count"] is not None else "Not enumerated",
               "Planned scope only. Task execution and completion are not measured here."),
        metric("Functional areas", metrics["functional_area_count"] if metrics["functional_area_count"] is not None else "Not enumerated",
               "Selected scope entries; empty input means full offering scope."),
        metric("Required applicable checks passed",
               f'{metrics["required_applicable_passes"]} / {metrics["required_applicable_checks"]}',
               "Excludes NOT APPLICABLE rows; zero applicable checks cannot establish readiness."),
    ]
    return ('<section aria-labelledby="metrics-heading"><h2 id="metrics-heading">Readiness at a glance</h2>'
            '<dl class="metrics">' + "".join(cards) + '</dl>'
            '<h3>Assessment scope</h3><dl class="metrics scope-metrics">' + "".join(scope_cards) + '</dl>'
            '<p class="boundary">These numbers summarize recorded assessment evidence. They are not an implementation '
            'completion percentage or proof of production readiness. Missing required categories are shown separately '
            'and are not invented check results.</p></section>')


def findings_table(report, metrics):
    rows = []
    for category in metrics["missing_required_categories"]:
        rows.append(
            f'<tr><th scope="row">{e(category.replace("_", " ").title())}</th>'
            '<td><strong class="blocked">Missing required result</strong><small>Prevents readiness</small></td>'
            '<td>Retry the assessment to obtain this missing result, or explicitly override the finding after reviewing the missing coverage. Do not infer a pass '
            'from an advisory result or from the absence of a failure.</td>'
            '<td>No required result was supplied for this category.</td></tr>')
    findings = [check for check in report["checks"] if check_status(check) == "REVIEW NEEDED"]
    # Required blockers first, retaining input order within each priority.
    for check in sorted(findings, key=lambda row: not row["required"]):
        evidence = ('<details><summary>Support and technical details</summary>'
                    + '<p>' + e(check.get("support_action", "Share these diagnostics with FSCR support if help is needed.")) + '</p>'
                    + '<p>' + e(check.get("review_reason", "confirmed_issue" if check["status"] == "FAIL" else "verification_incomplete"))
                    + ' · ' + e(check["failure_classification"]) + '</p>'
                    + "<strong>Repository</strong>" + lines(check["repository_evidence"])
                    + "<strong>Recorded environment observations</strong>" + lines(check["live_environment_evidence"])
                    + "<strong>Artifacts</strong>" + lines(check["artifact_references"])
                    + '<p>' + e(check["notes"]) + '</p></details>')
        rows.append(
            f'<tr><th scope="row">{e(check.get("implementation_message", check["check_name"]))}<small>{e(check["category"].replace("_", " ").title())}</small></th>'
            f'<td><strong class="{check_status(check).split()[0].lower()}">{e(check_status(check))}</strong>'
            f'<small>{"Required — prevents readiness" if check["required"] else "Advisory — warning"}</small>'
            '</td>'
            f'<td>{e(check["recommended_remediation"])}</td><td>{evidence}</td></tr>')
    if rows:
        content = ('<div class="scroll"><table class="findings"><thead><tr><th>Finding</th><th>Impact</th>'
                   '<th>Recommended action for you</th><th>Evidence supplied</th></tr></thead><tbody>'
                   + "".join(rows) + '</tbody></table></div>')
    elif metrics["decision"] == "NOT READY":
        content = '<p class="blocked">No required applicable check passed. Record supported passing evidence before claiming readiness.</p>'
    else:
        content = '<p>No checks needing review or missing required categories are recorded for this assessment. Review the exclusions and scope limitations below.</p>'
    excluded = [check for check in report["checks"] if check["status"] == "NOT APPLICABLE"]
    if excluded:
        content += '<h3>Excluded checks</h3><ul>' + "".join(
            f'<li><strong>{e(check["check_name"])}</strong> — {e(check["notes"])}</li>' for check in excluded) + '</ul>'
    return '<section id="findings"><h2>Findings and next actions</h2>' + content + '</section>'


def scope_tables(scope):
    """Render local fragment-linked tables without scripts or external links."""
    details = scope.get("task_details", [])
    areas = scope["functional_areas"]
    area_rows = []
    for code in areas:
        tasks = [row for row in details if row["functional_area_code"] == code]
        names = list(dict.fromkeys(row["functional_area_name"] for row in tasks))
        area_rows.append(f'<tr><th scope="row">{e(code)}</th><td>{e(", ".join(names) or "Name not recorded")}</td>'
                         f'<td>{len(tasks) if details else "Not recorded"}</td></tr>')
    task_rows = []
    if details:
        for row in sorted(details, key=lambda row: row["sequence"]):
            task_rows.append(f'<tr><td>{row["sequence"]}</td><td>{e(row["functional_area_name"])}'
                             f'<small>{e(row["functional_area_code"])}</small></td>'
                             f'<th scope="row">{e(row["task_name"])}</th><td>{e(row["task_code"])}</td>'
                             f'<td>{e(row["phase"])}</td></tr>')
    else:
        # Older reports retain their exact task text; never guess area ownership.
        for index, task in enumerate(scope["planned_setup_tasks"], 1):
            task_rows.append(f'<tr><td>{index}</td><td>Not recorded</td><th scope="row">{e(task)}</th>'
                             '<td>Not recorded</td><td>Not recorded</td></tr>')
    def panel(identifier, title, headings, rows, empty):
        content = ('<div class="scroll"><table class="scope-table"><caption>' + e(title) + '</caption><thead><tr>'
                   + ''.join(f'<th scope="col">{e(heading)}</th>' for heading in headings)
                   + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>') if rows else f'<p>{e(empty)}</p>'
        return (f'<section id="{identifier}" class="scope-panel" aria-labelledby="{identifier}-heading">'
                f'<h2 id="{identifier}-heading">{e(title)}</h2><p><a href="#report-summary">Close table and return to summary</a></p>'
                + content + '</section>')
    return (panel("functional-area-table", "Functional areas", ("Code", "Functional area", "Planned tasks"),
                  area_rows, "Full offering coverage; individual functional areas were not enumerated in this report.")
            + panel("setup-task-table", "Planned setup tasks", ("Sequence", "Functional area", "Task", "Task code", "Phase"),
                    task_rows, "All applicable tasks are in scope; individual tasks were not enumerated in this report."))


def render(report):
    metrics = summarize_report(report)
    decision = metrics["decision"]
    stage = metrics["assessment_stage"]
    stage_label = ("Before Run Book creation — write access remains unverified"
                   if stage == "pre_runbook" else ("Historical full environment readiness" if "runbook_write_verification" in report_categories(report)
                         else "Standalone environment readiness — read-only; write access remains unverified"))
    env = report["target_environment"]
    scope = report["selected_scope"]
    sections = []
    for category in report_categories(report):
        rows = []
        for check in report["checks"]:
            if check["category"] != category:
                continue
            evidence = "<strong>Repository</strong>" + lines(check["repository_evidence"])
            evidence += "<strong>Recorded environment observations</strong>" + lines(check["live_environment_evidence"])
            details = "<strong>Artifacts</strong>" + lines(check["artifact_references"])
            details += "<strong>External identifiers</strong>" + lines(check["external_identifiers"])
            rows.append(
                f'<tr><th scope="row">{e(check["check_name"])}<small>{"Required" if check["required"] else "Advisory"}</small></th>'
                f'<td><b class="{check_status(check).split()[0].lower()}">{e(check_status(check))}</b>'
                f'<small>{e(check["failure_classification"] or "—")}</small></td>'
                f'<td>{evidence}</td><td>{e(check["recommended_remediation"])}<p>{e(check["notes"])}</p>'
                f'<details><summary>References and identifiers</summary>{details}</details></td></tr>'
            )
        if rows:
            missing = ('<p class="blocked">Required result missing. Advisory rows do not satisfy required coverage.</p>'
                       if category in metrics["missing_required_categories"] else "")
            sections.append(f'<section><h2>{e(category.replace("_", " ").title())}</h2>{missing}<details><summary>Technical check details</summary><div class="scroll"><table>'
                            '<thead><tr><th>Check</th><th>Status / classification</th><th>Evidence</th><th>Recommended solution / notes</th></tr></thead>'
                            '<tbody>' + "".join(rows) + '</tbody></table></div></details></section>')
        else:
            sections.append(f'<section><h2>{e(category.replace("_", " ").title())}</h2><p class="blocked">Missing required result — no check was supplied.</p></section>')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>FSCR Prevalidation</title><style>
body{font:16px/1.5 system-ui,sans-serif;color:#203039;background:#f3f5f5;margin:0}
main{max-width:1500px;margin:auto;padding:32px}header,section{background:white;border:1px solid #d8e0e1;border-radius:12px;padding:24px;margin-bottom:20px}
header{border-top:7px solid #285a50}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.13em;font-weight:700;color:#52616a}
h1{margin:0 0 12px;font-size:34px;line-height:1.2}h2{font-size:21px;margin-top:0}h3{font-size:17px}.decision{font-size:24px;font-weight:700;border-left:6px solid #486272;padding-left:14px}
.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0 24px}.metric{border:1px solid #dce3e5;border-radius:8px;padding:16px;background:#f8faf9}.metric dt{font-size:13px;font-weight:700;color:#354b47}.metric dd{margin:4px 0;font-size:34px;line-height:1.2;font-weight:750;overflow-wrap:anywhere}.metric p{font-size:12px;line-height:1.5;margin:8px 0 0;color:#53636b}.metric.pass{border-top:4px solid #27714c}.metric.fail{border-top:4px solid #b04b46}.metric.blocked{border-top:4px solid #9c6e21}.boundary{padding:14px 18px;background:#f1f5f4;border-left:4px solid #7a918b}
.meta{overflow-wrap:anywhere}small{display:block;color:#53636b;margin-top:8px}table{border-collapse:collapse;width:100%;table-layout:fixed}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #dce3e5;padding:12px;overflow-wrap:anywhere}thead{background:#edf2f3}th:nth-child(1){width:18%}th:nth-child(2){width:17%}th:nth-child(3){width:32%}ul{padding-left:18px;margin:6px 0 14px}.pass{color:#12613a}.fail{color:#a32424}.blocked,.potential,.review{color:#8a4900}.not{color:#52616a}summary{cursor:pointer}details{margin-top:12px}.scroll{overflow-x:auto}footer{color:#53636b}
.scope-links{display:flex;flex-wrap:wrap;gap:12px 24px}a{color:#205c79;text-underline-offset:3px}a:focus-visible{outline:3px solid #205c79;outline-offset:4px}.scope-panel{display:none}.scope-panel:target{display:block}.scope-table caption{text-align:left;font-weight:600;margin:0 0 12px}.scope-table th:nth-child(n){width:auto}.scope-panel{scroll-margin-top:20px}
@media(max-width:800px){main{padding:12px}header,section{padding:14px}table{min-width:760px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:450px){.metrics{grid-template-columns:1fr}}
@media print{body{background:white;font-size:11px}main{padding:0}header,section{border-radius:0;break-inside:auto;padding:12px;margin-bottom:12px}details{display:block}table{font-size:10px;min-width:0}th,td{padding:5px}.metrics{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.metric{break-inside:avoid;padding:10px}.metric dd{font-size:25px}.metric p{font-size:10px}thead{display:table-header-group}h2,h3{break-after:avoid}}
@media print{.scope-panel{display:block}.scope-links,.scope-panel>p{display:none}}
</style></head><body><main>''' + (
        f'<header id="report-summary"><p class="eyebrow">Environment readiness report</p><h1>FSCR Prevalidation</h1><p class="decision">{e(decision)}</p>'
        f'<p><strong>Assessment stage:</strong> {e(stage_label)}</p>'
        f'<div class="meta"><strong>{e(env["name"])}</strong> · {e(env["base_url"])} · Release: {e(env["release"])}'
        f'<p>Pillar: {e(scope["pillar"])} · Offering: {e(scope["offering"])}</p>'
        f'<nav class="scope-links" aria-label="Report sections"><a href="#findings">Findings and next actions</a><a href="#functional-area-table">Functional areas: '
        f'{len(scope["functional_areas"]) if scope["functional_areas"] else "Full offering scope"} — View table</a>'
        f'<a href="#setup-task-table">Planned setup tasks: '
        f'{len(scope["planned_setup_tasks"]) if scope["planned_setup_tasks"] else "All applicable tasks"} — View table</a></nav>'
        f'<small>Run {e(report["run_id"])} · Report generated: {e(report["generated_at"])}</small></div></header>'
    ) + ('<section id="continuation"><h2>Implementation continuation options</h2>'
        '<p>Review the findings and recommended solutions, then choose: fix and rerun; '
        'override selected results and continue; or override all results and continue. A passing assessment can continue normally without an override.</p>'
        '<p>Give your choice to the agent. No override is assumed or executed by this report. '
        'The agent records your explicit decision separately, preserving the original assessment. '
        'An override does not establish PASS or waive authentication, target identity, supported routes, '
        'payload validation or operation-specific approval requirements.</p></section>') + executive_summary(report, metrics) + findings_table(report, metrics) + scope_tables(scope) + "".join(sections) + (
        '<footer>Readiness reflects the recorded scope and evidence at assessment time. The renderer computes counts and '
        'checks the supplied decision; it does not contact Fusion, collect evidence or independently verify observations. '
        'Evidence references remain text. See JSON and run diagnostics for provenance and observation times.</footer></main></body></html>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True, help="JSON path relative to project root")
    parser.add_argument("--dry-run", action="store_true", help="Validate and render in memory without writing")
    args = parser.parse_args()
    try:
        repo = Path(__file__).resolve().parents[4]
        project_base = repo / "project"
        # Reject a redirected project directory before resolving the trusted root.
        if project_base.is_symlink() or project_base.resolve().parent != repo:
            raise ValueError("The repository project directory must be a real directory directly under the repository")
        projects = project_base.resolve()
        root = args.project_root.resolve()
        if root.parent != projects or root.name == "_template" or args.project_root.is_symlink():
            raise ValueError("project-root must be a real project directly under this repository's project/")
        if not (root / "state/project-state.json").is_file():
            raise ValueError("An initialized project state is required")
        if args.input.is_absolute() or ".." in args.input.parts:
            raise ValueError("input must be a relative path inside the assessment artifact directory")
        source = root / args.input
        target = source.with_suffix(".html")
        artifact_root = root / "artifacts/shared/validation/prevalidation"
        if source.suffix != ".json" or not source.resolve().is_relative_to(artifact_root.resolve()):
            raise ValueError("input must be assessment artifact JSON")
        # Reject symlink components, including a symlinked artifact root.
        for path in (source, target):
            if any(part.is_symlink() for part in (path, *path.parents) if part != projects.parent):
                raise ValueError("Symlink paths are not supported")
        if target.exists():
            raise ValueError("HTML already exists; use a fresh run directory")
        report = json.loads(source.read_text(encoding="utf-8"))
        content = render(report)
        if args.dry_run:
            print(f"Validated: {report['overall_decision']}; HTML not written")
        else:
            with target.open("x", encoding="utf-8") as output:
                output.write(content)
            print(target)
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Readiness report error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
