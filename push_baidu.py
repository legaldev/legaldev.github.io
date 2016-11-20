# -*- coding: utf-8 -*-
import urllib2
import requests

url = 'http://data.zz.baidu.com/urls?site=disenone.github.io&token=gjZXbMTC0FfXAEuZ'

def run():
    sitemap = urllib2.urlopen('http://disenone.github.io/sitemap.txt')
    sites = sitemap.read()
    sites = sites.split('\n')
    sites = filter(lambda x: x, sites)
    sites = '\n'.join(sites)

    return requests.post(url, data=sites).text

if __name__ == '__main__':
    print run()
