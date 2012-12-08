#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cgi
import sys, os
import codecs

sys.path.insert(0, '/data/web-latin/wsgi/scansion')

from scandeur import scande_texte

def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain; charset=utf-8')])

    post_env = env.copy()
    post_env['QUERY_STRING'] = ''
    post = cgi.FieldStorage(
        fp=env['wsgi.input'],
        environ=post_env,
        keep_blank_values=True
    )
    
    type = post["type"].value
    
    vers = unicode(post["texte"].value, "utf-8").splitlines()

    #yield repr(vers)

    for r in scande_texte(type, vers):
        yield codecs.encode(r, "utf-8") + "\n"

#    yield repr(post)


#     yield '<h1>FastCGI Environment</h1>'
#     yield '<table>'
#     for k, v in sorted(environ.items()):
#          yield '<tr><th>%s</th><td>%s</td></tr>' % (escape(k), escape(v))
#     yield '</table>'


if __name__ == "__main__":
        f = codecs.open("horace_brut.txt", "r", encoding="utf-8")
    
        for r in scande_texte("hdsi", f):
            print r