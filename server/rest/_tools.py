# coding=utf-8
# See main file for licence
# pylint: disable=W0702,R0201,C0111,W0613,W0212,E0202,W0231,W0703,R0912

"""
  Cherrypy app tools.
"""

import threading
import time
import cherrypy
import logging

_logger = logging.getLogger("server")

from utils import initialize_logging, get_logger_messages
from settings import settings as settings_inst


# helpers
#

def add_cross_domain_access_headers_if_set():
    """
        Allow cross domain requests to these services.

        Javascript specific.
    """
    if settings_inst["server"]["allow-cross-domain"]:
        response = cherrypy.response
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'


def handle_error(code=None, message=None):
    """
        Handles real errors inside the cherrypy framework e.g., exceptions in our code.
    """
    add_cross_domain_access_headers_if_set()
    code = code or 500
    message = message or 'Ouch, an error occurred. See logs for more details.'
    _logger.critical(u"Error occurred [%s] with status [%s] and body [%s], returning [%s] [%s]",
                     cherrypy._cperror.format_exc(), cherrypy.response.status, cherrypy.response.body,
                     code, message)
    #cherrypy.response.status = 500
    #cherrypy.response.body = [ "<html><body>Ouch, an error occurred. See logs for more details.</body></html>" ]
    raise cherrypy.HTTPError(code, message)


#
#
#

#noinspection PyDocstring
class ThreadStatus(object):
    """ Status of one thread """
    start = None
    end = None
    url = None

    def last_req_time(self):
        if self.end is None:
            return 0
        return self.end - self.start

    def idle_time(self):
        if self.end is None:
            return 0
        return time.time() - self.end


#noinspection PyDocstring
class StatusMonitor(cherrypy.Tool):
    """Register the status of each thread."""

    def __init__(self):
        self._point = 'on_start_resource'
        self._name = 'status'
        self._priority = 50
        self.seen_threads = {}

    def callable(self):
        threadID = threading._get_ident()
        ts = self.seen_threads.setdefault(threadID, ThreadStatus())
        ts.start = cherrypy.response.time
        ts.url = cherrypy.url()
        ts.end = None

    def unregister(self):
        """Unregister the current thread."""
        threadID = threading._get_ident()
        if threadID in self.seen_threads:
            self.seen_threads[threadID].end = time.time()

    def _setup(self):
        """ Setup the monitor. """
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource', self.unregister)


cherrypy.tools.status = StatusMonitor()


#noinspection PyDocstring
class RootThreadStatus(object):
    @cherrypy.tools.json_out()
    def index(self):
        if 'options' == cherrypy.request.method.lower():
            return {}
        thread_items = cherrypy.tools.status.seen_threads.items()
        cherrypy_thread_stats = [
            {
                "id": _id,
                "idle_time": ts.idle_time(),
                "last_req_time": ts.last_req_time(),
                "url": ts.url,
            } for _id, ts in thread_items]
        thread_stats = [
            {
                "id": t.ident,
                "name": t.name,
                "alive": t.is_alive(),
                "daemon": t.daemon,
            } for t in threading.enumerate()]

        return {
            "cherrypy": cherrypy_thread_stats,
            "all": thread_stats,
        }

    index.exposed = True


#noinspection PyDocstring
class _exit_tool(object):
    """
  Gracefully exits cherrypy.
  """
    in_progress = False

    @staticmethod
    def exit_implementation():
        """ Exit cherrypy engine. """
        try:
            cherrypy.engine.exit()
        except Exception, e:
            _logger.warning(u"Not a clean shutdown [%s].", repr(e))

    @cherrypy.tools.json_out()
    def index(self):
        if 'options' == cherrypy.request.method.lower():
            return {}
        ret_exit = _exit_tool.in_progress
        _exit_tool.in_progress = True
        import thread

        thread.start_new_thread(_exit_tool.exit_implementation, ())
        return {
            "exit": u"started" if not ret_exit else u"in progress",
        }

    index.exposed = True

    @staticmethod
    def send(url):
        """
        Send exitter the hard way.
      """
        import urllib2

        req = urllib2.Request(url)
        urllib2.urlopen(req)


