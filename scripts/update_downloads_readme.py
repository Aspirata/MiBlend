"""Update the release download leaderboard in the project README files."""

import json
import os
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen as open_url


MEDALS = ("🥇", "🥈", "🥉")
START_MARKER = "<!-- release-downloads:start -->"
END_MARKER = "<!-- release-downloads:end -->"
RELEASES_URL = "https://api.github.com/repos/Aspirata/MiBlend/releases?per_page=100"


def fetch_releases(urlopen=open_url):
    """Fetch public release metadata from the GitHub REST API."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MiBlend-download-leaderboard",
        "X-GitHub-Api-Version": "2026-03-10",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(RELEASES_URL, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def _format_date(value, language):
    published = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if language == "ru":
        return published.strftime("%d.%m.%Y")
    return published.strftime("%b %d, %Y").replace(" 0", " ")


def _format_downloads(value, language):
    separator = " " if language == "ru" else ","
    return f"{value:,}".replace(",", separator)


def render_leaderboard(releases, language="en", limit=10):
    """Render the most-downloaded release assets as a Markdown table."""
    rows = []
    for release in releases:
        downloads = sum(asset.get("download_count", 0) for asset in release["assets"])
        if downloads:
            rows.append((downloads, release))
    rows.sort(key=lambda item: item[0], reverse=True)

    if language == "ru":
        lines = [
            "### Рейтинг скачиваний",
            "",
            "Небольшой рейтинг ради интереса по числу скачиваний файлов в [GitHub Releases]"
            "(https://github.com/Aspirata/MiBlend/releases).",
            "",
            "| Место | Версия | Тип | Дата релиза | Скачивания |",
            "| :---: | --- | --- | :---: | ---: |",
        ]
        stable_label = "✅ Стабильная"
        prerelease_label = "🧪 Предрелиз"
        footer = (
            "_Обновляется автоматически примерно раз в полторы недели "
            "по данным GitHub Releases._"
        )
    else:
        lines = [
            "### Download leaderboard",
            "",
            "A small just-for-fun ranking based on asset downloads from [GitHub Releases]"
            "(https://github.com/Aspirata/MiBlend/releases).",
            "",
            "| Rank | Version | Type | Release date | Downloads |",
            "| :---: | --- | --- | :---: | ---: |",
        ]
        stable_label = "✅ Stable"
        prerelease_label = "🧪 Pre-release"
        footer = (
            "_Updated automatically about every week and a half "
            "from GitHub Releases._"
        )

    for index, (downloads, release) in enumerate(rows[:limit], start=1):
        rank = MEDALS[index - 1] if index <= len(MEDALS) else str(index)
        name = (release.get("name") or release["tag_name"]).replace("|", "·")
        release_type = prerelease_label if release["prerelease"] else stable_label
        published = _format_date(release["published_at"], language)
        formatted_downloads = _format_downloads(downloads, language)
        lines.append(
            f"| {rank} | [{name}]({release['html_url']}) | {release_type} | "
            f"{published} | **{formatted_downloads}** |"
        )

    lines.extend(("", footer))
    return "\n".join(lines)


def replace_section(readme, section):
    """Replace only the generated leaderboard section in a README string."""
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise ValueError("README download leaderboard markers are missing or invalid")

    content_start = start + len(START_MARKER)
    return readme[:content_start] + "\n" + section + "\n" + readme[end:]


def update_readme_file(path, releases, language):
    """Update one README and return whether its contents changed."""
    path = Path(path)
    original = path.read_text(encoding="utf-8")
    updated = replace_section(original, render_leaderboard(releases, language=language))
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main(repository_root=None, fetcher=fetch_releases):
    """Refresh both localized README leaderboards and return the change count."""
    repository_root = Path(repository_root or Path(__file__).resolve().parents[1])
    releases = fetcher()
    targets = (
        (repository_root / "docs" / "README.md", "en"),
        (repository_root / "docs" / "README_ru.md", "ru"),
    )
    return sum(
        update_readme_file(path, releases, language)
        for path, language in targets
    )


if __name__ == "__main__":
    changes = main()
    print(f"Updated {changes} README file(s).")
