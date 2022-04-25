# Code-forces Scraper
---

## Structure
The two main files are:
+ `scrap-links.ipynb`: it scraps links and tags from `codeforces.com/problemset/`
+ `scrap-items.ipynb`: it uses links from `links.sqlite3` file, created by `scrap-links.ipynb`, to scrap pages

*NOTE*: there is a limit of 5 requests per second for site

change the `num_cores` (in `scrap-items.ipynb` file) to 5 if you're using a CPU with more than 5 physical cores

otherwise, your ip might gets banned (temporarily)


## Running
use `pipenv` to install dependencies

then, run `jupyter notebook scrap-links.ipynb`

then, run `jupyter notebook scrap-items.ipynb`

you can run these files with custom virtualenv or system python but it's not recommended
## LICENSE
 Copyright 2022 Mohammad Mohamamdi. All rights reserved.
 Use of this source code is governed by a BSD-style
 license that can be found in the LICENSE file.
