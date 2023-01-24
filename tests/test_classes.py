import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase

class ClassesTestCase(ModuleTestCase):
    'Test classes module'
    module = 'akademy'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        ClassesTestCase))
    return suite