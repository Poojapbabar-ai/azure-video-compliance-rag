"""
Main Execution Entry Point for the compliance QA Pipeline .

This file is the "control center" that starts and manages the entire
compliance audit workflow. Think of it as the master switch that:
1. set up the audit request
2. Runs the AI workflow
3. Displays the final compliance report
"""
import uuid  #Generated the Unique ID
import json #handle json Data formatting (converts the python dicts to readble text)
import logging  # Records what happens during the  execution (like a flight recorder)
from pprint import pprint #Pretty print data strutures ) (unused here but availble)

from dotenv import load_dotenv
load_dotenv(override=True)


from graph.workflow import app

logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s-%(name)s - %(levelname)s -%(message)s'
)

logger = logging.getLogger("brand-guardian-runner")



def run_cli_simulation():
    '''
    simulate the video compliance audit request.
    This function orchestrayes the entire audit process:
    - creates a unique session ID 
    - Prepare the video URL and metadata
    - Runs it through the AI workflow
    - Display the compliance results
    '''
    session_id = str(uuid.uuid4())
    logger.info(f"starting Audit Session: {session_id}")

    #define the inintial states
    #This dictionary contains all the inputs data for the workflow
    #Think of it as the "intake form" for the compliance audit
    initial_inputs = {
        #The  youtube Video to audit
        "video_url" : "https://youtu.be/dT7S75eYhcQ",
        #shortned video ID for easier tracking(forst 8 chars of session ID)
        #ex : "vid_ce6c43bb"
        "video_id" :f"vid{session_id[:8]}",

        #Empty list that will store compliance violations found
        #will be populated by the auditor node
        "compliance_issues":[],


        #Empty list for any errors during processing 
        #ex  : ["Download failed","Transcript unavilable"]
         "errors":[]
    }


    ###---Display  section : input summary -----------
    print("------------Initilaize workdlow------------------")
    print(f"Input Payload : {json.dumps(initial_inputs,indent=2)}")
    #-----------------3. Execute graph --------------
    try:
        final_state = app.invoke(initial_inputs)
        print("\n-------------------Workflow execution is complete-----------------------")


        print("\n Compliance AUdit Report == ")
        print(f"Video ID : {final_state.get('video_id')}")
        print(f"Status :{final_state.get('final_status')}")
        print("\n [VIOLATIONS DETECTED]")

        results = final_state.get('compliance_issues', [])
        if results:
            for issue in results:
                print(f"-[{issue.get('severity')}] [{issue.get('category')}]: [{issue.get('description')}]")

        elif final_state.get("final_status") == "PASS":
            print("No violations detected.")
        else:
            print("Audit did not complete successfully; see the final summary and errors.")
        print("\n[FINAL SUMMARY]")
        print(final_state.get('final_report'))


    except Exception as e:
        logger.error(f"Workflow Execution Failed : {str(e)}")
        raise e



##---------------- Program Entry point  -----

#this block only runs when we execute python main.py 
#it won't run if you import  this file as a module


if __name__ == "__main__":
    run_cli_simulation() # start the compliance audit simulation
