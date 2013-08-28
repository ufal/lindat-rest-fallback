# coding=utf-8
# See main file for licence
# pylint: disable=W0702,R0201,C0111,W0613,W0703

"""
  Cherrypy app and handlers.
  Handlers parse the input parameters, validates them, process errors.
  The communication between the REST server and the application itself is using
  `processing` module which exposes API for all required services.
"""

import logging
_logger = logging.getLogger("server")

import cherrypy
from ._tools import add_cross_domain_access_headers_if_set, handle_error


# Default handler
#

def error_page(err_msg):
    """
    Handles soft errors from outside e.g., invalid parameters.
    Returns object which can be json-ed.
  """
    add_cross_domain_access_headers_if_set()
    _logger.critical(u"Soft error occurred [%s]", err_msg)
    cherrypy.response.status = 500
    return {
        "error": "Ouch, an error occurred on your side.",
        "details": err_msg
    }


#noinspection PyDocstring
class _default_handler(object):
    """
        Handles invalid paths.
    """
    _logger = logging.getLogger("server.default_handler")
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *args, **kwargs):
        _default_handler._logger.warning(u"Requested GET [%s] method with these params [%s][%s].",
                                         cherrypy.request.path_info, args, kwargs)
        return {"error": u"Invalid GET method requested"}

    @cherrypy.tools.json_out()
    def PUT(self, *args, **kwargs):
        _default_handler._logger.warning(u"Requested PUT [%s] method with these params [%s][%s].",
                                         cherrypy.request.path_info, args, kwargs)
        return {"error": u"Invalid PUT method requested"}

    @cherrypy.tools.json_out()
    def POST(self, *args, **kwargs):
        _default_handler._logger.warning(u"Requested POST [%s] method with these params [%s][%s].",
                                         cherrypy.request.path_info, args, kwargs)
        return {"error": u"Invalid POST method requested"}

    @cherrypy.tools.json_out()
    def DELETE(self, *args, **kwargs):
        _default_handler._logger.warning(u"Requested DELETE [%s] method with these params [%s][%s].",
                                         cherrypy.request.path_info, args, kwargs)
        return {"error": u"Invalid DELETE method requested"}


# Application specific for cherrypy framework
#

class app(object):
    """
        Sample request handler class.
    """
    _cp_config = {
        "request.error_response": handle_error
    }

    def __init__(self):
        """ Default ctor. """
        pass

    # if no one is available default will be called
    default = _default_handler()


def mount_handlers(env_dict, main_app, handlers):
    """
    Mount different APIs to app_inst.

    Example of `env_dict`::

      "server"  : {
      ...
        "handlers" : {
          "extract"     : "/status",
          "ready"       : "/ready",
          "reload"      : "/reload",
        }
      }

    """
    for handler_cls in handlers:
        handler = handler_cls()
        setattr(main_app,
                handler.exposed_uri.strip("/"),
                handler)
