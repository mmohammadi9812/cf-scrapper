# Copyright 2022 Mohammad Mohamamdi. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
import sqlite3
import requests

API_ADDRESS = "https://codeforces.com/api/problemset.problems"

def fetch_links():
  r = requests.get(API_ADDRESS)
  r.raise_for_status()
  data = r.json()
  if data["status"] != "OK":
      raise Exception(f"{data['status']}")

  conn = sqlite3.connect("problems.db")
  conn.execute("DROP TABLE IF EXISTS problems")
  conn.execute(
      """
  CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    contestId INTEGER,
    name TEXT,
    tags TEXT,
    difficulty TEXT,
    link TEXT
  )
  """
  )

  for problem in data["result"]["problems"]:
      url = f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
      conn.execute(
          "INSERT INTO problems (contestId, name, tags, difficulty, link) VALUES (?, ?, ?, ?, ?)",
          (
              problem["contestId"],
              problem["name"],
              ",".join(problem["tags"]),
              problem["index"],
              url,
          ),
      )
  conn.commit()
  conn.close()


if __name__ == "__main__":
  fetch_links()
