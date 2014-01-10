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
    software_version = u'v1.2.1.2'

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

    # Shell cmd : echo "something" | elixir lookup 
    # URI :  http://host:port/elixirfm/lookup?data='something'
    api_lookup = "lookup"
    api_lookup_p1 = "data"

    # Shell cmd : echo "fhm" | elixir resolve tim | cut -f 9 | sort | uniq | elixir derive 'A--P------'
    # URI :  http://host:port/elixirfm/derive?data='fhm'&q1='tim'&q2='A--P------'
    api_derive = "derive"
    api_derive_p1 = "data"    # input data for "lookup" 
    api_derive_p2 = "q1"      # query for "resolve" 
    api_derive_p3 = "q2"      # query for "derive" 

    # Shell cmd : echo "something" | elixir lookup | cut -f 3 | elixir inflect '-------P1[ID]' 
    # URI :  http://host:port/elixirfm/inflect?data='something'&q1='-------P1[ID]'
    api_inflect = "inflect"
    api_inflect_p1 = "data"   # input data for "lookup" 
    api_inflect_p2 = "q1"     # query for "inflect"
    
    # Shell cmd : echo "fhm" | elixir resolve tim 
    # URI :  http://host:port/elixirfm/resolve?data='fhm'&q1='tim'
    api_resolve = "resolve"
    api_resolve_p1 = "data"   # input data for "lookup"
    api_resolve_p2 = "q1"     # query for "resolve"


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
        # API : derive
        if elixirfm.api_derive in args:
            input_data = kwargs[elixirfm.api_derive_p1]
            q1 = kwargs[elixirfm.api_derive_p2]
            q2 = kwargs[elixirfm.api_derive_p3]
            cmd = "echo '%s' | %s resolve %s | cut -f 9 | sort | uniq | %s derive '%s'" % (input_data, elixirfm.elixir_exe, q1, elixirfm.elixir_exe, q2)
            retcode, stdout, stderr = utils.run(cmd)
            self.log("ElixirFM ran: [%s]", cmd)
            if 0 == retcode:
                return {
                    "api": elixirfm.api_derive,
                    "data": input_data,
                    "q1": q1,
                    "q2": q2,
                    "output": stdout
                }
            else:
                return self._failed( detail="retcode:%d, stdout=%s, stderr=%s, cmd=%s" % (retcode,  stdout, stderr, cmd) )
