#
# Tests for displayContentsTab script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from Products.CMFCore.CMFCorePermissions import ListFolderContents
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import AddPortalContent
from AccessControl.Permissions import copy_or_move
from AccessControl.Permissions import delete_objects

from AccessControl import getSecurityManager
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone import transaction


class TestDisplayContentsTab(PloneTestCase.PloneTestCase):
    '''For the contents tab to display a user must have the ListFolderContents,
       and one of the (Modify portal contents, Copy or move, Add portal contents,
       Delete objects) permissions either on the object itself, or on the
       parent object if the object is not folderish or is the default page for
       its parent.
    '''

    def afterSetUp(self):
        self.parent = self.folder.aq_parent
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.foo.invokeFactory('Document', id='doc1')
        self.folder.foo.invokeFactory('Folder', id='folder1')
        folder_path = '/'.join(self.folder.foo.folder1.getPhysicalPath())
        transaction.commit(1) # make rename work
        # Make the folder the default page
        self.folder.folder_rename(paths=[folder_path], new_ids=['index_html'], new_titles=['Default Folderish Document'])

    def getModificationPermissions(self):
        return [ModifyPortalContent,
                AddPortalContent,
                copy_or_move,
                delete_objects]

    def removePermissionsFromObject(self, permissions, object):
        for permission in permissions:
            object.manage_permission(permission, ['Manager'], acquire=0)

    def testDisplayContentsTab(self):
        # We should see the tab
        self.failUnless(self.folder.displayContentsTab())

    def testAnonymous(self):
        # Anonymous should not see the tab
        self.logout()
        self.failIf(self.folder.displayContentsTab())

    def testNoListPermission(self):
        # We should not see the tab without ListFolderContents
        self.folder.manage_permission(ListFolderContents, ['Manager'], acquire=0)
        self.failIf(self.folder.displayContentsTab())

    def testNoModificationPermissions(self):
        # We should see the tab with only copy_or_move
        perms = self.getModificationPermissions()
        self.removePermissionsFromObject(perms, self.folder)
        self.failIf(self.folder.displayContentsTab())

    def testOnlyModifyPermission(self):
        # We should see the tab with only ModifyPortalContent
        perms = self.getModificationPermissions()
        perms.remove(ModifyPortalContent)
        self.removePermissionsFromObject(perms, self.folder)
        self.failUnless(self.folder.displayContentsTab())

    def testOnlyCopyPermission(self):
        # We should see the tab with only copy_or_move
        perms = self.getModificationPermissions()
        perms.remove(copy_or_move)
        self.removePermissionsFromObject(perms, self.folder)
        self.failUnless(self.folder.displayContentsTab())

    def testOnlyDeletePermission(self):
        # We should see the tab with only copy_or_move
        perms = self.getModificationPermissions()
        perms.remove(delete_objects)
        self.removePermissionsFromObject(perms, self.folder)
        self.failUnless(self.folder.displayContentsTab())

    def testOnlyAddPermission(self):
        # We should see the tab with only copy_or_move
        perms = self.getModificationPermissions()
        perms.remove(AddPortalContent)
        self.removePermissionsFromObject(perms, self.folder)
        self.failUnless(self.folder.displayContentsTab())

    def testNonFolderishObjectDoesNotShowTab(self):
        # The availability of the contents tab on a non-folderish object should be
        # based on the parents permissions.
        doc = self.folder.foo.doc1
        self.failIf(doc.displayContentsTab())

    def testFolderishDefaultPageUsesParentPermissions(self):
        # The availability of the contents tab on a default page should be
        # based on the parents permissions, whether the default page is
        # folderish or not.
        def_page = self.folder.foo.index_html
        self.failUnless(def_page.displayContentsTab())
        self.folder.foo.manage_permission(ListFolderContents, ['Manager'], acquire=0)
        self.failIf(def_page.displayContentsTab())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDisplayContentsTab))
    return suite

if __name__ == '__main__':
    framework()
