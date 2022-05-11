# Copyright 2022 Mohammad Mohamamdi. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from pathlib import Path
from .links import fetch_links
from .items import fetch_problems

def main():
  if not Path('problems.db').exists():
    fetch_links()
  if not Path('details.pkl').exists():
    fetch_problems()

if __name__ == '__main__':
  main()
