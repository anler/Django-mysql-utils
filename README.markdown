MySQL specific tweaks in order to gain efficiency
=================================================

References:
-----------
* Blog Post: http://www.tablix.org/~avian/blog/archives/2011/07/django_admin_with_large_tables/
* Github Gist: https://gist.github.com/1068255

Description:
------------
Counting all rows is very expensive on large Innodb tables. This is a replacement for QuerySet that returns an approximation if count() is called with no additional constraints. In all other cases it should behave exactly as QuerySet.
Only works with MySQL. Behaves normally for all other engines.

Usage:
------
Just create a custom Manager that uses the Query class in optimizedquery.py instead of Django's default and
use that manager in your models:

    import optimizedquery
    
    class MySQLOptimizedManager(models.Manager):
        def get_query_set(self):
            return QuerySet(self.model, using=self._db, query=optimizedquery.Query(self.model))

An use case:
    
    >>> from django.db import connection
    >>> from myapp.models import City
    >>> City.objects.count()
    69495834L
    >>> connection.queries
    [{'sql': u'SHOW TABLE STATUS LIKE myapp_city', 'time': '0.387'}]
    >>> City.objects.filter(name__icontains='Madrid').count()
    70
    >>> connection.queries
    [{'sql': u'SHOW TABLE STATUS LIKE myapp_city', 'time': '0.387'},
     {'sql': u'SELECT COUNT(*) FROM `myapp_city` WHERE `myapp_city`.`name` LIKE %Madrid% ',
      'time': '0.041'}]

