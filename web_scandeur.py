#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cgi
import sys, os

def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])

    post_env = env.copy()
    post_env['QUERY_STRING'] = ''
    post = cgi.FieldStorage(
        fp=env['wsgi.input'],
        environ=post_env,
        keep_blank_values=True
    )
    
    yield repr(post)


#     yield '<h1>FastCGI Environment</h1>'
#     yield '<table>'
#     for k, v in sorted(environ.items()):
#          yield '<tr><th>%s</th><td>%s</td></tr>' % (escape(k), escape(v))
#     yield '</table>'

