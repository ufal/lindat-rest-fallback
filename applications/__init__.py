# coding=utf-8
# See main file for licence
""" Plugin dir. """

import os
import server
import cherrypy
import json
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

    def GET(self, *args, **kwargs):
        """
            HTTP GET request.

            Common API
                - version

            Note:
                Mime can be set when returning a tuple ["mime type", ret obj]
        """
        ret = None
        if server.api_version in args:
            ret = self.version()
        else:
            ret = self.handle(*args, **kwargs)
        return self.set_mime(ret)

    def POST(self, *args, **kwargs):
        """
            HTTP POST request.
        """
        return self.set_mime(self.handle(*args, **kwargs))

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
        """ Return raw posted body. """
        try:
            cl = cherrypy.request.headers['Content-Length']
            return cherrypy.request.body.read(int(cl))
        except:
            pass
        return None

    @staticmethod
    def set_mime(obj_mime):
        if not isinstance(obj_mime, (list, tuple)):
            return plugin.jsonify(obj_mime)
        cherrypy.response.headers['Content-Type'] = obj_mime[0]
        return obj_mime[1]

    @staticmethod
    def jsonify(d):
        cherrypy.serving.response.headers['Content-Type'] = "application/json"
        return json.dumps(d, indent=2)
        

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
