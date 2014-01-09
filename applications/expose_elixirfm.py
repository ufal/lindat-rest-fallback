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

    # #######################
    # SOFTWARE EXECUTABLES
    # #######################
    elixir_exe = '/home/smrz/.cabal/bin/elixir'

    # #######################
    # BASE URI
    # #######################

    # http://host:port/elixirfm
    exposed_uri = "/elixirfm"

    # #######################
    # DEFINE API NAMES
    # #######################
    # 1. lookup
    #       "data" - <UTF-8 encoded string> 
    # 2. derive
    # 3. inflect
    # 4. resolve

    # URI :  http://host:port/elixirfm/lookup?data='your input'
    api_lookup = "lookup"
    api_lookup_p1 = "data"

    # #######################
    # DEFAULT APIs
    # #######################
    # 1. version
    #       uri:  http://host:port/elixirfm/version


    def version(self):
        """ ElixirFM version """
        return { 'version': self.__class__.__dict__['software_version'], 'author': self.__class__.__dict__['software_author'] }

    def execute(self, *args, **kwargs):
        """
            Execute the application.
        """

        # API: lookup        
        if elixirfm.api_lookup in args:	  
            input_data = kwargs[elixirfm.api_lookup_p1]
            cmd = "echo '%s' | %s lookup" % (input_data, elixirfm.elixir_exe)
            retcode, stdout, stderr = utils.run(cmd)
            self.log("ElixirFM ran: [%s]", cmd)
            if 0 == retcode:
                return {
                    "api": elixirfm.api_lookup,
                    "data": input_data,
                    "output": stdout
                }
            else:
                return self._failed( detail="retcode:%d, stdout=%s, stderr=%s, cmd=%s" % (retcode,  stdout, stderr, cmd) )
    
