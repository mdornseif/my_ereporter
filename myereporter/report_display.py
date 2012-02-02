#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
# Copyright 2012 Dr. Maximillian Dornseif
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Displays exception reports.

See google/appengine/ext/ereporter/__init__.py for usage details.
"""

import datetime
import itertools
import os
import re
from xml.sax import saxutils

from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import ereporter
from google.appengine.ext import webapp
from google.appengine.ext.webapp import _template
from google.appengine.ext.webapp.util import run_wsgi_app


class ReportGenerator(webapp.RequestHandler):
  """Handler class to generate and email an exception report."""

  DEFAULT_MAX_RESULTS = 100

  def __init__(self, *args, **kwargs):
    super(ReportGenerator, self).__init__(*args, **kwargs)

  def GetQuery(self):
    """Creates a query object that will retrieve the appropriate exceptions.

    Returns:
      A query to retrieve the exceptions required.
    """
    q = ereporter.ExceptionRecord.all()
    q.filter('major_version =', self.major_version)
    q.filter('date >=', self.yesterday)
    return q

  def GenerateReport(self, exceptions):
    """Generates an HTML exception report.

    Args:
      exceptions: A list of ExceptionRecord objects. This argument will be
        modified by this function.
    Returns:
      An HTML exception report.
    """

    exceptions.sort(key=lambda e: (e.minor_version, -e.count))
    versions = [(minor, list(excs)) for minor, excs
                in itertools.groupby(exceptions, lambda e: "%s.%s" % (e.major_version, e.minor_version))]

    template_values = {
        'version_filter': self.version_filter,
        'version_count': len(versions),

        'exception_count': sum(len(excs) for _, excs in versions),

        'occurrence_count': sum(y.count for x in versions for y in x[1]),
        'app_id': self.app_id,
        'major_version': self.major_version,
        'date': self.yesterday,
        'versions': versions,
    }
    path = os.path.join(os.path.dirname(__file__), 'templates', 'report.html')
    return _template.render(path, template_values)

  def get(self):
    self.version_filter = 'all'
    self.app_id = os.environ['APPLICATION_ID']
    version = os.environ['CURRENT_VERSION_ID']
    self.major_version, self.minor_version = version.rsplit('.', 1)
    self.minor_version = int(self.minor_version)
    self.yesterday = datetime.date.today() - datetime.timedelta(days=1)

    exceptions = self.GetQuery().fetch(100)
    report = self.GenerateReport(exceptions)
    self.response.out.write(report)
        

application = webapp.WSGIApplication([('.*', ReportGenerator)])


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