#
#
#

#noinspection PyDocstring
class _logger_info(object):
    """
    What has been logged
  """
    #noinspection PyUnusedLocal
    @cherrypy.tools.json_out()
    def index(self, *args, **kwargs):
        """
            If no param specified, assume it is OPTIONS call.
        """
        add_cross_domain_access_headers_if_set()
        if 'options' == cherrypy.request.method.lower():
            return {}

        if "debug" in kwargs:
            if kwargs["debug"].lower() == "true":
                initialize_logging(settings_inst["logger_config_debug"])
                _logger.debug(u"Changed logging to debug.")
            elif kwargs["debug"].lower() == "false":
                incremental_copy = settings_inst["logger_config"].copy()
                incremental_copy["incremental"] = True
                initialize_logging(incremental_copy)
                _logger.debug(u"This should not be here (if not debug set explicitly).")
                _logger.info(u"Changed logging to default.")

        return {
            "messages": get_logger_messages("server"),
            "version": settings_inst["server"]["version"],
        }

    index.exposed = True


#noinspection PyDocstring
class _version_info(object):
    """
        Version
    """
    #noinspection PyUnusedLocal
    @cherrypy.tools.json_out()
    def index(self, *args, **kwargs):
        """
            If no param specified, assume it is OPTIONS call.
        """
        add_cross_domain_access_headers_if_set()
        if 'options' == cherrypy.request.method.lower():
            return {}
        try:
            from applications import app_plugins_classes
            avail_plugins_str = u"\n\t".join([ repr(x) for x in app_plugins_classes ] )
        except:
            avail_plugins_str = "error fetching plugins"

        return {
            "plugins": avail_plugins_str,
            "version": settings_inst["server"]["version"],
        }

    # noinspection PyUnresolvedReferences
    index.exposed = True


def _log_request():
    """
        Log requests.
    """
    req = cherrypy.request
    _logger.info(u"Processing: %s(%s) requested %s, query string [%s], X-Forwarded-For [%s], "
        "headers [%s], body params [%s]", 
        req.remote.ip, req.remote.name, req.request_line, req.query_string, req.headers.get("X-Forwarded-For", "None"),
        req.headers, req.body_params)


#
#
#

def mount_tools(env_dict):
    """
    Mount different status pages if applicable.

    Example of `env_dict`::

      "server"  : {
      ...
        "handler-tools" : {
          "threadstatus"  : "/status-thread",
          "status"        : "/status",
          "exit"          : "/exitter",
          "debug-db"      : "/db",
        }
      }

  """
    if env_dict["server"].get("log_every_request", False):
        cherrypy.request.hooks.attach("on_start_resource",
                                      _log_request,
                                      failsafe=True,
                                      priority=0)

    assert env_dict["server"]["handler-tools"], \
        "Missing [server][handler-tools] dict entry."

    if "threadstatus" in env_dict["server"]["handler-tools"]:
        cherrypy.config.update({"tools.status.on": True})
        cherrypy.tree.mount(RootThreadStatus(),
                            env_dict["server"]["handler-tools"]["threadstatus"])

    if "status" in env_dict["server"]["handler-tools"]:
        from cherrypy.lib import cpstats

        cherrypy.tree.mount(
            cpstats.StatsPage(),
            env_dict["server"]["handler-tools"]["status"],
            {
                env_dict["server"]["handler-tools"]["status"]: {
                    'tools.cpstats.on': True
                }
            })

    if "exit" in env_dict["server"]["handler-tools"]:
        cherrypy.tree.mount(_exit_tool(),
                            env_dict["server"]["handler-tools"]["exit"])

    if "logger" in env_dict["server"]["handler-tools"]:
        cherrypy.tree.mount(_logger_info(),
                            env_dict["server"]["handler-tools"]["logger"])

    if "version" in env_dict["server"]["handler-tools"]:
        cherrypy.tree.mount(_version_info(),
                            env_dict["server"]["handler-tools"]["version"])
