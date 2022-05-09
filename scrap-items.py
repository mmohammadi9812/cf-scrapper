# Copyright 2022 Mohammad Mohamamdi. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file

import logging
import mechanicalsoup
import multiprocessing
import numpy as np
import re
import sqlite3
import pandas as pd
import tqdm

from bs4 import Tag
from joblib import Parallel, delayed
from pathlib import Path

def scrap_basic_sections(problem_statement: Tag, name: str):
  out = {}
  sections = ["time-limit", "memory-limit", "input-file", "output-file"]
  for section in sections:
    try:
      out[section.replace("-", "_")] = problem_statement.find("div", class_=section).text.strip()
    except Exception as _:
      logging.warning(f"{name} has no {section.replace('-', ' ')}")
      out[section.replace("-", "_")] = "N/A"
  return out

def scrap_specifications(problem_statement: Tag, name: str):
  out = {}
  specifications = ["input-specification", "output-specification"]
  for spec in specifications:
    try:
      io_spec = problem_statement.find("div", class_=spec)
      io_spec.find("div", class_="section-title").decompose()
      out[spec.replace("-", "_")] = io_spec.prettify()
    except Exception as _:
      logging.warning(f"{name} has no {spec.replace('-', ' ')}")
      out[spec.replace("-", "_")] = "N/A"
  return out

def scrap_examples(problem_statement: Tag, name: str):
  out = {}
  try:
      sample_tests_div = problem_statement.find("div", class_="sample-tests")
      (title.decompose() for title in sample_tests_div.find_all("div", class_="section-title"))
      sample_tests = zip(sample_tests_div.find_all("div", class_="input"), sample_tests_div.find_all("div", class_="output"))
      for i in range(len(sample_tests)):
          sample_tests[i] = (sample_tests[i][0].text, sample_tests[i][1].text)
      out["sample_tests"] = sample_tests
  except Exception as _:
      logging.warning(f"{name} has no sample tests")
      out["sample_tests"] = []
  return out

def scrap_description(problem_statement: Tag, name: str):
  out = {}
  try:
      out["description"] = problem_statement.find("div", class_="header").next_sibling.text
  except Exception as _:
      logging.warning(f"{name} has no description")
      out["description"] = "N/A"
  return out

def scrap_notes(problem_statement: Tag, name: str):
  out = {}
  try:
      out["notes"] = problem_statement.find("div", class_="note").prettify()
  except Exception as _:
      logging.warning(f"{name} has no notes")
      out["notes"] = "N/A"
  return out


def scrap(row: pd.Series, browser: mechanicalsoup.StatefulBrowser):
    out = {
      "name": row["name"],
      "url": row["url"],
      "difficulty": row["difficulty"],
      "tags": row["tags"].split(","),
      "contest": row["contestId"],
    }
    browser.open(row["url"])
    page = browser.get_current_page()
    ps = page.find("div", class_="problem-statement")

    out |= scrap_basic_sections(ps, row["name"])
    out |= scrap_specifications(ps, row["name"])
    out |= scrap_examples(ps, row["name"])
    out |= scrap_description(ps, row["name"])
    out |= scrap_notes(ps, row["name"])

    return out


def scrap_chunk(chunk: pd.DataFrame, browser: mechanicalsoup.StatefulBrowser):
    df = pd.DataFrame()

    for row in tqdm.tqdm(chunk.itertuples(), total=len(chunk)):
        try:
            df = df.append(scrap(row, browser))
        except:
            logging.warning(f"Failed to scrap {row.name}")
            continue
    return df

def filter_df(df: pd.DataFrame):
  df = df[df["description"] != "N/A"]
  df = df[(~df["memory_limit"].str.contains("мегабайт"))]
  df["memory_limit"] = df["memory_limit"].apply(lambda r: int(re.search(r"^(\d+)", r).group(1)) * 1024 * 1024)
  df["time_limit"] = df["time_limit"].apply(lambda r: int(re.search(r"^(\d+)", r).group(1)))
  return df


def main():
  if not Path("problems.db").exists():
    raise FileNotFoundError("problems database not found")
  if Path("details.pkl").exists():
    return

  user_agent = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:62.0) Gecko/20100101 Firefox/49.0"
  browser = mechanicalsoup.StatefulBrowser(user_agent=user_agent)
  num_cores = max(multiprocessing.cpu_count(), 5)

  with sqlite3.connect("problems.db") as conn:
    df = pd.read_sql_query("SELECT * FROM problems", conn)
    chunks = np.array_split(df, num_cores)

    parallel = Parallel(n_jobs=num_cores, prefer="threads", verbose=2)
    results = parallel(delayed(scrap_chunk)(chunk, browser) for chunk in chunks)
    df = filter_df(pd.concat(results))

    df.to_pickle("details.pkl")


if __name__ == "__main__":
  main()
