"""Domain contract and fail-closed interpretation for the Item index GET.

Transport and authentication belong to core.fusion-api.rest-api-client.
This module performs no network requests and prepares no import artifacts.
"""

UNKNOWN_INDEX = "FND_ERROR_SEARCH_SERVICE_UNKNOWN_INDEXES"
ENDPOINT = "/fscmRestApi/applcoreApi/search/v1/fa-fscm-item/_search"


def readiness_request() -> dict:
    """Check the index without a request body, arbitrary item ID, or item rows."""
    return {"method": "GET", "endpoint": ENDPOINT, "query": {"size": "0"}}


def _has_unknown_index(response: object) -> bool:
    if isinstance(response, dict):
        return response.get("errorCode") == UNKNOWN_INDEX or any(_has_unknown_index(value) for value in response.values())
    if isinstance(response, list):
        return any(_has_unknown_index(value) for value in response)
    return False


def classify_readiness(http_status: int | None, response: object) -> str:
    """Return only outcomes declared by REF_ORG_ITEMS.CHECK_ITEM_INDEX."""
    if http_status == 200:
        if isinstance(response, dict) and isinstance(response.get("hits"), dict):
            hits = response["hits"].get("hits")
            shards = response.get("_shards")
            if (isinstance(hits, list) and not hits
                    and not response.get("errorCode") and not response.get("error")
                    and response.get("timed_out") is False
                    and isinstance(shards, dict)
                    and type(shards.get("failed")) is int
                    and shards["failed"] == 0):
                return "available"
        return "failure"
    if http_status == 404 and _has_unknown_index(response):
        return "index_remediation_required"
    return "failure"
