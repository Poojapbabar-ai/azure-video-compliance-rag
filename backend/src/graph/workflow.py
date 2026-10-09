'''
This module defines the DAG : Directed Acyclic Graph that Orchestrates the video compliance audit process

it connects the node using the StateGraph from LangGraph 


START -> index_video_node -> audio_content_node -> END

'''
from langgraph.graph import StateGraph,END
from graph.nodes import index_video_node, audio_content_node
from graph.state import VideoAuditState


def create_graph():
    '''
    Construct and complies the LangGraph workflow 
    Returns : 
        complied Graph :runnable graph object for execution 
    '''

    #initialize the  graph with state schema 
    workflow =  StateGraph(VideoAuditState)

    #add the node
    workflow.add_node("indexer",index_video_node)
    workflow.add_node("auditor",audio_content_node)


    #define the entry point 

    workflow.set_entry_point("indexer")
    #define the edge points :indexer  
    workflow.add_edge("indexer","auditor")
    #once the audit is done , workflow will end
    workflow.add_edge("auditor",END)

    #complie the graph
    app = workflow.compile()
    return app


#expose this runnable app
app = create_graph()


