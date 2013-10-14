# coding=utf-8
# See main file for licence
""" One plugin. """
import codecs
import os

from applications import plugin
import utils


class myservice(plugin):
    """
       myservice
    """
    exposed_uri = "/myservice"

    # myservice apis
    api_myapi1 = "myapi"
    api_myapi1_param1 = "list"

    def version(self):
        """ myservice version """
        # TODO should be retrieved from cesilko itself
        return { "version": "myservice version 1" }

    def execute(self, *args, **kwargs):
        """
            Execute the application.
        """
        if myservice.api_myapi1 in args:	  
	  input_data = kwargs[myservice.api_myapi1_param1]
	  return {
                        "input": input_data,
                        "result": "this is an example"
	  }
