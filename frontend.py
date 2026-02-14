import streamlit
import os
import json
import uuid
from datetime import datetime
import yt_dlp

from dotenv import load_dotenv
from backend.src.graphs.workflow import app

load_dotenv(override=True)

streamlit.set_page_config(
    page_title="Compliance Audit Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_rate_limit_status(user_id, max_per_day=5):
    rate_file = "backend/data/rate_limit.json"
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(rate_file):
        data = json.load(open(rate_file))
    else:
        data = {}

    if user_id not in data or data[user_id]["date"] != today:
        data[user_id] = {"date":today,"count":0}

    if data[user_id]["count"] >= max_per_day:
        return False, f"daily limit: {data[user_id]['count']}/{max_per_day} videos used"
    
    data[user_id]["count"]+=1
    json.dump(data,open(rate_file, "w"))
    return True, f"videos used today: {data[user_id]['count']}/{max_per_day}"


def get_video_duration(url):
    try:
        ydl_opts = {"quiet": True, "no_warnings":True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration_seconds = info.get("duration", 0)
            return duration_seconds/60
    except Exception as e:
        return None
    
streamlit.title("Video Compliance Auditor")

session_id = str(uuid.uuid4())[:8]
col1, col2 = streamlit.columns([2,1])

with col1:
    streamlit.markdown("### Upload Video for Audit")
    video_url = streamlit.text_input("Enter youtube url:", placeholder="https://youtu.be/...")

with col2:
    streamlit.markdown("### limits ")
    streamlit.info("max duration: 5 minutes\nmax per day: 5 videos")

if video_url:
    if streamlit.button("check video"):
        with streamlit.spinner("checking video duration..."):
            duration = get_video_duration(video_url)

            if duration is None:
                streamlit.error("could not fetch the video. try again")
            elif duration>5:
                streamlit.error(f"video duration is: {duration:.1f} can be max of 5 minutes!")
            else:
                allowed, message = get_rate_limit_status(session_id)
                streamlit.info(message)

                if allowed:
                    streamlit.success(f"video ok({duration:.1f}). ready for audit")
                    streamlit.session_state.video_checked = True
                else:
                    streamlit.error(message)

if streamlit.session_state.get("video_checked"):
    if streamlit.button("start audit"):
        streamlit.session_state.ready_to_audit = True

if streamlit.session_state.get("ready_to_audit"):
    streamlit.write("DEBUG: Audit started, processing...")
    with streamlit.spinner("Running compliance audit..."):
        initial_inputs = {
            "video_url": video_url,
            "video_id": f"vid_{session_id}",
            "local_file_path": None,
            "video_metadata": {},
            "video_transcript": "",
            "ocr_text": [],
            "compliance_result": [],
            "audit_result": "",
            "audit_report": "",
            "errors": []
        }
        
        final_state = app.invoke(initial_inputs)

        streamlit.success("Audit Complete!")
        
        col1, col2 = streamlit.columns([1, 1])
        
        with col1:
            streamlit.markdown("### Audit Result")
            result = final_state.get("audit_result", "unknown")
            if result == "pass":
                streamlit.success("PASS")
            else:
                streamlit.error("FAIL")
        
        with col2:
            streamlit.markdown("### Video ID")
            streamlit.info(final_state.get("video_id"))
        
        streamlit.markdown("### Violations Detected")
        violations = final_state.get("compliance_result", [])
        if violations:
            for violation in violations:
                streamlit.warning(f"[{violation.get('severity')}] {violation.get('category')}: {violation.get('description')}")
        else:
            streamlit.success("No violations found")
        
        streamlit.markdown("### Summary")
        streamlit.info(final_state.get("audit_report", "No summary available"))
        
        errors = final_state.get("errors", [])
        if errors:
            streamlit.markdown("### Errors")
            for error in errors:
                streamlit.error(error)