# coding=utf-8
# See main file for licence
""" One plugin. """
import codecs
import os

from applications import plugin
import utils


class elixirfm(plugin):
    """
       elixirfm
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


    # http://host:port/elixirfm
    exposed_uri = "/elixirfm"

    # elixirfm apis
    
    # API:  "myapi"
    # required params: "param1"
    # uri:  http://host:port/elixirfm/myapi1?param1='your input'
    api_myapi1 = "myapi1"
    api_myapi1_param1 = "param1"

    # API: "version"
    # uri:  http://host:port/elixirfm/version

    def version(self):
        """ ElixirFM version """
        return { 'version': self.__class__.__dict__['software_version'], 'author': self.__class__.__dict__['software_author'] }

    def execute(self, *args, **kwargs):
        """
            Execute the application.
        """
        if elixirfm.api_myapi1 in args:	  
            input_data = kwargs[elixirfm.api_myapi1_param1]
            return {
                        "input": input_data,
                        "result": "this is an example"
            }
