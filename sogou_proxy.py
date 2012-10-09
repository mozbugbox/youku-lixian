#!/usr/bin/python
# vim:fileencoding=utf-8:sw=4:et

from __future__ import print_function, unicode_literals, absolute_import

__version__ = "1.0"

import sys, os
import logging as log
import urllib2
import struct
import random
import time

def gen_cn_ip():
    """Create a China IP"""
    base = "220.181.1{}.{}".format(
            random.randint(0, 55),
            random.randint(1, 255))
    return base

def gen_sogou_auth():
    """Generate sogou auth tag"""
    sogou_auth_suffix = "/30/853edc6d49ba4e27"
    rands = [random.randint(0, 65536) for x in range(8)]
    tmp = ["{:04X}".format(x) for x in rands]
    tmp.append(sogou_auth_suffix)
    ret = "".join(tmp)
    return ret

CN_IP = gen_cn_ip()
SOGOU_AUTH = gen_sogou_auth()

def calc_sogou_hash(timestamp, host):
    """Generate a sogou tag based on a timestamp and a hostname"""
    s = "%s%s%s" % (timestamp, host, "SogouExplorerProxy")
    length = code = len(s)
    dwords = code // 4
    rest = code % 4
    v = struct.unpack(b"%di%ds" % (dwords, rest), s)
    for i in xrange(dwords):
        vv = v[i]
        a = vv & 0xFFFF
        b = vv >> 16
        code += a
        code ^= ((code << 5) ^ b) << 0xb
        # To avoid overflows
        code &= 0xffffffff
        code += code >> 0xb
    if rest == 3:
        code += ord(s[length - 2]) * 256 + ord(s[length - 3])
        code ^= (code ^ (ord(s[length - 1]) * 4)) << 0x10
        code &= 0xffffffff
        code += code >> 0xb
    elif rest == 2:
        code += ord(s[length - 1]) * 256 + ord(s[length - 2])
        code ^= code << 0xb
        code &= 0xffffffff
        code += code >> 0x11
    elif rest == 1:
        code += ord(s[length - 1])
        code ^= code << 0xa
        code &= 0xffffffff
        code += code >> 0x1
    code ^= code * 8
    code &= 0xffffffff
    code += code >> 5
    code ^= code << 4
    code &= 0xffffffff
    code += code >> 0x11
    code ^= code << 0x19
    code &= 0xffffffff
    code += code >> 6
    code &= 0xffffffff
    return "{:08x}".format(code)

class SogouProxyHandler(urllib2.ProxyHandler):
    """ProxyHandler to use sogou proxy service"""
    SERVER_TYPES = [
        ("edu", 3),
        ("dxt", 3),
    ]

    def __init__(self, do_not_track=True):
        self.do_not_track = do_not_track
        import urllib
        proxy = urllib.getproxies()
        proxy["http"] = self.get_sogou_proxy()
        urllib2.ProxyHandler.__init__(self, proxy)

    def get_sogou_proxy(self):
        server_type = "dxt"
        server_range = 5
        server_idx = random.randint(0, server_range)
        sogou_host = "h%d.%s.bj.ie.sogou.com" % (server_idx, server_type)
        return sogou_host

    def http_request(self, request):
        """Fix HTTP headers before sending out request"""
        timestamp = "{:08x}".format(int(time.time()))
        host = request.get_origin_req_host()
        sogou_tag = calc_sogou_hash(timestamp, host)
        request.add_header("X-Sogou-Auth", SOGOU_AUTH)
        request.add_header("X-Sogou-Timestamp", timestamp)
        request.add_header("X-Sogou-Tag", sogou_tag)
        request.add_header("X-Forwarded-For", CN_IP)

        if not request.has_header("DNT") and self.do_not_track:
            request.add_header("DNT", "1")
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0 SogouProxy/{}".format(__version__))

        # change proxy on each connection
        proxy_host = self.get_sogou_proxy()
        request.set_proxy(proxy_host, "http")
        return request

def install_proxy_opener_with_cookie():
    """Short cut to install sogou proxy to urllib2 default opener"""
    import cookielib
    cookiejar = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)

    sogou_proxy = SogouProxyHandler()
    opener = urllib2.build_opener(sogou_proxy, cookie_handler)
    urllib2.install_opener(opener)
    return cookiejar

def main():
    log_level = log.INFO
    log.basicConfig(format="%(levelname)s>> %(message)s", level=log_level)
    print("SOGOU_AUTH: {}".format(SOGOU_AUTH))
    print("CN_IP: {}".format(CN_IP))

    timestamp = hex(int(time.time()))[2:].rstrip("L").zfill(8)
    timestamp2 = "{:08x}".format(int(time.time()))
    print("Time Stamp: {} {}".format(timestamp, timestamp2))

    print("\nTesting remote proxy:")
    install_proxy_opener_with_cookie()
    #test_url = "http://www.lagado.com/proxy-test"
    test_url = "http://scooterlabs.com/echo"
    fd = urllib2.urlopen(test_url)
    print(fd.read())

if __name__ == '__main__':
    main()

