"""Oracle Fusion Run Book API operations."""

from typing import Any, Callable, Optional, Sequence
from urllib.parse import quote, urlsplit
from urllib.request import urlopen

from runbook_http import (
    ApiError,
    IndeterminateWriteError,
    JsonTransport,
    SuccessResponseError,
    TIMEOUT_SECONDS,
)
from runbook_values import MAX_INT64, positive_int64


REST_RESOURCES_PATH = "/hcmRestApi/resources/11.13.18.05"
RUNBOOK_SEARCH_PATH = (
    "/hcmRestApi/redwood/11.13.18.05/workerJourneySearches"
)
RUNBOOK_STATUS_TERMS = frozenset(("Completed", "Open", "Overdue"))


def normalized_runbook_statuses(statuses: object) -> list[str]:
    """Return exact supported status terms or the all-status default."""

    if isinstance(statuses, (str, bytes)) or not isinstance(statuses, Sequence):
        return []
    values = list(statuses)
    if any(
        not isinstance(value, str) or value not in RUNBOOK_STATUS_TERMS
        for value in values
    ):
        return []
    return values
ASSIGNED_RUNBOOKS_PATH = (
    f"{REST_RESOURCES_PATH}/journeySubjects/RBK/child/assignedJourneys"
)
CREATE_RUNBOOK_PATH = (
    f"{ASSIGNED_RUNBOOKS_PATH}/action/assignRunbook"
)
ADD_TASK_PATH = f"{ASSIGNED_RUNBOOKS_PATH}/"
DATA_LOADER_RUNBOOK_SUMMARY_PATH = (
    f"{REST_RESOURCES_PATH}/dataLoaderDataSets/action/generateRunbookSummary"
)
TASK_COMMENT_OBJECT_TYPE = "ORA_CHK_ALLOC_TASK"
TASK_COMMENT_CONTEXT_TYPE = "TASK_COMMENTS"
TASK_COMMENT_NOTES_PATH = (
    f"{REST_RESOURCES_PATH}/objectNotesV2/{TASK_COMMENT_OBJECT_TYPE}/child/notes"
)
TASK_COMMENT_FIELDS = (
    "AuthorId,TagList,AuthorKnownAs,AuthorName,AuthorNumber,ContextId,ContextId2,"
    "ContextNameVo,ContextNameVo2,ContextType,ContextType2,ContextTypeMeaning,"
    "CreatedBy,CreationDate,LastUpdateDate,LastUpdatedBy,NoteId,NoteText,"
    "NoteTypeCode,NoteTypeMeaning,NoteVisibilityCode,NoteVisibilityMeaning,ObjectId,"
    "ObjectType,AllowUpdate,AllowDelete,attachments"
)
RUNBOOK_LIST_FIELDS = (
    "DisplayName",
    "PersonNumber",
    "AssignmentName",
    "WorkerJourneyId",
    "JourneyDisplayName",
    "BackgroundThumbnailURL",
    "Status",
    "StatusCategoryMeaning",
    "AssignedDate",
    "QualificationName",
    "QualificationId",
    "SupplierName",
    "OrganizationUnitName",
    "SupplierId",
    "OrganizationUnitId",
    "Category",
    "Comments",
    "SubCategory",
    "CategoryMeaning",
    "taskCounts",
)
DEFAULT_PAGINATION_RECORD_LIMIT = 500
DEFAULT_TOTAL_RECORD_FETCH_LIMIT = 2500
DEFAULT_PAGINATION_LIMIT = 50

