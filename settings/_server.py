# coding=utf-8
# See main file for licence
# pylint: disable=W0702,R0201

"""
  Settings server (request, response).
"""

settings = {

    "server": {
        "host": "127.0.0.1",
        "port": 8280,

        # to be filled at runtime
        "version": "",

        "allow-cross-domain": True,
        "timeout": 60,

        # filled out by applications plugins
        "handlers": {
        },


        # optional
        "handler-tools": {
            "threadstatus": "/status-thread",
            "serverstatus": "/status-server",
            #"exit": "/exitter",
            "version": "/version",
            "logger": "/logger",
        },

        "log_every_request": True,

    },

    "response": {
        "json": {
            "indent": 2,
        },

    },
}
