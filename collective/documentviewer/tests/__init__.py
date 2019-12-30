import unittest
from os.path import dirname, join

from collective.documentviewer.interfaces import ILayer
from collective.documentviewer.testing import DocumentViewer_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles
from plone.namedfile.file import NamedBlobFile
from Products.CMFPlone.utils import safe_unicode
from zope.interface import alsoProvides
import celery
_files = join(dirname(__file__), 'test_files')


class BaseTest(unittest.TestCase):

    layer = DocumentViewer_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, ILayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def createFile(self, name=u"test.pdf", id='test1'):
        with open(join(_files, name), 'rb') as fi:
            pdf_data = fi.read()
        if id in self.portal.objectIds():
            api.content.delete(self.portal[id])
        return api.content.create(
            container=self.portal,
            type='File', id=id,
            file=NamedBlobFile(data=pdf_data, filename=safe_unicode(name)))

    def tearDown(self):
        pass
