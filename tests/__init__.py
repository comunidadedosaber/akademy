
#try:
#    from trytond.modules.akademy.tests.test_configuration import suite
#    from trytond.modules.akademy.tests.test_matriculation import suite
#    from trytond.modules.akademy.tests.test_classes import suite
#    from trytond.modules.akademy.tests.test_avaliation import suite
#except ImportError:
from .test_configuration import suite
from .test_matriculation import suite
from .test_classes import suite
from .test_avaliation import suite


__all__ = ['suite']