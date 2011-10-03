"""
PEP 8 style enforcement shim.

This module hooks the PEP 8 style validator into our unit test framework. We
use the unit test framework, rather than a commit hook, to keep all of our
validation in one place.
"""
import os
from unittest import TestLoader, TestSuite

from django.test import TestCase
import pep8

from rainbeard import common


class PEP8ValidatorTestcase(TestCase):

    def test_style(self):
        """
        Runs the rainbeard code through pep8.py.

        This is a bit sketchy, since pep8.py is desiged to be run as a
        command-line utility, and doesn't seem to have given much thought to
        programatic users. Still, it works well enough that we can use it
        without resorting to shell hackery.
        """

        # Output a blank line, so that any output of pep8 starts on its own
        # line. This breaks up the dots in the Django test suite harness, but
        # it's not that big of a deal.
        print ""

        # Get the top-level Rainbeard directory by examining common.py.
        srcdir = os.path.dirname(common.__file__)

        # Process the 'options'. This is necessary to define some internal
        # variables, even though there are no options to pass. As far as I can
        # tell, the worst thing that happens here is that options.prog is set
        # to sys.argv[0], which isn't helpful in this context. But that
        # variable is never actually examined within pep8.py, so we're probably
        # ok.
        pep8.process_options()

        # Run the validator on all python files in the top-level Rainbeard
        # directory and all subdirectories.
        pep8.input_dir(srcdir)

        # We should have zero errors
        self.assertEqual(pep8.get_count(), 0)


def suite():
    return TestLoader().loadTestsFromTestCase(PEP8ValidatorTestcase)
