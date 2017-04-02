from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['explore-poets', 'explore-poetry', ]

    def location(self, item):
        return reverse(item)