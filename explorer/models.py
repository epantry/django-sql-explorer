from explorer.utils import passes_blacklist, write_csv, swap_params, execute_query
from django.db import models, DatabaseError
from django.core.urlresolvers import reverse

MSG_FAILED_BLACKLIST = "Query failed the SQL blacklist."


class Query(models.Model):
    title = models.CharField(max_length=255)
    sql = models.TextField()
    description = models.TextField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    params = {}

    class Meta:
        ordering = ['title']
    
    def __unicode__(self):
        return unicode(self.title)

    def passes_blacklist(self):
        return passes_blacklist(self.final_sql())

    def final_sql(self):
        return swap_params(self.sql, self.params)

    def csv_report(self):
        headers, data, error = self.headers_and_data()
        if error:
            return error
        return write_csv(headers, data)

    def headers_and_data(self):
        if not self.passes_blacklist():
            return [], [], MSG_FAILED_BLACKLIST
        try:
            return execute_query(self.final_sql())
        except DatabaseError, e:
            return [], [], e

    def get_absolute_url(self):
        return reverse("query_detail", kwargs={'query_id': self.id})