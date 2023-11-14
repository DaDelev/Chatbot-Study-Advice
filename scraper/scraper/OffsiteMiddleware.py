import re
from scrapy.spidermiddlewares import offsite

# Unlike the original implementation, this OffsiteMiddleware only allows URLs to
# the root domain, but no other subdomain
# When allowed_domains = [example.com] allows example.com, but not
# www.example.com or sub.example.com
# Original implementation:
# https://github.com/scrapy/scrapy/blob/master/scrapy/spidermiddlewares/offsite.py
class OffsiteMiddleware(offsite.OffsiteMiddleware):
    def get_host_regex(self, spider):
        regex = super().get_host_regex(spider)
        # Allow root domain and www-domain only 
        regex = regex.pattern.replace("(.*\.)?", "(www\.)?", 1)
        return re.compile(regex)