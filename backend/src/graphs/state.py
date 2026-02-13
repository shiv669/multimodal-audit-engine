import operator

from typing import Annotated, List, Dict, Optional, Any, TypedDict

#if audit result is failed to follow the compliance of the pdf return the following
class complianceIssue(TypedDict):
    category : str
    description : str
    severity : str
    timestamp : Optional[str]

class videoState(TypedDict):
    '''
    defines the dataschema of the video itself for langgraph 
    '''
    #input data
    video_url : str 
    video_id : str #id is just a unique identifier for video each times will update

    #ingestion and extraction data
    local_file_path : Optional[str] #we are storing the video locally on our device
    video_metadata : Dict[str,Any]
    video_transcript : Optional[str]
    ocr_text : List[str]

    #output data
    compliance_result : Annotated[List[complianceIssue], operator.add]

    #final result 
    audit_result : str #either pass or fail 
    audit_report : str

    #errors
    errors : Annotated[List[str], operator.add]



