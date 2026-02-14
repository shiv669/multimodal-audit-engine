'''
main file to run our multimode audit engine
'''

import logging
import uuid 
import json 
from pprint import pprint

from dotenv import load_dotenv

load_dotenv(override=True)

from backend.src.graphs.workflow import app

logging.basicConfig(
    level = logging.INFO,
    format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("multimodal-audit-engine")

def run_cli_simulation():
    '''
    simulates the audit compliance request
    '''

    session_id = str(uuid.uuid4())
    logger.info(f"starting the audit report for: {session_id}")

    initial_inputs = {
        "video_url" : "https://youtu.be/dT7S75eYhcQ",
        "video_id" : f"vid_{session_id[:8]}",
        "local_file_path" : None,
        "video_metadata" : {},
        "video_transcript" : "",
        "ocr_text" : [],
        "compliance_result" : [],
        "audit_result" : "",
        "audit_report" : "",
        "errors" : []
    }

    print("initialsing the workflow")
    print(f"input payload : {json.dumps(initial_inputs, indent=2)}")

    try:
        final_state = app.invoke(initial_inputs)
        print("workflow execution is completed")

        print("compliance audit report")
        print(f"video id: {final_state.get('video_id')}")
        print(f"final status: {final_state.get('audit_result')}")

        print("violations detected")
        result = final_state.get('compliance_result', [])

        if result:
            for issue in result:
                print(f"- [{issue.get('severity')}] {issue.get('category')}: {issue.get('description')}")
        else:
            print("no violations found")

        print("final summary")
        print(final_state.get('audit_report'))

    except Exception as e:
        logger.error(f"workflow execution failed {str(e)}")
        raise e
    
if __name__ == "__main__":
    run_cli_simulation()