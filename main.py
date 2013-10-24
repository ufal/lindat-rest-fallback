# coding=utf-8
# This work is licensed!
# pylint: disable=W0702,R0201,C0111,W0613,R0914

"""
  Main entry point.
"""

import os
import sys
import logging
import getopt
import time

from settings import settings as settings_inst
import utils


# set the working directory to the top-level directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

# initialise logging
utils.initialize_logging( settings_inst["logger_config"] )
logger = logging.getLogger( 'common' )
logger.info(u"Setting the working directory to: " + os.path.dirname(os.path.abspath(sys.argv[0])))
settings_project_inst = None

try:
    #noinspection PyUnresolvedReferences
    from project_settings import settings as settings_project_inst
except ImportError:
    print ("Please, copy project_settings.py.example to project_settings.py.")
    sys.exit(1)


#=======================================
# start the server
#=======================================

def start_server(env):
    """ Set up plugins and start the server providing light REST API. """
    from applications import app_plugins_classes
    from server.rest import rest_server
    rest_server( env, app_plugins_classes ).start( )


#=======================================
# help
#=======================================

def help_msg(env):
    """ Returns help message. """
    logger.warning( u"""\n%s help. Supported commands:\n""", env["name"] )


def version_msg(env):
    """ Return the current application version. """
    return logger.warning( u"Version: %s", env["name"] )


#=======================================
# command line
#=======================================

def parse_command_line(env):
    """ Parses the command line arguments. """
    try:
        options = ["help",
                   "start",
                   "version",
                   ]
        input_options = sys.argv[1:]
        opts, _ = getopt.getopt( input_options, "", options )
    except getopt.GetoptError:
        help_msg( env )
        sys.exit( 1 )

    what_to_do = None
    for option, _1 in opts:
        if option == "--help":
            env["print_info"] = False
            return help_msg
        if option == "--version":
            return version_msg
        if option == "--start":
            what_to_do = start_server

    if what_to_do:
        return what_to_do
        # what to do but really?
    return start_server


#=======================================
# check system settings
#=======================================

#noinspection PyBroadException
def check_system(env):
    """
        Check few basic system settings.
    """
    versions_arr = [env["name"]]
    if 0 < env.get( "debug", 0 ):
        logger.warning( u"Debug mode [%s]", env["debug"] )
    logger.info( u"Version: %s", env["server"]["version"] )
    env["server"]["version"] = u"\n".join( versions_arr )
    # list all plugins
    from applications import app_plugins_classes
    logger.info( u"Available plugins [%d]:\n %s",
                 len(app_plugins_classes),
                 u"\n\t".join([ repr(x) for x in app_plugins_classes ] ) )


def load_project_settings(env):
    """ Update env with local settings. """
    from settings import smart_extend
    smart_extend( env, settings_project_inst )


#=======================================
# main
#=======================================

if __name__ == "__main__":
    lasted = time.time()
    logger.info( u"Starting at " + utils.host_info() )
    check_system(settings_inst)
    load_project_settings(settings_inst)

    # do what was specified or default
    try:
        what_to_do_callable = parse_command_line( settings_inst )
        what_to_do_callable( settings_inst )
    except Exception, e_inst:
        logger.critical( "An exception occurred, ouch:\n%s", e_inst )
        raise
    finally:
        lasted = time.time() - lasted
        logger.info( "Stopping after [%f] secs.", lasted )
