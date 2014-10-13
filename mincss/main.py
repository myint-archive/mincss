from __future__ import absolute_import
from __future__ import print_function

import io
import os
import sys
import time

from .processor import Processor


def run(args):
    options = {'debug': args.verbose}
    if args.phantomjs_path:
        options['phantomjs'] = args.phantomjs_path
    elif args.phantomjs:
        options['phantomjs'] = True
    p = Processor(**options)
    t0 = time.time()
    p.process(args.url)
    t1 = time.time()
    print('TOTAL TIME ', t1 - t0, file=sys.stderr)
    for inline in p.inlines:
        print('ON', inline.url, file=sys.stderr)
        print('AT line', inline.line, file=sys.stderr)
        print('BEFORE '.ljust(79, '-'), file=sys.stderr)
        print(inline.before, file=sys.stderr)
        print('AFTER '.ljust(79, '-'), file=sys.stderr)
        print(inline.after, file=sys.stderr)
        print(file=sys.stderr)

    if not os.path.isdir(args.output):
        os.mkdir(args.output)
    for link in p.links:
        print('FOR', link.href)
        orig_name = link.href.split('/')[-1]
        with io.open(os.path.join(args.output, orig_name), 'w') as f:
            f.write(link.after)
        before_name = 'before_' + link.href.split('/')[-1]
        with io.open(os.path.join(args.output, before_name), 'w') as f:
            f.write(link.before)
        print('Files written to\n', args.output, file=sys.stderr)
        print(
            '(from %d to %d saves %d)' %
            (len(link.before), len(link.after),
             len(link.before) - len(link.after)),
            file=sys.stderr
        )

    return 0


def main():
    import argparse
    parser = argparse.ArgumentParser()
    add = parser.add_argument
    add('url', type=str,
        help='URL to process')
    add('-o', '--output', action='store', required=True,
        help='directory where to put output')
    add('-v', '--verbose', action='store_true',
        help='increase output verbosity')
    add('--phantomjs', action='store_true',
        help='Use PhantomJS to download the source')
    add('--phantomjs-path', action='store',
        default='',
        help='Where is the phantomjs executable')

    args = parser.parse_args()
    return run(args)
