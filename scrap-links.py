# Copyright 2022 Mohammad Mohamamdi. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import re
import sqlite3
from typing import Any, List
from urllib.parse import urljoin, urlparse

import mechanicalsoup
import pandas as pd
from tqdm import tqdm

url = "http://codeforces.com/problemset"


def get_links(
    page: str, browser: mechanicalsoup.StatefulBrowser, base_url: str
) -> List[Any]:
    browser.open(urljoin(base_url, page))
    table = browser.page.select(".problems")[0]
    problems = table.find_all("tr")
    out = []
    for i in range(1, len(problems)):
        data = problems[i].find_all("td")[0:2]
        ida = data[0].a["href"]
        difficulty = urlparse(ida).path.rpartition("/")[2]
        if not difficulty.isalpha():
            continue
        name = data[1].select("div:nth-child(1)")[0]
        tags = [tag.text for tag in data[1].select("div:nth-child(2)")[0].find_all("a")]
        out.append(
            {
                "link": urljoin(base_url, ida),
                "difficulty": difficulty[0],
                "name": name.a.text.strip(),
                "tags": tags,
            }
        )
    return out


def main():
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(url)
    next_page_anchor = browser.page.find("a", text="→")
    last_page_url = next_page_anchor.parent.parent.select("li:nth-last-child(2)")[
        0
    ].span.a["href"]
    last_page = urljoin(url, last_page_url)
    pattern = r".+/(\d+)$"
    lp = int(re.search(pattern, last_page).groups(1)[0])
    base_url = urljoin(last_page, ".")
    scraped = []
    for i in tqdm(range(1, lp + 1)):
        scraped.append(get_links(f"{i}", browser, base_url))

    df = pd.DataFrame(columns=["name", "difficulty", "link", "tags"])
    for page in scraped:
        links = pd.DataFrame(page, columns=["name", "difficulty", "link", "tags"])
        links["tags"] = links["tags"].apply(
            lambda r: [re.sub(r"[^A-Za-z0-9 ]+", "", s).replace(" ", "_") for s in r]
        )
        df = df.append(links)

    df["contest"] = df.apply(
        lambda r: urlparse(r.link).path.rpartition("/")[0].rpartition("/")[2], axis=1
    )
    df.to_csv("links.csv", index=False)
    dft = df.join(pd.get_dummies(df["tags"].apply(pd.Series).stack()).sum(level=0))
    dft.drop("tags", axis=1, inplace=True)
    dft = dft.convert_dtypes(convert_floating=True)

    conn = sqlite3.connect("./links.sqlite3")
    dft.to_sql("codeforces", conn, if_exists="replace")
    conn.commit()

    tags = dft.columns.tolist()[3:]
    pd.DataFrame(tags, columns=["tags"]).to_sql("tags", conn, if_exists="replace")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
