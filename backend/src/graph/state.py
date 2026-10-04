import operator
from typing import Annotated, Any, Dict, List, Optional, TypeDict, Union


#define schema for a single compliance issue
#Error  Report 
class ComplianceIssue(TypeDict):
    description: str #spefic description of violation
    severity: str #CRTICAL | WARNING 
    timestamp: Optional[str]
    category: str #eg: 


#define the global graph state 
#this defines the state that gets passed around in the agentic workflow

class VideoAuditState(TypeDict):
    '''
    Define the data schema for langgraph execution content
    Main Container : holds all the information about the audit 
    right from  the initial URL to the final report     
    '''

    # input parameters
    video_url: str
    video_id: str


    #ingestion and extraction data 
    local_file = Optional[str]
    video_metadata =    Dict[str, Any] # {"duration": 15,"resolution": "1080p"}
    transcript: Optional[str] #Fully Extracted speech to text 
    ocr_text : List[str]


    # analysis output
    #List of all the compliance issues found in the video
    compliance_issues: Annotated[List[ComplianceIssue], operator.add]


    #final deliverables 
    final_status : str #PASS | FAIL
    final_report : str #markdown format


    #system observability 
    #errors : API timeout , system level erros 
    errors: Annotated[List[str], operator.add] 