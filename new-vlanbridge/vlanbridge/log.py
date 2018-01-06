#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
def logfile(logfile):
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt = '%a, %d %b %Y %H:%M:%S',
        filename = logfile,
        filemode = 'w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-4s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
def main():
    logging.info('This is info message')
if __name__== '__main__':
    main()



