"""Render offline pre-report commentary for an accepted Data Loader request."""

from __future__ import annotations

import argparse


STATUS_QUESTION = "Would you like me to check the status of this Data Loader request now?"


def build_followup(request_id: str) -> str:
    """Return commentary to emit before Core's unchanged final report; never query status."""
    if not request_id.isdecimal() or int(request_id) <= 0:
        raise ValueError("accepted Data Loader Request ID must be a positive integer")
    return (
        f"Data Loader Request ID: {request_id}. Its status has not been checked.\n"
        f"{STATUS_QUESTION}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request-id", required=True, help="positive Request ID returned by core.data-loader")
    args = parser.parse_args(argv)
    try:
        print(build_followup(args.request_id))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