TASK_LIST_FIELDS = (
    "ParentWorkerJourneyId,WorkerJourneyTaskId,Description,Name,RequiredFlag,"
    "Status,StatusCategory,TargetEndDate,TargetStartDate,ExpiryRelativeTo,"
    "TargetDuration,TargetDurationUOM,CompletionDate,Type,"
    "TypeMeaning,SubType,ActionReassign,StageName,StageSequence,Sequence,"
    "SubSequence,TaskPercentageComplete,ActionEditDueDate,ActionRemove,"
    "ActionReopen,ActionEdit,AllowPrecedingTaskFlag,PerformerType,"
    "PerformerTypeMeaning,PerformerName,PerformerUsername"
)
TASK_DETAIL_FIELDS = (
    "WorkerJourneyTaskId,Name,Type,SubType,RequiredFlag,StatusCategory,Status,"
    "Sequence,TaskPercentageComplete,"
    "TargetStartDate,TargetEndDate,CompletionDate,"
    "AccessNotes,AccessGuidedJourney,AccessComments,"
    "AccessAttachments,AccessActivity,AllowAttachmentFlag,NoteTitle,Notes,"
    "AllowNoteTitleFlag,"
    "ActionURL,QuestionnaireId,ContentProviderCode,ActionComplete,"
    "ActionReject,ActionAddToCalendar,ActionSave,AccessContact,"
    "OwnerTypeMeaning,OwnerPersonId,OwnerName,OwnerWorkEmailAddress,"
    "DocumentTypeId,ActionCompleteLabel,ActionRejectLabel,"
    "ActionAddToCalendarLabel,ActionSaveLabel,ActivityAction1Label,"
    "ActivityAction2Label,ActivityAction3Label,ActivityAction4Label,"
    "ActivityAction5Label,OpenReportInSamePageFlag,OpenInSamePageFlag,"
    "AllowNotesContentFlag,GuidedJourneyCode,GuidedJourneyTaskCodes,"
    "AnalysisPath,AnalyticsSubType,DynamicNotesType,DynamicNotesSource,"
    "AgentCodeForSave,AgentCodeForCompletion,AdvisorCode,Description,"
    "ApplicationTaskName;attachments:AttachedDocumentId"
)
ATTACHMENT_FIELDS = (
    "DatatypeCode,DocumentPreviewURL,FileName,Title,FileUrl,Url"
)
DOCUMENT_FIELDS = "AttachedDocumentId,DatatypeCode,DocumentPreviewURL,Url,FileName,Title"
JOURNEY_FIELDS = (
    "WorkerJourneyId,JourneyDisplayName,JourneyTitle,BackgroundImageURL,"
    "CategoryMeaning,Category,Description,Comments,MessageTitle,"
    "MessageSubTitle,SubjectKey,AssignmentId,AllocationDate,PersonId,"
    "DisplayName,SubCategory,ChecklistFeature,ActionAddTask,"
    "ActionAddTaskFromLibrary"
)


def _path_segment(value: Any) -> str:
    return quote(str(value), safe="")


def _server_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Run Book REST base URL must identify an HTTP(S) server.")
    host = f"[{parsed.hostname}]" if ":" in parsed.hostname else parsed.hostname
    port = f":{parsed.port}" if parsed.port is not None else ""
    return f"{parsed.scheme}://{host}{port}"


