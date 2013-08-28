# coding=utf-8
# See main file for licence
# pylint: disable=W0702,R0201

"""
  REST multithreaded server implementation based on cherrypy.
"""

import sys
import logging
_logger = logging.getLogger( "server" )

# cherrypy import
#
#noinspection PyBroadException
try:
    # set nicer output
    #
    import settings
    if settings.settings["response"]["json"]["indent"]:
        import __builtin__
        __builtin__.json_indent = settings.settings["response"]["json"]["indent"]
    import cherrypy
    MIN_MAJOR, MIN_MINOR = 3, 2
    major, minor, rel = cherrypy.__version__.split( "." )
    assert int( major ) >= MIN_MAJOR and int( minor ) >= MIN_MINOR, "cherrypy too old version"
    cherrypy.__version__ += " customised by Jozef Misutka v1.2"
except:
    logging.exception( u"Cannot import cherrypy server, reinstall it please." )
    sys.exit( u"Unable to import cherrypy." )


# handlers
#
from ._handlers import app as default_app
from ._handlers import mount_handlers
from ._tools import mount_tools


# Server
#

# noinspection PyDocstring
class rest_server( object ):
    """
        REST server based on cherrypy python framework (`http://www.cherrypy.org/`)
        implementation.
    """

    _logger = logging.getLogger( "server.rest_server" )

    def __init__(self, env_dict, handlers):
        """
            Receives app_inst or uses this_module._rest_server_app.
        """
        self._env = env_dict
        self.app = default_app()

        # add handlers to appropriate names
        mount_handlers( env_dict, self.app, handlers )

        assert "server" in env_dict, "Missing server in env settings."
        self.host = env_dict["server"]["host"]
        self.port = env_dict["server"]["port"]

        # additional parameters
        cherrypy.engine.autoreload.unsubscribe( )
        cherrypy.server.thread_pool_max = env_dict["server"].get( "thread_max", -1 )
        cherrypy.server.statistics = True

        # mount additional handlers
        mount_tools( env_dict )

    def start(self, block_bool=True, global_config_dict=None):
        """
            Start the service supporting REST API. If **block_bool** is True the method will
            return only if the server stops serving.
        """
        # global configs
        global_config = {
            'server.socket_host': self.host,
            'server.socket_port': self.port,
        }
        global_config.update( global_config_dict if not global_config_dict is None else { } )
        cherrypy.config.update( global_config )

        # application configs
        local_config = {
            '/': { 'request.dispatch': cherrypy.dispatch.MethodDispatcher( ), }
        }

        cherrypy.tree.mount( self.app, "/", config=local_config )

        # start and block if specified
        cherrypy.server.start( )
        _logger.info( "Rest server started at [%s:%s].", self.host, self.port )
        if block_bool:
            _logger.info( "Rest server blocking." )
            cherrypy.engine.block( )
