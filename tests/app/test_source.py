# -*- coding: utf-8 -*-
from app.source import Source

def test_source_create():
    s = Source()
    s.name = "test_source"
    assert s.name == "test_source"
