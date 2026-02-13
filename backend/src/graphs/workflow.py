'''
here we are going to create an DAG: direct acyclic graph 
it will connect the nodes from stategraph using langgraph 
'''

from langgraph.graph import StateGraph, END
from backend.src.graphs.state import videoState

from backend.src.graphs.nodes import (
    videoIndexNode,
    audit_content_node
)

def create_graph():
    '''
    this function complies and constructs the langgraph and returns an complied graph for execution
    '''

    workflow = StateGraph(videoState)
    workflow.add_node("indexer", videoIndexNode)
    workflow.add_node("auditor", audit_content_node)

    workflow.set_entry_point("indexer")
    workflow.add_edge("indexer", "auditor")
    workflow.add_edge("auditor",END)

    app = workflow.compile()
    return app

app = create_graph()

