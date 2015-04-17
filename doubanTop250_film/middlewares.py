# -*- coding: utf-8 -*-

import socket
from scrapy import log
from scrapy.exceptions import CloseSpider

class UnknownResponseError(Exception):
    """未处理的错误"""
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr(self.value)
        else:
            return 'UnknownResponseError'


class ShouldNotEmptyError(Exception):
    """返回不应该为空，但是为空了，在spider里抛出"""
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        if self.value:
            return repr(self.value)
        else:
            return 'ShouldNotEmptyError'


class RequestCountMiddleware(object):
    def __init__(self, host, port):
        self.r = _default_redis(host, port)
        ip = socket.gethostbyname(socket.gethostname())
        self.req_count_key = 'req_count_{ip}'.format(ip=ip)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        host = settings.get('REDIS_HOST')
        port = settings.get('REDIS_PORT')
        return cls(host, port)

    def process_request(self, request, spider):
        count = self.r.incr(self.req_count_key)
        log.msg(format='Spider [%(spider)s] Request count: %(count)s',
                level=log.INFO, spider=spider.name, count=count)


class RetryErrorResponseMiddleware(object):
    def __init__(self, retry_times):
        self.retry_times = retry_times

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        retry_times = settings.get('RETRY_TIMES', 3)
        return cls(retry_times)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0)
        if retries < self.retry_times:
            log.msg(format="Retrying %(request)s (failed %(retries)d times): %(reason)s",
                    level=log.WARNING, spider=spider, request=request, retries=retries, reason=reason)
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            return retryreq
        else:
            log.msg(format="Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                    level=log.ERROR, spider=spider, request=request, retries=retries, reason=reason)

    def process_spider_exception(self, response, exception, spider):
        if 'dont_retry' not in response.request.meta and isinstance(exception, UnknownResponseError):
            return [self._retry(response.request, exception, spider)]
