"""The brain's map as its sessions load it — CLAUDE.md, the rule files and the four skills: each
skill named as its folder and its brief last, the handbook read first, the format skill cited by
its name, pilot.py's verbs as its parser has them, and every path the map cites in place."""

import importlib.util
import json
import os
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
CLAUDE = ROOT / "CLAUDE.md"
SKILL_NAMES = {"create", "chat", "pre-rule", "plan"}
FORMAT_SKILL = "/dev:document-format"
BRIEF = "## The brief\n\n$ARGUMENTS"
# A project's folder in the store's tree (PilotApp's docs/projection.md), with chat.md, and the
# tree root's reference.json: the map cites them relative to the folder, never this repo.
TREE_FILES = {
    "project.md",
    "handbook.md",
    "plan.json",
    "timeline.json",
    "chat.md",
    "reference.json",
}
TREE_FOLDERS = ("items/", "inbox/", "attachments/")
PATH_LIKE = re.compile(r"[^\s/]*(/[^\s/]*)*(\.(md|py|json|yaml|toml)|/)")
NOT_IN_REPO = {".git", ".venv", "__pycache__", ".ruff_cache"}


def skill_file(name: str) -> Path:
    return SKILLS / name / "SKILL.md"


def the_map() -> dict[str, str]:
    files = [CLAUDE, *sorted((ROOT / "rules").glob("*.md"))]
    files += [skill_file(name) for name in sorted(SKILL_NAMES)]
    return {str(path.relative_to(ROOT)): path.read_text() for path in files}


def front_matter(text: str) -> tuple[dict, str]:
    head, separator, body = text.removeprefix("---\n").partition("\n---\n")
    if not text.startswith("---\n") or not separator:
        raise AssertionError("no front matter")
    return yaml.safe_load(head), body


def cited_paths(text: str) -> list[str]:
    """Every path-like word of the text's code spans: a file name with an extension, or a
    folder ending in a slash."""
    words = (word for span in re.findall(r"`([^`]+)`", text) for word in span.split())
    return [word for word in words if PATH_LIKE.fullmatch(word)]


def repo_names() -> set[str]:
    names: set[str] = set()
    for _, folders, files in os.walk(ROOT):
        folders[:] = [folder for folder in folders if folder not in NOT_IN_REPO]
        names.update(files)
    return names


def is_there(path: str, names: set[str]) -> bool:
    """A cited path is a file or a folder of a project's folder, absolute and so outside this
    repo, a file name this repo holds somewhere, or a path from its root, `<…>` any one name."""
    if path.startswith("/") or path in TREE_FILES or path.startswith(TREE_FOLDERS):
        return True
    if "/" not in path.rstrip("/"):
        return path in names or (ROOT / path).is_dir()
    return any(ROOT.glob(re.sub(r"<[^>]*>", "*", path.rstrip("/"))))


def first_step(body: str) -> str:
    match = re.search(r"^1\. (.+?)(?=\n\S|\n\n|\Z)", body, re.MULTILINE | re.DOTALL)
    if match is None:
        raise AssertionError("no numbered step")
    return match.group(1)


def pilot_verbs() -> dict[str, str]:
    spec = importlib.util.spec_from_file_location("pilot", ROOT / "tools" / "pilot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {leaf.prog: leaf.description for leaf in module._leaves(module.build_parser())}


class SkillsTest(unittest.TestCase):
    def test_the_four_skills_are_there_and_no_other(self) -> None:
        self.assertEqual({path.parent.name for path in SKILLS.glob("*/SKILL.md")}, SKILL_NAMES)

    def test_each_skill_is_named_as_its_folder_and_says_when_it_runs(self) -> None:
        for name in SKILL_NAMES:
            with self.subTest(name):
                meta, _ = front_matter(skill_file(name).read_text())
                self.assertEqual(meta["name"], name)
                self.assertIn(f"/{name}", meta["description"])

    def test_the_brief_is_last_under_its_heading(self) -> None:
        for name in SKILL_NAMES:
            with self.subTest(name):
                text = skill_file(name).read_text()
                self.assertTrue(text.endswith(BRIEF + "\n"))
                self.assertEqual(text.count("## The brief"), 1)
                self.assertEqual(text.count("$ARGUMENTS"), 1)

    def test_every_skill_but_create_reads_the_handbook_first(self) -> None:
        for name in SKILL_NAMES - {"create"}:
            with self.subTest(name):
                _, body = front_matter(skill_file(name).read_text())
                self.assertIn("`handbook.md`", first_step(body))

    def test_claude_md_names_every_skill_by_its_command(self) -> None:
        text = CLAUDE.read_text()
        for name in SKILL_NAMES:
            with self.subTest(name):
                self.assertIn(f"`/{name}`", text)


class CitationsTest(unittest.TestCase):
    def test_claude_md_and_every_skill_cite_the_format_skill_by_its_name(self) -> None:
        for path in [CLAUDE, *(skill_file(name) for name in SKILL_NAMES)]:
            with self.subTest(path.relative_to(ROOT)):
                text = path.read_text()
                self.assertIn(f"`{FORMAT_SKILL}`", text)
                self.assertEqual(set(re.findall(r"/[\w:-]*format\b", text)), {FORMAT_SKILL})

    def test_every_path_the_map_cites_is_there(self) -> None:
        names = repo_names()
        for source, text in the_map().items():
            for path in cited_paths(text):
                with self.subTest(source=source, path=path):
                    self.assertTrue(is_there(path, names))

    def test_claude_md_gives_every_verb_of_pilot_py_its_one_line(self) -> None:
        text = " ".join(CLAUDE.read_text().split())
        verbs = pilot_verbs()
        for verb, description in verbs.items():
            with self.subTest(verb):
                self.assertIn(f"`{verb}`: {description}", text)
        named = set(re.findall(r"`(pilot\.py [a-z ]+)`:", text))
        self.assertEqual(named, set(verbs))

    def test_the_grants_name_every_confirmation_reason_by_its_code(self) -> None:
        reference = json.loads(
            (ROOT / "tests" / "fixtures" / "tree" / "reference.json").read_text()
        )
        grants = (ROOT / "rules" / "grants.md").read_text()
        for reason in reference["confirmation_reasons"]:
            with self.subTest(reason["code"]):
                self.assertIn(f"`{reason['code']}`", grants)


class PathCheckTest(unittest.TestCase):
    """The citation check itself: what it takes for a path, and what it refuses."""

    def test_a_path_is_a_file_name_or_a_folder(self) -> None:
        self.assertEqual(
            cited_paths(
                "`rules/grants.md`, `cexec python uv run tools/pilot.py <verb> …`, `items/`,"
                " `owner/Name`, `--project`, `$PILOT_PROJECT`, `<environment>:<path>`"
            ),
            ["rules/grants.md", "tools/pilot.py", "items/"],
        )

    def test_a_path_is_there_in_the_repo_or_the_project_folder(self) -> None:
        names = repo_names()
        for path in (
            "rules/grants.md",
            ".claude/skills/<name>/SKILL.md",
            "tools/",
            "pilot.py",
            "handbook.md",
            "items/<seq>-<slug>.md",
            "/work/Projects/reference.json",
        ):
            with self.subTest(path):
                self.assertTrue(is_there(path, names))

    def test_a_path_missing_from_both_is_not(self) -> None:
        names = repo_names()
        for path in ("rule/grants.md", ".claude/skill/<name>/SKILL.md", "handbok.md", "tool/"):
            with self.subTest(path):
                self.assertFalse(is_there(path, names))
