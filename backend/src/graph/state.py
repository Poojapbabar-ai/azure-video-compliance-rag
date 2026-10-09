import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


# Define schema for a single compliance issue
class ComplianceIssue(TypedDict):
    description: str
    severity: str
    timestamp: Optional[str]
    category: str


# Define the global graph state
class VideoAuditState(TypedDict):
    '''
    Define the data schema for langgraph execution content.
    Main container: holds all the information about the audit,
    from the initial URL to the final report.
    '''

    # input parameters
    video_url: str
    video_id: str

    # ingestion and extraction data
    local_file: Optional[str]
    video_metadata: Dict[str, Any]
    transcript: Optional[str]
    ocr_text: List[str]

    # analysis output
    compliance_issues: Annotated[List[ComplianceIssue], operator.add]

    # final deliverables
    final_status: str
    final_report: str

    # system observability
    errors: Annotated[List[str], operator.add]