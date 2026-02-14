import json
import os 
import logging
import re
from typing import List, Dict, Any

from langchain_mistralai import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from backend.src.graphs.state import complianceIssue, videoState
from backend.src.services.video_indexer import videoIndexerService

logger = logging.getLogger("multimodal-audit-engine")
logging.basicConfig(level=logging.INFO)

#node 1 : indexer 

def videoIndexNode(state: videoState) -> Dict[str, Any]:
    '''
    DOWNLOAD the youtube video from the url 
    index it 
    get insights
    '''

    video_url = state.get("video_url")
    video_id_input = state.get("video_id", "video_demo")

    logger.info(f"[node:indexer] processing : {video_url}")

    local_filename = os.path.abspath("temp_audit_video.mp4")

    try:

        video_service = videoIndexerService()
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = video_service.download_youtube_video(video_url, output_path=local_filename)
        else:
            # Handle direct video URLs (non-YouTube)
            local_path = video_service.download_direct_video(video_url, output_path=local_filename)
        
        raw_insights = video_service.extract_video_data(local_path, video_id=video_id_input)
        logger.info(f"[node:indexer] extraction successful")

        if os.path.exists(local_path):
            os.remove(local_path)

        clean_data = video_service.extract_data(raw_insights)
        logger.info("[node: indexer] extraction successful")
        return clean_data
    
    except Exception as e:
        logger.error(f"video indexer failed: {e}")
        return{
            "errors" : [str(e)],
            "audit_result" : "fail",
            "video_transcript" : "",
            "ocr_text" : []
        }
    
#node 2 : compliance auditor

def audit_content_node(state: videoState) -> Dict[str, Any]:
    '''
    performs rag to audit the content
    '''

    logger.info("[node:audior] quering...")
    transcript = state.get("video_transcript", "")
    if not transcript:
        logger.warning("no transcript available for this video")
        return{
            "audit_result": "fail",
            "audit_report": "audit got skipped because no trasncript was available"
        }
    
# initialise clients

    llm = ChatMistralAI(model="mistral-small", api_key=os.getenv("MISTRAL_API_KEY"))

    embeddings = MistralAIEmbeddings(api_key=os.getenv("MISTRAL_API_KEY"))

    try:
        vector_store = FAISS.load_local("backend/data/faiss_index", embeddings, allow_dangerous_deserialization=True)
        logger.info("loader vector store from disk")
    except Exception as e:
        logger.warning(f"vector store not found, creating empty: {str(e)}")
        vector_store = FAISS.from_documents([], embeddings)

    # rag retrival
    ocr_text = state.get("ocr_text", [])
    query_text = f"{transcript} {''.join(ocr_text)}"
    docs = vector_store.similarity_search(query_text, k=3)
    retrived_rules = "\n\n".join([doc.page_content for doc in docs])

    system_prompt = f"""
        {{
            role: you are an senior brand compliance auditor you have multiple years of experience in the compliance industry as an auditor you have seen multiple reports and results so youre very used to it you are not rude or arrogant you are just true to data.,
            rules: 1.{retrived_rules},
            instrcutions: 1. analyse the transcript and ocr text given to you skim it end to end
            2. identify any kind of violations of the rules
            return type: strictly return json in the following format: {{
                {{
                    "compliance_result": [ 
                        {{
                            "category" : "claim validation",
                            "severity" : "critical",
                            "description" : "explanation of the violation"
                        }}
                        ],
                    "audit_result" : "fail",
                    "audit_report" : "summary of findings"
                }}
            }}
        }}

        if no violations are found , set "audit_result" to "pass" and "compliance_result" to []
            """

    user_message = f"""
            VIDEO_METADATA :{state.get('video_metadata',{})}
            TRANSCRIPT : {transcript}
            OCR: {ocr_text}
            """
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        content = response.content
        if "```" in content:
            content = re.search(r"```(?:json)?(.*)```", content, re.DOTALL).group(1)
        audit_data = json.loads(content.strip())
        return{
            "compliance_result" : audit_data.get("compliance_result", []),
            "audit_result" : audit_data.get("audit_result", "fail"),
            "audit_report" : audit_data.get("audit_report", "no report generated")
        }
    
    except Exception as e:
        logger.error(f"system error in auditor node : {str(e)}")
        logger.error(f"raw llm response : {response.content if 'response' in locals() else 'none'}")
        return {
            "errors" : [str(e)],
            "audit_result" : "fail"
        }