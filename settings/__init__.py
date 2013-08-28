# coding=utf-8
# See main file for licence
# pylint: disable=W0702,R0201

"""
  Settings module.
"""
import os
import re

settings = {


    # name
    "name": u"Ufal service server v1.0",

    # logger config - read from _logger
    "logger_config": os.path.join( os.path.dirname(__file__),
                                   "logger.config"),

    # use system default temp dir
    "temporary_directory": None,

    "runners": {
        # delete all temp files
        "cleanup": True,
    }

}  # settings


def smart_extend(what, with_what):
    """ Extend dicts instead of replace items.  """
    for k, v in with_what.iteritems( ):
        if k in what and isinstance( what[k], dict ):
            smart_extend( what[k], v )
        else:
            what[k] = v

# update settings with global ones
#
from . import _server
smart_extend( settings, _server.settings )
