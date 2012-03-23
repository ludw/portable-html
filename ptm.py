#!/usr/bin/python
import sys
import textile
import re
import unittest
from jinja2 import Environment, PackageLoader
from BeautifulSoup import BeautifulSoup as bs
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
    
    def replace_images(self, html):
        soup = bs(html)
        for img in soup.findAll("img"):
            if img.has_key("src"):
                src = img.src
                data = urlopen(img)
                b64 = base64.b64encode(data)
                newsrc = "data:image/png;base64,"+b64+"="

        return str(soup)
    
    def write_output(self, path, data):
        out = open(path, 'w')
        out.write(data)
        out.close()
    
    def process(self, infile, outfile):
        indata = self.read_infile(infile)
        context, text = self.parse_infile(indata)
        context['body'] = textile.textile(text)
    
        env = Environment(loader=PackageLoader('ptm', 'templates'))
        template = env.get_template(context['template'])
        html = template.render(context)
    
        html = self.replace_images(html)
        
        self.write_output(outfile, html)
    
    
class TestPtm(unittest.TestCase):
    
    def setUp(self):
        self.ptm = Ptm()

    def testReplaceImages(self):
        html = open("fixtures/input_replace_image.html").read()

        expected = open("fixtures/expected_replace_image.html").read() 
        result = self.ptm.replace_images(html)

        self.assertEqual(expected, result)



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
