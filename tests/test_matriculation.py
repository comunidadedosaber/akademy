import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase

class MatriculationTestCase(ModuleTestCase):
    'Test matriculation module'
    module = 'akademy'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        MatriculationTestCase))
    return suite