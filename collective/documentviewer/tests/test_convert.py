import shutil
import unittest
from os import listdir
from os.path import join
from tempfile import mkdtemp

from collective.documentviewer import storage
from collective.documentviewer.convert import Converter
from collective.documentviewer.settings import GlobalSettings, Settings
from collective.documentviewer.tests import BaseTest
from DateTime import DateTime
from zope.annotation import IAnnotations
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class ConvertTest(BaseTest):

    def test_converts(self):
        fi = self.createFile('test.pdf')
        settings = Settings(fi)
        self.assertEqual(settings.successfully_converted, True)
        self.assertEqual(settings.num_pages, 1)

    def test_auto_assigns_view(self):
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_select_layout = True
        fi = self.createFile('test.pdf')
        self.assertEqual(fi.getLayout(), 'documentviewer')

    def test_not_auto_assigns_view(self):
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_select_layout = False
        fi = self.createFile('test.pdf')
        self.assertTrue(fi.getLayout() != 'documentviewer')

    def test_auto_convert_word(self):
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_select_layout = True
        gsettings.auto_layout_file_types = ['word']

        fi = self.createFile('test.doc')
        settings = Settings(fi)
        self.assertEqual(settings.successfully_converted, True)
        self.assertEqual(settings.num_pages, 2)

    def test_auto_convert_powerpoint(self):
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_select_layout = True
        gsettings.auto_layout_file_types = ['ppt']

        fi = self.createFile('test.odp')
        settings = Settings(fi)
        self.assertEqual(settings.successfully_converted, True)
        self.assertEqual(settings.num_pages, 1)

    def test_sets_filehash(self):
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_select_layout = True
        gsettings.auto_layout_file_types = ['ppt']

        fi = self.createFile('test.odp')
        settings = Settings(fi)
        self.assertTrue(settings.filehash is not None)

    def test_sets_can_not_convert_after_conversion(self):
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_select_layout = True
        gsettings.auto_layout_file_types = ['ppt']

        fi = self.createFile('test.odp')
        converter = Converter(fi)
        self.assertTrue(not converter.can_convert)

    def test_saves_with_file_storage(self):
        gsettings = GlobalSettings(self.portal)
        gsettings.auto_select_layout = True
        gsettings.auto_layout_file_types = ['ppt']
        gsettings.storage_type = 'File'
        _dir = mkdtemp()
        gsettings.storage_location = _dir

        fi = self.createFile('test.odp')

        fi_dir = storage.getResourceDirectory(obj=fi)
        self.assertEqual(len(listdir(fi_dir)), 5)
        self.assertEqual(len(listdir(join(fi_dir, 'normal'))), 1)
        self.assertEqual(len(listdir(join(fi_dir, 'small'))), 1)
        self.assertEqual(len(listdir(join(fi_dir, 'large'))), 1)
        self.assertEqual(len(listdir(join(fi_dir, 'text'))), 1)
        shutil.rmtree(fi_dir)

    def test_indexation_enabled(self):
        gsettings = GlobalSettings(self.portal)
        # indexation is enabled by default
        self.assertEqual(gsettings.enable_indexation, True)
        fi = self.createFile('test.pdf')
        # make sure conversion was successfull
        self.assertTrue(self._isSuccessfullyConverted(fi))
        annotations = IAnnotations(fi)['collective.documentviewer']
        self.assertIsNotNone(annotations['catalog'])
        # we have relevant informations in the catalog
        self.assertTrue('software' in annotations['catalog']['text'].lexicon.words())

    def test_indexation_disabled(self):
        gsettings = GlobalSettings(self.portal)
        # indexation is enabled by default, so disable it
        gsettings.enable_indexation = False

        fi = self.createFile('test.pdf')
        # make sure conversion was successfull
        self.assertTrue(self._isSuccessfullyConverted(fi))
        annotations = IAnnotations(fi)['collective.documentviewer']
        self.assertTrue(annotations['catalog'] is None)

    def test_indexation_switch_mode(self):
        '''
          Test that switching the indexation from enabled to disabled
          and the other way round keep the state consistent.
        '''
        fi = self.createFile('test.pdf')
        # indexation is enabled by default
        # make sure conversion was successfull
        self.assertTrue(self._isSuccessfullyConverted(fi))
        annotations = IAnnotations(fi)['collective.documentviewer']
        # something is catalogued
        self.assertTrue(annotations['catalog'] is not None)
        # now disable indexation and convert again
        gsettings = GlobalSettings(self.portal)
        gsettings.enable_indexation = False
        # make it convertable again by adapting last_updated and filehash
        annotations['last_updated'] = DateTime('1901/01/01').ISO8601()
        annotations['filehash'] = 'dummymd5'
        notify(ObjectModifiedEvent(fi))
        # make sure conversion was successfull
        self.assertTrue(self._isSuccessfullyConverted(fi))
        # nothing indexed anymore
        self.assertTrue(annotations['catalog'] is None)

    def test_indexation_settings(self):
        '''
          The enable_indexation setting can be defined on the object
          local settings or in the global settings.  Local settings are
          overriding global settings...
        '''
        fi = self.createFile('test.pdf')
        # indexation is enabled by default in the global settings
        # and nothing is defined in the local settings
        # make sure conversion was successfull
        self.assertTrue(self._isSuccessfullyConverted(fi))
        annotations = IAnnotations(fi)['collective.documentviewer']
        self.assertTrue(annotations['catalog'] is not None)
        # nothing defined on the 'fi'
        self.assertTrue('enable_indexation' not in annotations)
        # if we disable indexation in the local settings, this will be
        # taken into account as it overrides global settings
        annotations['enable_indexation'] = False
        # make it convertable again by adapting last_updated and filehash
        annotations['last_updated'] = DateTime('1901/01/01').ISO8601()
        annotations['filehash'] = 'dummymd5'
        notify(ObjectModifiedEvent(fi))
        # make sure conversion was successfull
        self.assertTrue(self._isSuccessfullyConverted(fi))
        # as indexation is disabled in local settings, the text
        # of the PDF is no longer indexed...
        self.assertTrue(annotations['catalog'] is None)

    def _isSuccessfullyConverted(self, fi):
        '''
          Check if the given p_fi was successfully converted
        '''
        # make sure conversion was successfull
        settings = Settings(fi)
        return settings.successfully_converted


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
