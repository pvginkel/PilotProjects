"""The brain's map as its sessions load it — CLAUDE.md, the rule files and the four skills: each
skill named as its folder and its brief last, the handbook read first, the format skill cited by
its name, pilot.py's verbs as its parser has them, every pilot.py command line it quotes one the
parser takes, every path the map cites in place, the chat skill and the create skill reading a
person's message as PilotApp's server sends it, the create skill naming a draft's ask and its
material as pilot-store takes them, and the plan skill's setup reading the draft's sections the
create skill writes."""

import importlib.util
import itertools
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
# A fenced block, its fences included: no code span, and its backticks would shift the pairing.
FENCED = re.compile(r"^[ \t]*```.*?^[ \t]*```[^\n]*$", re.MULTILINE | re.DOTALL)
# A person's message as PilotApp's server sends it to the chat (its ChatService and BriefService):
# the line naming its author, a quote's three tags, and the paths a quote by path names.
NAMING_LINE = '"The message, from <handle> (member|not a member):"'
QUOTE_TAGS = (
    '`<quoted_item id="<item id>">…</quoted_item id="<item id>">`',
    '`<quoted_block id="<item id>/<local id>">…</quoted_block id="<item id>/<local id>">`',
    '`<quoted_path path="<path>">…</quoted_path path="<path>">`',
)
QUOTED_PATHS = ("`handbook.md`", "`project.md`", "`attachments/<batch>/<filename>`")
# The server names a message's author only when the message before was another person's, so the
# chat skill takes a message without the line, and a ruling's `for`, from the latest such line.
LATEST_NAMING = (
    "A message without that line is from the person the latest such line named, the brief's"
    " included.",
    f"`for` their handle, as the latest line {NAMING_LINE} names them",
)
# In a draft's definition chat the server's quotes are of the draft alone — an ask of it by
# `project.md/<local id>`, the id pilot-store's `answer` takes for it, or a file by its path — and
# its brief names the person who started the draft, the first message's author unless the line
# names another.
DRAFT_QUOTE_TAGS = (
    '`<quoted_block id="project.md/<local id>">…</quoted_block id="project.md/<local id>">`',
    '`<quoted_path path="<path>">…</quoted_path path="<path>">`',
)
DRAFT_QUOTED_PATHS = ("`project.md`", "`attachments/<batch>/<filename>`")
DRAFT_LATEST_NAMING = (
    "A message without that line is from the person the latest such line named, the brief's"
    " included, and with none so far from the person who started the draft.",
    "`for` their handle, as step 4 names them",
)
# pilot-store's `answer` on a draft's ask and `attach_file` hung on nothing (PilotApp's
# pilot_mcp/tools.py), and the one link the Draft tab opens, relative to the draft's folder.
DRAFT_CALLS = (
    "`answer` with `block` `project.md/<local id>`",
    "`attach_file`: `source` `<environment>:<path>`",
    "and no `to`, so that it hangs on nothing until Create project hangs it on the opening",
    "`[words](attachments/<batch>/<filename>)`, relative to the draft's folder",
)
# What the create skill never does: Create project is the operator's.
CREATE_IS_THE_OPERATORS = (
    "**Create project is the operator's**: never ask for it, and never say the draft is"
    ' "ready".'
)
# The draft's sections the create skill writes and the plan skill's setup reads.
DRAFT_SECTIONS = ("`## The plan`", "`## Rules`", "`## Context`")
SETUP_KIND = "`Pilot's brief · the setup · …`"


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


def code_spans(text: str) -> list[str]:
    return re.findall(r"`([^`]+)`", FENCED.sub("", text))


def cited_paths(text: str) -> list[str]:
    """Every path-like word of the text's code spans, outside its fenced blocks: a file name
    with an extension, or a folder ending in a slash."""
    words = (word for span in code_spans(text) for word in span.split())
    return [word for word in words if PATH_LIKE.fullmatch(word)]


def quoted_commands(text: str) -> list[str]:
    """Every code span of the text, outside its fenced blocks, that is a pilot.py command line."""
    return [span for span in code_spans(text) if span.startswith("pilot.py ")]


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