class RunbookClient:
    """Call the Oracle Fusion journey resources used by the run-book workflow."""

    def __init__(
        self,
        *,
        base_url: str,
        authorization: str,
        refresh_authorization: Optional[Callable[[], str]] = None,
        timeout: int = TIMEOUT_SECONDS,
        opener: Callable[..., Any] = urlopen,
        total_record_fetch_limit: int = DEFAULT_TOTAL_RECORD_FETCH_LIMIT,
        pagination_record_limit: int = DEFAULT_PAGINATION_RECORD_LIMIT,
        pagination_limit: int = DEFAULT_PAGINATION_LIMIT,
    ) -> None:
        for name, value in (("total_record_fetch_limit", total_record_fetch_limit),
                            ("pagination_record_limit", pagination_record_limit),
                            ("pagination_limit", pagination_limit)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer.")
        self.total_record_fetch_limit = total_record_fetch_limit
        self.pagination_record_limit = pagination_record_limit
        self.pagination_limit = pagination_limit
        self._transport = JsonTransport(
            base_url=base_url,
            authorization=authorization,
            refresh_authorization=refresh_authorization,
            timeout=timeout,
            opener=opener,
        )
        self.server_url = _server_url(base_url)

    @staticmethod
    def _require_object(value: Any, resource: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ApiError(f"Expected {resource} to return a JSON object.")
        return value

    @staticmethod
    def _require_items(value: Any, resource: str) -> list[dict[str, Any]]:
        response = RunbookClient._require_object(value, resource)
        items = response.get("items")
        if not isinstance(items, list):
            raise ApiError(f"Expected {resource} to return an items array.")
        if not all(isinstance(item, dict) for item in items):
            raise ApiError(f"Expected every {resource} item to be a JSON object.")
        return items

    def _collect_paginated_items(
        self, *, resource: str,
        fetch_page: Callable[[int, int], Any], offset: int = 0,
    ) -> dict[str, Any]:
        """Bound page fetches; authentication retries belong to the transport."""
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be a nonnegative integer.")
        if offset >= self.total_record_fetch_limit:
            raise ApiError("The total_record_fetch_limit has been reached; no more records may be fetched with the current limit.")
        items = []
        start_offset = offset
        settings = {"total_record_fetch_limit": self.total_record_fetch_limit,
                    "pagination_record_limit": self.pagination_record_limit,
                    "pagination_limit": self.pagination_limit}
        for page in range(self.pagination_limit):
            limit = min(self.pagination_record_limit,
                        self.total_record_fetch_limit - offset)
            response = self._require_object(fetch_page(offset, limit), resource)
            page_items = self._require_items(response, resource)
            has_more = response.get("hasMore")
            if not isinstance(has_more, bool):
                raise ApiError(f"Expected {resource} hasMore to be a boolean.")
            if len(page_items) > limit:
                raise ApiError(f"Oracle Fusion exceeded the requested record limit for {resource}.")
            if has_more and not page_items:
                raise ApiError(f"Oracle Fusion reported another {resource} page but returned no items.")
            items.extend(page_items)
            offset += len(page_items)
            if not has_more:
                return {"items": items, "count": len(items), "hasMore": False,
                        "complete": True, "offset": start_offset, "nextOffset": None,
                        "paginationSettings": settings, "fetchedSoFar": offset,
                        "remainingRecordAllowance": self.total_record_fetch_limit - offset,
                        "continuationAllowed": False}
            reasons = []
            if offset >= self.total_record_fetch_limit:
                reasons.append("total_record_fetch_limit")
            if page + 1 >= self.pagination_limit:
                reasons.append("pagination_limit")
            if reasons:
                return {"items": items, "count": len(items), "hasMore": True,
                        "complete": False, "offset": start_offset,
                        "nextOffset": offset if offset < self.total_record_fetch_limit else None,
                        "fetchedSoFar": offset,
                        "remainingRecordAllowance": self.total_record_fetch_limit - offset,
                        "continuationAllowed": offset < self.total_record_fetch_limit,
                        "paginationSettings": settings,
                        "stopReasons": reasons}
        raise AssertionError("Pagination must return within its configured limits")


    @staticmethod
    def task_path(parent_worker_journey_id: str, worker_journey_task_id: str) -> str:
        return (
            f"{ASSIGNED_RUNBOOKS_PATH}/"
            f"{_path_segment(parent_worker_journey_id)}/child/tasks/"
            f"{_path_segment(worker_journey_task_id)}"
        )

    def list_tasks(
        self,
        journey_id: str,
        *, offset: int = 0,
    ) -> dict[str, Any]:
        path = (
            f"{ASSIGNED_RUNBOOKS_PATH}/"
            f"{_path_segment(journey_id)}/child/allStepTasks"
        )

        return self._collect_paginated_items(
            resource='allStepTasks', offset=offset,
            fetch_page=lambda offset, limit: self._transport.request_json(
                    "GET",
                    path,
                    params={
                        "orderBy": "Sequence",
                        "fields": TASK_LIST_FIELDS,
                        "offset": offset,
                        "limit": limit,
                    },
                ),
        )

    def list_runbooks(
        self,
        offset: int = 0,
        query: Optional[str] = None,
        statuses: object = (),
    ) -> dict[str, Any]:
        """Return one Oracle Fusion search page of self Run Books."""

        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be a nonnegative integer.")
        if query is not None and (
            not isinstance(query, str) or not query.strip()
        ):
            raise ValueError("query must be non-empty text when supplied.")
        status_terms = normalized_runbook_statuses(statuses)
        payload = {
            "finder": {
                "name": "findSelfJourneys",
                "parameters": [{"name": "SubjectType", "value": "RBK"}],
            },
        "filters": [
            {"name": "StatusCategoryMeaning", "terms": status_terms}
        ],
            "displayFields": list(RUNBOOK_LIST_FIELDS),
            "offset": offset,
        }
        if query is not None:
            payload["query"] = query
            payload["searchFields"] = ["JourneyDisplayName"]
        response = self._transport.request_json(
            "POST",
            RUNBOOK_SEARCH_PATH,
            payload=payload,
            read_semantic_post=True,
        )
        result = self._require_object(response, "workerJourneySearches")
        self._require_items(result, "workerJourneySearches")
        return result

    def get_journey(self, journey_id: str) -> dict[str, Any]:
        response = self._transport.request_json(
            "GET",
            f"{ASSIGNED_RUNBOOKS_PATH}/"
            f"{_path_segment(journey_id)}",
            params={"fields": JOURNEY_FIELDS, "onlyData": "true"},
        )
        return self._require_object(response, "assignedJourneys")

    def get_task(
        self,
        parent_worker_journey_id: str,
        worker_journey_task_id: str,
    ) -> dict[str, Any]:
        response = self._transport.request_json(
            "GET",
            self.task_path(parent_worker_journey_id, worker_journey_task_id),
            params={"fields": TASK_DETAIL_FIELDS},
        )
        return self._require_object(response, "tasks")

    def add_task_comment(self, worker_journey_task_id: Any, note_text: str) -> Any:
        """Create one visible task comment without retrying the POST."""

        if not isinstance(note_text, str):
            raise ValueError("Comment text must be text.")
        task_id = str(positive_int64(worker_journey_task_id, "WorkerJourneyTaskId"))
        return self._transport.request_json(
            "POST",
            TASK_COMMENT_NOTES_PATH,
            payload={
                "ObjectId": task_id,
                "ObjectType": TASK_COMMENT_OBJECT_TYPE,
                "NoteVisibilityCode": "ALL",
                "ContextType": TASK_COMMENT_CONTEXT_TYPE,
                "NoteText": note_text,
            },
            allow_unusable_success_body=True,
        )

    def get_task_comments(
        self,
        worker_journey_task_id: Any,
        *, offset: int = 0,
    ) -> dict[str, Any]:
        """Return every Object Notes task comment in Fusion's descending order."""

        task_id = str(positive_int64(worker_journey_task_id, "WorkerJourneyTaskId"))
        query = f"ObjectId={task_id} and ContextType='{TASK_COMMENT_CONTEXT_TYPE}'"

        return self._collect_paginated_items(
            resource='task comments', offset=offset,
            fetch_page=lambda offset, limit: self._transport.request_json(
                    "GET",
                    TASK_COMMENT_NOTES_PATH,
                    params={
                        "expand": "NoteText,attachments",
                        "fields": TASK_COMMENT_FIELDS,
                        "onlyData": "true",
                        "orderBy": "LastUpdateDate:desc",
                        "q": query,
                        "offset": offset,
                        "limit": limit,
                    },
                ),
        )

    def get_documents(
        self,
        parent_worker_journey_id: str,
        worker_journey_task_id: str,
        *, offset: int = 0,
    ) -> dict[str, Any]:
        path = (
            f"{self.task_path(parent_worker_journey_id, worker_journey_task_id)}"
            "/child/documents"
        )

        return self._collect_paginated_items(
            resource='documents', offset=offset,
            fetch_page=lambda offset, limit: self._transport.request_json(
                    "GET",
                    path,
                    params={
                        "fields": DOCUMENT_FIELDS,
                        "onlyData": "true",
                        "offset": offset,
                        "limit": limit,
                    },
                ),
        )

    def get_attachments(
        self,
        parent_worker_journey_id: str,
        worker_journey_task_id: str,
        *, offset: int = 0,
    ) -> dict[str, Any]:
        path = (
            f"{self.task_path(parent_worker_journey_id, worker_journey_task_id)}"
            "/child/attachments"
        )

        return self._collect_paginated_items(
            resource='attachments', offset=offset,
            fetch_page=lambda offset, limit: self._transport.request_json(
                    "GET",
                    path,
                    params={
                        "fields": ATTACHMENT_FIELDS,
                        "onlyData": "true",
                        "offset": offset,
                        "limit": limit,
                    },
                ),
        )

    def add_task_attachment(
        self,
        parent_worker_journey_id: str,
        worker_journey_task_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Attach one file to an assigned task without retrying the POST."""

        response = self._transport.request_json(
            "POST",
            f"{self.task_path(parent_worker_journey_id, worker_journey_task_id)}"
            "/child/attachments",
            payload=payload,
        )
        if not isinstance(response, dict):
            raise SuccessResponseError(
                "Expected the task attachment POST to return a JSON object."
            )
        try:
            positive_int64(
                response.get("AttachedDocumentId"),
                "AttachedDocumentId",
            )
        except ValueError as error:
            raise SuccessResponseError(
                "Oracle Fusion accepted the task attachment POST but did not "
                "return AttachedDocumentId."
            ) from error
        return response

    def get_runbook_summary(
        self,
        run_id: Any,
        fsm_task_code: Any,
    ) -> dict[str, Any]:
        if not isinstance(fsm_task_code, str) or not fsm_task_code.strip():
            raise ValueError("fsm_task_code must be non-empty text.")
        payload = {
            "runId": positive_int64(run_id, "run_id"),
            "fsmTaskCode": fsm_task_code,
        }
        response = self._transport.request_json(
            "POST",
            DATA_LOADER_RUNBOOK_SUMMARY_PATH,
            payload=payload,
            payload_content_type="application/vnd.oracle.action+json",
            read_semantic_post=True,
        )
        return self._require_object(response, "generateRunbookSummary")

    def update_task(
        self,
        parent_worker_journey_id: str,
        worker_journey_task_id: str,
        payload: dict[str, Any],
    ) -> Any:
        return self._require_object(
            self._transport.request_json(
                "PATCH",
                self.task_path(parent_worker_journey_id, worker_journey_task_id),
                payload=payload,
            ),
            "task update",
        )

    def force_complete_runbook(self, journey_id: Any) -> dict[str, Any]:
        """Force-complete one assigned Run Book without retrying the POST."""

        validated_id = positive_int64(journey_id, "WorkerJourneyId")
        path = (
            f"{ASSIGNED_RUNBOOKS_PATH}/"
            f"{_path_segment(validated_id)}/action/forceComplete"
        )
        return self._require_object(
            self._transport.request_json(
                "POST",
                path,
                payload={},
                payload_content_type="application/vnd.oracle.action+json",
            ),
            "forceComplete",
        )

    def add_task(self, payload: dict[str, Any]) -> Any:
        """Add one task to an assigned run book without retrying the POST."""

        return self._transport.request_json(
            "POST",
            ADD_TASK_PATH,
            payload=payload,
            additional_headers={"Upsert-Mode": "true"},
        )

    def create_runbook(self, payload: dict[str, Any]) -> dict[str, int | str]:
        """Create one assigned run book without retrying the POST."""

        response = self._transport.request_json(
            "POST",
            CREATE_RUNBOOK_PATH,
            payload=payload,
            payload_content_type="application/vnd.oracle.action+json",
        )
        if not isinstance(response, dict):
            raise SuccessResponseError(
                "Expected assignRunbook to return a JSON object containing result."
            )
        try:
            worker_journey_id = positive_int64(
                response.get("result"),
                "assignRunbook result",
            )
        except ValueError as error:
            raise SuccessResponseError(str(error)) from error
        return {
            "WorkerJourneyId": worker_journey_id,
            "ServerUrl": self.server_url,
        }

    def merge_runbook(self, journey_id: str, payload: dict[str, Any]) -> None:
        """Merge planned task details into one assigned run book without retrying."""

        validated_id = positive_int64(journey_id, "WorkerJourneyId")
        path = (
            f"{ASSIGNED_RUNBOOKS_PATH}/"
            f"{_path_segment(validated_id)}/action/mergeJourney"
        )
        self._transport.request_json(
            "POST",
            path,
            payload=payload,
            payload_content_type="application/vnd.oracle.action+json",
            allow_unusable_success_body=True,
        )
