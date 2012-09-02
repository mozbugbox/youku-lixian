#!/usr/bin/env python

__all__ = ['qq_download_by_id']

import re
from common import *

def qq_download_by_id(id, title, config):
	url = 'http://vsrc.store.qq.com/%s.flv' % id
	assert title
	merge = config["merge"]
	download_urls([url], title, 'flv', total_size=None, merge=merge)

