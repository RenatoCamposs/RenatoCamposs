"""Atualiza as linhas de stats do README mantendo o alinhamento do painel."""
import os
import re
import requests

USER = os.environ["GH_USER"]
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

LEFT_W = 58   # largura da arte ASCII + espaçamento
PANEL_W = 54  # largura do painel da direita


def leader(key: str, value: str) -> str:
    base = f"\u00b7 {key}: "
    space = PANEL_W - len(base) - len(value) - 1
    if space < 1:
        return base + value
    return base + "." * space + " " + value


def get_stats() -> dict:
    u = requests.get(f"https://api.github.com/users/{USER}", headers=HEADERS).json()
    repos_count = u.get("public_repos", 0)
    followers = u.get("followers", 0)

    stars = 0
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}",
            headers=HEADERS,
        ).json()
        if not isinstance(r, list) or not r:
            break
        stars += sum(x.get("stargazers_count", 0) for x in r)
        if len(r) < 100:
            break
        page += 1

    c = requests.get(
        f"https://api.github.com/search/commits?q=author:{USER}",
        headers=HEADERS,
    ).json()
    commits = c.get("total_count", 0)

    return {
        "repos": repos_count,
        "stars": stars,
        "commits": commits,
        "followers": followers,
    }


def replace_panel(line: str, new_panel: str) -> str:
    left = line[:LEFT_W].ljust(LEFT_W)
    return (left + new_panel).rstrip()


def main() -> None:
    s = get_stats()
    lines = open("README.md", encoding="utf-8").read().split("\n")

    out = []
    for line in lines:
        if "\u00b7 Repos:" in line:
            panel = leader("Repos", f"{s['repos']} | Stars: {s['stars']}")
            out.append(replace_panel(line, panel))
        elif "\u00b7 Commits:" in line:
            panel = leader("Commits", f"{s['commits']:,} | Followers: {s['followers']}")
            out.append(replace_panel(line, panel))
        elif re.search(r"\S+@github \u2500+", line):
            header = f"{USER}@github " + "\u2500" * (PANEL_W - len(USER) - 8)
            out.append(replace_panel(line, header))
        else:
            out.append(line)

    open("README.md", "w", encoding="utf-8").write("\n".join(out))
    print(f"ok: {s}")


if __name__ == "__main__":
    main()
