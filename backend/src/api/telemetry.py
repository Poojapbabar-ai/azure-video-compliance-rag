import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor


#create the  dedicated logger

logger = logging.getLogger("brand-guardian.-telemetry")



def setup_telemetry():
    '''
    Initialize Azure Monitor OpenTelemetry 
    Tracks : Http Request ,database queries ,error, performance metrices
    send this data to azure monitor

    it auto captures  every API request 

    No needed to manually log each endpoint
    '''


    #retrive connection string 
    connection_string = (
        os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        or os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")
    )

    #check if configured
    if not connection_string:
        logger.warning("No instrumentation key found .Telemtry is DISABLED")
        return
    try:
        configure_azure_monitor(
            connection_string =connection_string,
            logger_name = "brand-guardian-tracer"
        )
        logger.info("Azure monitor Tracking Enables and connected")

    except Exception as e:
        logger.error(f"Failed to initialize azure monirot: {e}")


'''
Why do we use telemetry ?

without :
API is slow : no idea which part
how many users today ? No visibilty 


with :

/audit endpoint averages 4.5 s (indexer take 3.8 s)
Error logs show : 12% of audit failsdue to Youtube download erros
Metrics shows : 450 API calls today , 89% success rate 
'''
