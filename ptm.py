#!/usr/bin/python
import sys
import textile
import re
from jinja2 import Environment, PackageLoader

def read_infile(path):
    infile = open(path)
    text = infile.read()
    infile.close()
    return text

def parse_infile(infile):
    config = {'template': 'default.html'}
    text = ""
    configdone = False
    for line in infile.split("\n"):
        if not configdone and re.match(r"^[^=]+=[^=]+$", line):
            key, val = line.split('=')
            config[key] = val
        else:
            configdone = True
            text += line+"\n"

    return config, text

def write_output(path, data):
    out = open(path, 'w')
    out.write(data)
    out.close()

def main(args):
    if(len(args) != 2):
        print "Usage: ptm source.txl outfile.htm"
        return

    infile = read_infile(args[0])
    context, text = parse_infile(infile)
    context['body'] = textile.textile(text)

    env = Environment(loader=PackageLoader('ptm', 'templates'))
    template = env.get_template(context['template'])
    html = template.render(context)
    
    write_output(args[1], html)

if __name__ == "__main__":
    main(sys.argv[1:])