def pilot_module():
    spec = importlib.util.spec_from_file_location("pilot", ROOT / "tools" / "pilot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pilot_verbs() -> dict[str, str]:
    module = pilot_module()
    return {leaf.prog: leaf.description for leaf in module._leaves(module.build_parser())}


def pilot_options() -> dict[str, set[str]]:
    """The options each verb's parser takes, by its prog, and the script's own, `pilot.py`'s."""
    module = pilot_module()
    root = module.build_parser()
    parsers = [root, *module._leaves(root)]
    return {parser.prog: set(parser._option_string_actions) for parser in parsers}


def command_fault(command: str, options: dict[str, set[str]]) -> str | None:
    """Why a quoted pilot.py command line is not one its parser takes — a word after the
    script's name that is no verb of it, or an option its verb does not have; None for one it
    takes. A word after the verb is an option, `--…`, or a placeholder, `<…>`."""
    words = command.split()
    verb = max((prog for prog in options if words[: len(prog.split())] == prog.split()), key=len)
    rest = words[len(verb.split()) :]
    named = list(itertools.takewhile(lambda word: not word.startswith(("-", "<")), rest))
    if named:
        return f"`{verb}` has no verb `{' '.join(named)}`"
    unknown = [word for word in rest if word.startswith("--") and word not in options[verb]]
    return f"`{verb}` takes no {', '.join(unknown)}" if unknown else None


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


class ChatSkillTest(unittest.TestCase):
    def test_the_chat_skill_reads_the_naming_line_and_every_quote_tag(self) -> None:
        text = " ".join(skill_file("chat").read_text().split())
        for form in (NAMING_LINE, *QUOTE_TAGS, *QUOTED_PATHS):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_chat_skill_takes_for_from_the_latest_naming_line(self) -> None:
        text = " ".join(skill_file("chat").read_text().split())
        for rule in LATEST_NAMING:
            with self.subTest(rule):
                self.assertIn(rule, text)


class CreateSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = " ".join(skill_file("create").read_text().split())

    def test_the_create_skill_reads_the_naming_line_and_the_draft_s_quote_tags(self) -> None:
        for form in (NAMING_LINE, *DRAFT_QUOTE_TAGS, *DRAFT_QUOTED_PATHS):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_create_skill_takes_for_from_the_latest_naming_line_or_the_starter(self) -> None:
        for rule in DRAFT_LATEST_NAMING:
            with self.subTest(rule):
                self.assertIn(rule, self.text)

    def test_the_create_skill_answers_and_attaches_as_pilot_store_takes_a_draft_s(self) -> None:
        for call in DRAFT_CALLS:
            with self.subTest(call):
                self.assertIn(call, self.text)

    def test_the_create_skill_leaves_create_project_to_the_operator(self) -> None:
        self.assertIn(CREATE_IS_THE_OPERATORS, self.text)


class PlanSkillTest(unittest.TestCase):
    def test_the_plan_skill_names_the_setup_by_its_kind_line(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        self.assertIn(SETUP_KIND, text)
        self.assertIn("## The setup", text)

    def test_the_setup_reads_the_sections_the_create_skill_writes(self) -> None:
        for name in ("create", "plan"):
            text = skill_file(name).read_text()
            for section in DRAFT_SECTIONS:
                with self.subTest(skill=name, section=section):
                    self.assertIn(section, text)


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

    def test_every_pilot_py_command_the_map_quotes_is_one_its_parser_takes(self) -> None:
        options = pilot_options()
        for source, text in the_map().items():
            for command in quoted_commands(text):
                with self.subTest(source=source, command=command):
                    self.assertIsNone(command_fault(command, options))

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

    def test_a_fenced_block_is_taken_out_before_the_code_spans(self) -> None:
        self.assertEqual(
            cited_paths(
                "```text\ncexec python uv run tools/pilot.py answer <file> <block>\n```\n\n"
                "Read `rules/nothere.md`, then `rules/grants.md`.\n"
            ),
            ["rules/nothere.md", "rules/grants.md"],
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


class CommandCheckTest(unittest.TestCase):
    """The command check itself: what it takes for a pilot.py command line, and what it refuses."""

    def test_a_command_is_a_code_span_that_opens_with_the_script(self) -> None:
        self.assertEqual(
            quoted_commands(
                "```text\npilot.py plan note strike n1\n```\n\n"
                "Run `pilot.py plan note strike <id>`, not `cexec python uv run tools/pilot.py"
                " <verb> …` or `pilot.py`."
            ),
            ["pilot.py plan note strike <id>"],
        )

    def test_a_verb_with_its_own_options_and_placeholders_is_taken(self) -> None:
        options = pilot_options()
        for command in (
            "pilot.py plan note add --task <id> --summary <line> --ref <block id> <content>",
            "pilot.py answer <file> <block id> --value <option> --note <their words>",
            "pilot.py items show <id>",
            "pilot.py --help",
        ):
            with self.subTest(command):
                self.assertIsNone(command_fault(command, options))

    def test_a_word_that_is_no_verb_or_an_option_of_another_verb_is_refused(self) -> None:
        options = pilot_options()
        self.assertEqual(
            command_fault("pilot.py plan note remove <id>", options),
            "`pilot.py` has no verb `plan note remove`",
        )
        self.assertEqual(
            command_fault("pilot.py answer <file> <block id> --to plan", options),
            "`pilot.py answer` takes no --to",
        )
