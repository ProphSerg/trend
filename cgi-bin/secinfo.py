#!/usr/bin/env python3

import requests
import json
from urllib.parse import parse_qs
import os

parse = parse_qs(os.getenv('QUERY_STRING'))
print()
print(parse)