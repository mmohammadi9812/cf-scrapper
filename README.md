## Why
After being rejected in a couple of interviews, I though lacking in algorithms' problems is hurting my career

So I thought maybe it's a good idea to get back to solving `codeforces`' problems

but the problem was that I had to be on my online laptop to think about problems

My initial motivation for scrapping `codeforces` problems was to use them as source for a telegram bot (definitely more a11y)

The telegram bot is out of scope for this repository, but I quite liked scrapping more than *6000* pages of problems •ᴗ•

## Structure
The two main files are:  
+ `scrap-links.ipynb`: it scraps links and tags from `codeforces.com/problemset/`
+ `scrap-items.ipynb`: it uses links from `links.sqlite3` file, created by `scrap-links.ipynb`, to scrap pages

*NOTE*: there is a limit of 5 requests per second for site

change the `num_cores` (in `scrap-items.ipynb` file) to 5 if you're using a CPU with more than 5 physical cores

otherwise, your ip might gets banned (temporarily)


## Running
You need pipenv to install dependencies:
```bash
pip install pipenv
```

after cloning this repository, install dependencies with `pipenv`:
```bash
pipenv install --dev
```
run jupyter to access notebooks:
```bash
pipenv shell
jupyter notebook
```

first, open `scrap-links.ipynb`, run all cells  
then open `scrap-items.ipynb` and run all cells  

## LICENSE
This repository is licensed under `cc by-nc-sa 4.0`, you can find full text in `license.txt`