# coding=utf-8
# See main file for licence
""" One plugin. """
import codecs
import os

from applications import plugin
import utils


class elixir(plugin):
    """
       elixir
    """
    # #######################
    # SOFTWARE INFORMATION
    # #######################
    # Fill the information about the plugin. Please do not change the following 
    # variable names. 
    # 1. software_author   - Author name of the software. Use commas to add more authors.
    # 2. software_version  - Software version number.
    # ########################
    software_author = [u'Otakar Smrž']
    software_version = u'v1.0'


    exposed_uri = "/elixir"

    # myservice apis
    api_myapi1 = "myapi"
    api_myapi1_param1 = "list"

    def version(self):
        """ Cesilko version """
        return { 'version': self.__class__.__dict__['software_version'], 'author': self.__class__.__dict__['software_author'] }

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
