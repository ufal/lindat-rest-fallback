# coding=utf-8
# See main file for licence
""" Plugin dir. """

import os
import server
import cherrypy
import logging
_logger = logging.getLogger("applications")

# noinspection PyMissingConstructor,PyDocstring
class _plugin_meta(type):
    """
        Meta class which stores all instances of subclasses of plugin class.
    """

    def __init__(cls, name, bases, attrs):
        """ Ctor """
        type.__init__(cls, name, bases, attrs)
        if not hasattr(cls, '_plugins'):
            cls._plugins = []
        else:
            cls._plugins.append(cls)

    def plugins(cls):
        """ Return all implicitly registered plugins. """
        return cls._plugins


# noinspection PyDocstring,PyUnresolvedReferences,PyUnusedLocal
class plugin:
    """
        Super class for applications plugins.

        Extend this to get a proper plugin.
    """
    __metaclass__ = _plugin_meta

    exposed_uri = "/invalid"
    exposed = True

    # default handlers
    #

    @cherrypy.tools.json_out()
    def GET(self, *args, **kwargs):
        """
            HTTP GET request.

            Common API
                - version
        """
        if server.api_version in args:
            return self.version()
        return self.handle(*args, **kwargs)

    @cherrypy.tools.json_out()
    def POST(self, *args, **kwargs):
        """
            HTTP POST request.
        """
        return self.handle(*args, **kwargs)

    def handle(self, *args, **kwargs):
        """
            Delegate below.
        """
        return self.execute( *args, **kwargs )

    # should be overloaded
    #

    def version(self):
        """ Should be overloaded. """
        raise NotImplementedError( "Implement this in your application" )

    def execute(self, *args, **kwargs):
        """ Should be overloaded. """
        raise NotImplementedError( "Implement this in your application" )

    def log(self, msg, *args):
        """ Log msg """
        _logger.info( msg, *args ) 

    def posted_body(self):
        """ Return posted body. """
        try:
            cl = cherrypy.request.headers['Content-Length']
            return cherrypy.request.body.read(int(cl))
        except:
            pass
        return None

        

# automatic loading
#

def _import(name):
    """ Import local path. """
    mod = __import__(name)
    return mod


# explicitly register all plugins from this directory
# starting with _must_start_with
#
_dir_path = os.path.dirname(__file__)
_dir_name = os.path.basename(_dir_path)
_must_start_with = "expose_"
for f in os.listdir(_dir_path):
    if f.startswith(_must_start_with) and f.endswith(".py"):
        _import( os.path.basename(_dir_name) + "." + f.replace(".py", ""))


# list of registered plugins
#

app_plugins_classes = [cls for cls in plugin.plugins()]
