from django.contrib.sitemaps import Sitemap

from .models import Product, ProductCategory

class ProductSitemap(Sitemap):
        changefreq = 'always'
        priority = 0.9

        def items(self):
                return Product.objects.all()

        def lastmod(self, obj):
                return obj.modified_at
