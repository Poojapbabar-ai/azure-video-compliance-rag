import json
import logging
import os
import re
from typing import Any, Dict

from langchain.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import AzureSearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from graph.state import VideoAuditState
from services.video_indexer import VideoIndexService

logger = logging.getLogger("brand-gurardian")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# NODE 1: Indexer

def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    '''
    Download the video, upload it to Azure Video Indexer, and extract insights.
    '''
    video_url = state.get("video_url")
    video_id_input = state.get("video_id", "vid_demo")

    logger.info(f"------------[Note:Indexer] Processing :{video_url}  ---------------")

    local_filename = "temp_audit_video.mp4"

    try:
        vi_service = VideoIndexService()

        # Download the video from YouTube
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url, output_path=local_filename)
        else:
            raise ValueError("Please provide a valid YouTube video URL for the test")

        azure_video_id = vi_service.upload_video_to_azure(local_path, video_id_input)
        logger.info(f"Video uploaded to Azure Video Indexer with ID: {azure_video_id}")

        if os.path.exists(local_path):
            os.remove(local_path)
            logger.info(f"Temporary file {local_path} removed.")

        raw_insights = vi_service.wait_for_processing(azure_video_id)
        clean_data = vi_service.extract_data(raw_insights)
        logger.info(f"[Node:Indexer] Video Insights Extracted Successfully for video_id: {azure_video_id}")

        return clean_data

    except Exception as e:
        logger.error(f"Video Indexer failed: {e}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL",
            "transcript": "",
            "ocr_text": [],
        }


# NODE 2: Compliance Auditor

def audio_content_node(state: VideoAuditState) -> Dict[str, Any]:
    '''
    Perform retrieval-augmented generation to audit the content.
    '''
    logger.info("-----[NODE:Auditor] querying Knowledge base & LLM")
    transcript = state.get("transcript", "")
    if not transcript or not transcript.strip():
        logger.warning("No transcript available. Skipping audit...")
        indexer_errors = state.get("errors", [])
        reason = f" Video processing error: {'; '.join(indexer_errors)}" if indexer_errors else ""
        return {
            "final_status": "FAIL",
            "final_report": f"Audit skipped because video processing failed (no transcript).{reason}",
        }

    # Initialize clients
    openai_base_url = f"{os.getenv('AZURE_OPENAI_ENDPOINT', '').rstrip('/')}/openai/v1"
    llm = ChatOpenAI(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        base_url=openai_base_url,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        temperature=0.0,
    )

    embeddings = OpenAIEmbeddings(
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        base_url=openai_base_url,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )

    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function=embeddings.embed_query,
    )

    # RAG
    ocr_text = state.get("ocr_text", [])
    query_text = f"{transcript} {' '.join(ocr_text)}"
    docs = vector_store.similarity_search(query_text, k=5)
    retrieved_rules = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant compliance rules found."

    system_prompt = f"""
            You are a senior brand compliance auditor.
            OFFICIAL REGULATORY RULES:
            {retrieved_rules}
            INSTRUCTIONS:
            1. Analyze the Transcript and OCR text below.
            2. Identify any violations of the rules.
            3. Return strictly JSON in the following format:
            {{
                "compliance_results": [
                    {{
                        "category": "Claim Validation",
                        "severity": "CRITICAL",
                        "description": "Explanation of the violation...."
                    }}
                ],
                "status": "FAIL",
                "final_report": "Summary findings...."
            }}

            If no violations are found, set "status" to "PASS" and "compliance_results" to [].
            """

    user_message = f"""
                  VIDEO_METADATA: {state.get('video_metadata', {})}
                  TRANSCRIPT: {transcript}
                  ONSCREEN TEXT (OCR): {ocr_text}
                  """

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])
        content = response.content

        if "```" in content:
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1)

        audit_data = json.loads(content.strip())
        return {
            "compliance_issues": audit_data.get("compliance_results", []),
            "final_status": audit_data.get("status", "FAIL"),
            "final_report": audit_data.get("final_report", "NO report generated"),
        }
    except Exception as e:
        logger.error(f"System Error in Auditor Node: {str(e)}")
        logger.error(f"Raw LLM Response: {response.content if 'response' in locals() else 'No response received'}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL",
        }
