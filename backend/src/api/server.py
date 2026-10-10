import uuid
import logging
from fastapi import FastAPI , HTTPException

from pydantic import BaseModel, Field
from typing import List


from dotenv import load_dotenv
load_dotenv(override=True)
from api.telemetry import setup_telemetry

setup_telemetry()


from graph.workflow import app as compliance_graph


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("api-server")

#Create the FastAPI applcation 


app = FastAPI(
    title = "Brand Guardian AI API",
    description = "API for Auditing video content against the branc compliance rules",
    version = "1.0.0"
)


#define data models


class AuditRequest(BaseModel):

    '''
    define the excepted structure of incoming API Requests
    example valid requests:
    {"video_url":"https:youtu.be/abc123"}
    Invalid  :422 errors
    {"video_url":12345}
    
    '''
    video_url :str 


class ComplianceIssue(BaseModel):
    category :str
    severity:str 
    description : str

class AuditResponse(BaseModel):
    session_id : str
    video_id : str 
    status : str 
    final_report : str
    compliance_results: List[ComplianceIssue] = Field(default_factory=list)


#define endpoint 


@app.post("/audit",response_model =AuditResponse)


async def audit_video(request:AuditRequest):
    '''
    Main API ENDpoint that trigger the compliance audit workflow
    '''

    session_id = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"
    logger.info(f"Received the audit Request :{request.video_url} (Session : {session_id})")


    #graph inputs 

    initial_inputs = {
        "video_url" : request.video_url,
        "video_id" : video_id_short,
        "compliance_issues" :[],
        "errors" : []
    }

    try:
        final_state = compliance_graph.invoke(initial_inputs)
        return AuditResponse(
            session_id=session_id,
            video_id= final_state.get("video_id"),
            status = final_state.get("final_status","UNKNOWN"),
            final_report=final_state.get("final_report","No report generated"),
            compliance_results = final_state.get("compliance_issues",[])

        )
    except Exception as e:
        logger.error(f"Audit Failed: {str(e)}")
        raise HTTPException(
            status_code=500 ,
            detail= f"Workflow Execution Failed : {str(e)}"
        )


@app.get("/health")
def health_check():
    '''Endpoint to verify if the API is working.'''
    return {"status": "healthy", "service": "Brand Guardian AI"}