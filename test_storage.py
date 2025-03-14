#!/usr/bin/env python
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

try:
    path = default_storage.save('test.txt', ContentFile(b'test content'))
    print('File saved successfully at:', path)
except Exception as e:
    print('Error saving file:', e)
