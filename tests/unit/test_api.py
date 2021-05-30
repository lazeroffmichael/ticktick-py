"""
Module for testing api.py
"""

import pytest
import httpx
import uuid
import os

from ticktick.api import TickTickClient
from unittest.mock import patch

class TestInitMethod:

    def test_init_class_members_set(self):
        """
        Tests all class members are set in the init method
        """


class TestDeleteFromLocalState:
    pass