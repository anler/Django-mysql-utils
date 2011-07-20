from django.db import connections
from django.db.models import sql


class Query(sql.Query):
    """Counting all rows is very expensive on large Innodb tables. This
    is a replacement for QuerySet that returns an approximation if count()
    is called with no additional constraints. In all other cases it should
    behave exactly as QuerySet.
    Only works with MySQL. Behaves normally for all other engines.
    
    Usage:
    Just create a custom Manager that uses this class instead of Django's and
    use that manager in your model.

    >>> import optimizedquery
    >>>
    >>> class MySQLOptimizedManager(models.Manager):
    >>>     def get_query_set(self):
    >>>         return QuerySet(self.model, using=self._db, query=optimizedquery.Query(self.model))
    """ 

    def get_count(self, using):
        """Performs a COUNT() query using the current filter constraints but
        optimized for InnoDB tables."""
        # In only the case we are simply doing a plain
        # "SELECT COUNT(*) FROM foo" query. Hack the query so we
        # get an approximation(faster result) instead. 
        sql = str(self)
        if 'WHERE' in sql:
            return super(MySQLOptimizedQuery, self).get_count(using)
        else:
            cursor = connections[using].cursor()
            cursor.execute("SHOW TABLE STATUS LIKE %s", (self.model._meta.db_table,))
            number = cursor.fetchall()[0][4]

            # Django code:
            # Apply offset and limit constraints manually, since using LIMIT/OFFSET
            # in SQL (in variants that provide them) doesn't change the COUNT
            # output.
            number = max(0, number - self.low_mark)
            if self.high_mark is not None:
                number = min(number, self.high_mark - self.low_mark)

            return number