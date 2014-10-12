#!/usr/bin/env python

import os
import unittest

# make sure it's running the mincss here and not anything installed
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mincss.processor import Processor


try:
    unicode
except NameError:
    unicode = str


HERE = os.path.realpath(os.path.dirname(__file__))

PHANTOMJS = os.path.join(HERE, 'fake_phantomjs')


class TestMinCSS(unittest.TestCase):

    def test_just_inline(self):
        html = os.path.join(HERE, 'one.html')
        url = 'file://' + html
        p = Processor()
        p.process(url)
        # on line 7 there inline css starts
        # one.html only has 1 block on inline CSS
        inline = p.inlines[0]
        lines_after = inline.after.strip().splitlines()
        self.assertEqual(inline.line, 7)
        self.assertTrue(len(inline.after) < len(inline.before))

        # compare line by line
        expect = '''
            h1, h2, h3 { text-align: center; }
            h3 { font-family: serif; }
            h2 { color:red }
        '''
        for i, line in enumerate(expect.strip().splitlines()):
            self.assertEqual(line.strip(), lines_after[i].strip())

    def test_just_one_link(self):
        html = os.path.join(HERE, 'two.html')
        url = 'file://' + html
        p = Processor()
        p.process(url)
        # two.html only has 1 link CSS ref
        link = p.links[0]
        self.assertEqual(link.href, 'two.css')
        self.assertTrue(len(link.after) < len(link.before))
        lines_after = link.after.splitlines()
        # compare line by line
        expect = '''
            body, html { margin: 0; }
            h1, h2, h3 { text-align: center; }
            h3 { font-family: serif; }
            h2 { color:red }
        '''
        for i, line in enumerate(expect.strip().splitlines()):
            self.assertEqual(line.strip(), lines_after[i].strip())

    def test_one_link_two_different_pages(self):
        html = os.path.join(HERE, 'two.html')
        url1 = 'file://' + html
        html_half = os.path.join(HERE, 'two_half.html')
        url2 = 'file://' + html_half
        p = Processor()
        p.process(url1, url2)
        # two.html only has 1 link CSS ref
        link = p.links[0]
        self.assertEqual(link.href, 'two.css')
        self.assertTrue(len(link.after) < len(link.before))
        lines_after = link.after.splitlines()
        # compare line by line
        expect = '''
            body, html { margin: 0; }
            h1, h2, h3 { text-align: center; }
            h3 { font-family: serif; }
            .foobar { delete:me }
            .foobar, h2 { color:red }
        '''
        for i, line in enumerate(expect.strip().splitlines()):
            self.assertEqual(line.strip(), lines_after[i].strip())

    def test_pseudo_selectors_hell(self):
        html = os.path.join(HERE, 'three.html')
        url = 'file://' + html
        p = Processor(preserve_remote_urls=False)
        p.process(url)
        # two.html only has 1 link CSS ref
        link = p.links[0]
        after = link.after
        self.assertTrue('a.three:hover' in after)
        self.assertTrue('a.hundred:link' not in after)

        self.assertTrue('.container > a.one' in after)
        self.assertTrue('.container > a.notused' not in after)
        self.assertTrue('input[type="button"]' not in after)

        self.assertTrue('input[type="search"]::-webkit-search-decoration' in after)
        self.assertTrue('input[type="reset"]::-webkit-search-decoration' not in after)

        self.assertTrue('@media (max-width: 900px)' in after)
        self.assertTrue('.container .two' in after)
        self.assertTrue('a.four' not in after)

        self.assertTrue('::-webkit-input-placeholder' in after)
        self.assertTrue(':-moz-placeholder {' in after)
        self.assertTrue('div::-moz-focus-inner' in after)
        self.assertTrue('button::-moz-focus-inner' not in after)

        self.assertTrue('@-webkit-keyframes progress-bar-stripes' in after)
        self.assertTrue('from {' in after)

        # some day perhaps this can be untangled and parsed too
        self.assertTrue('@import url(other.css)' in after)

    def test_media_query_simple(self):
        html = os.path.join(HERE, 'four.html')
        url = 'file://' + html
        p = Processor()
        p.process(url)

        link = p.links[0]
        after = link.after
        self.assertTrue('/* A comment */' in after, after)
        self.assertTrue('@media (max-width: 900px) {' in after, after)
        self.assertTrue('.container .two {' in after, after)
        self.assertTrue('.container .nine {' not in after, after)
        self.assertTrue('a.four' not in after, after)

    def test_double_classes(self):
        html = os.path.join(HERE, 'five.html')
        url = 'file://' + html
        p = Processor()
        p.process(url)

        after = p.links[0].after
        self.assertEqual(after.count('{'), after.count('}'))
        self.assertTrue('input.span6' in after)
        self.assertTrue('.uneditable-input.span9' in after)
        self.assertTrue('.uneditable-{' not in after)
        self.assertTrue('.uneditable-input.span3' not in after)

    def test_complicated_keyframes(self):
        html = os.path.join(HERE, 'six.html')
        url = 'file://' + html
        p = Processor()
        p.process(url)

        after = p.inlines[0].after
        self.assertEqual(after.count('{'), after.count('}'))
        self.assertTrue('.pull-left' in after)
        self.assertTrue('.pull-right' in after)
        self.assertTrue('.pull-middle' not in after)

    def test_ignore_annotations(self):
        html = os.path.join(HERE, 'seven.html')
        url = 'file://' + html
        p = Processor()
        p.process(url)

        after = p.inlines[0].after
        self.assertEqual(after.count('{'), after.count('}'))
        self.assertTrue('/* Leave this comment as is */' in after)
        self.assertTrue('/* Lastly leave this as is */' in after)
        self.assertTrue('/* Also stick around */' in after)
        self.assertTrue('/* leave untouched */' in after)
        self.assertTrue('.north' in after)
        self.assertTrue('.south' in after)
        self.assertTrue('.east' not in after)
        self.assertTrue('.west' in after)
        self.assertTrue('no mincss' not in after)

    def test_non_ascii_html(self):
        html = os.path.join(HERE, 'eight.html')
        url = 'file://' + html
        p = Processor()
        p.process(url)

        after = p.inlines[0].after
        self.assertTrue(isinstance(after, unicode))
        self.assertTrue(u'Varf\xf6r st\xe5r det h\xe4r?' in after)

    def test_preserve_remote_urls(self):
        html = os.path.join(HERE, 'nine.html')
        url = 'file://' + html
        p = Processor(preserve_remote_urls=True)
        p.process(url)

        after = p.links[0].after
        self.assertTrue("url('http://www.google.com/north.png')" in after)
        url = 'file://' + HERE + '/deeper/south.png'
        self.assertTrue('url("%s")' % url in after)
        # since local file URLs don't have a domain, this is actually expected
        self.assertTrue('url("file:///east.png")' in after)
        url = 'file://' + HERE + '/west.png'
        self.assertTrue('url("%s")' % url in after)

    @unittest.skip('This has always been failing')
    def test_download_with_phantomjs(self):
        html = os.path.join(HERE, 'one.html')
        url = 'file://' + html
        p = Processor(
            phantomjs=PHANTOMJS,
            phantomjs_options={'cookies-file': 'bla'}
        )
        p.process(url)
        # on line 7 there inline css starts
        # one.html only has 1 block on inline CSS
        inline = p.inlines[0]
        lines_after = inline.after.strip().splitlines()
        self.assertEqual(inline.line, 7)
        self.assertTrue(len(inline.after) < len(inline.before))

        # compare line by line
        expect = '''
            h1, h2, h3 { text-align: center; }
            h3 { font-family: serif; }
            h2 { color:red }
        '''
        for i, line in enumerate(expect.strip().splitlines()):
            self.assertEqual(line.strip(), lines_after[i].strip())

    def test_make_absolute_url(self):
        p = Processor()
        self.assertEqual(
            p.make_absolute_url('http://www.com/', './style.css'),
            'http://www.com/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com', './style.css'),
            'http://www.com/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com', '//cdn.com/style.css'),
            'http://cdn.com/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com/', '//cdn.com/style.css'),
            'http://cdn.com/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com/', '/style.css'),
            'http://www.com/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com/elsewhere', '/style.css'),
            'http://www.com/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com/elsewhere/', '/style.css'),
            'http://www.com/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com/elsewhere/', './style.css'),
            'http://www.com/elsewhere/style.css'
        )
        self.assertEqual(
            p.make_absolute_url('http://www.com/elsewhere', './style.css'),
            'http://www.com/style.css'
        )


if __name__ == '__main__':
    unittest.main()
