#!/usr/bin/python
import sys
import textile
import re
import unittest
import base64
from jinja2 import Environment, PackageLoader
from bs4 import BeautifulSoup as bs
from urllib2 import urlopen

class Ptm():
    def read_infile(self, path):
        infile = open(path)
        text = infile.read()
        infile.close()
        return text
    
    def parse_infile(self, infile):
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
    
    def build_html(self, config, text):
        config['body'] = self.render_textile(text) 
        html = self.apply_template(config)
        html = self.replace_images(html)
        return html

    def render_textile(self, text):
        html = textile.textile(text)
        return html

    def apply_template(self, config):
        env = Environment(loader=PackageLoader('ptm', 'templates'))
        template = env.get_template(config['template'])
        html = template.render(config)
        return html

    def replace_images(self, html):
        html = unicode(html)
        imgre = re.compile(r'<img [^>]*?src="([^"]+)"[^>]*?/?>')
        imgs = []
        paths = []
        for img in imgre.finditer(html):
            imgs.append(img.group(0))
            paths.append(img.group(1))
        for i, path in enumerate(paths):
            if path[:4] == 'http':
                u = urlopen(path)
                data = u.read()
                u.close()
            else:
                f = open(path)
                data = f.read()
                f.close()
            b64 = base64.b64encode(data)
            ext = path.split('.')[-1]
            if ext == 'png':
                newsrc = "data:image/png;base64,"+b64
            if ext == 'gif':
                newsrc = "data:image/gif;base64,"+b64
            if ext == 'jpg' or ext == 'jpeg':
                newsrc = "data:image/jpg;base64,"+b64
            
            newimg = imgs[i].replace(path, newsrc)
            html = html.replace(imgs[i], newimg)
        return html
    
    def write_output(self, path, data):
        out = open(path, 'w')
        out.write(data)
        out.close()
    
    def process(self, infile, outfile):
        indata = self.read_infile(infile)

        config, text = self.parse_infile(indata)
        html = self.build_html(config, text)
        
        self.write_output(outfile, html)
    
    
class TestPtm(unittest.TestCase):
    
    def setUp(self):
        self.ptm = Ptm()
        self.maxDiff = None
    
    def testReadAndParseInfile(self):
        infile = self.ptm.read_infile("example-source.txl")

        expected_config = {'template': 'default.html', 'title':'Some title' }
        expected_text = "\nh1. This is a example\n\nHello\nthis is a *example*\n\n!fixtures/image.png!\n\n"

        config, text = self.ptm.parse_infile(infile)
        
        self.assertEqual(expected_config, config)
        self.assertEqual(expected_text, text)

    def testReplaceImages(self):
        html = open("fixtures/input_replace_image.html").read()

        expected = unicode(open("fixtures/expected_replace_image.html").read())
        result = self.ptm.replace_images(html)

        self.assertEqual(expected, result)

    def testCode(self):
        infile = open("fixtures/input_code.html").read()
        expected = unicode(open("fixtures/expected_code.html").read())
        
        config, text = self.ptm.parse_infile(infile)
        result = self.ptm.build_html(config, text)

        self.assertEqual(expected, result+"\n")
        

def main(args):
    if len(args) == 1 and args[0] == 'test':
        suite = unittest.TestLoader().loadTestsFromTestCase(TestPtm)
        unittest.TextTestRunner(verbosity=2).run(suite)
        return

    if len(args) != 2:
        print "Usage: ptm source.txl outfile.htm"
        return

    ptm = Ptm()
    ptm.process(args[0], args[1])

if __name__ == "__main__":
    main(sys.argv[1:])
