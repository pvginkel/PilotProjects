"""The brain's map as its sessions load it — CLAUDE.md, the rule files and the four skills: each
skill named as its folder and its brief last, the handbook read first, the format skill cited by
its name, pilot.py's verbs as its parser has them, the tool calls the hook locks around, every
pilot.py command line it quotes one the parser takes, every path the map cites in place, the chat
skill and the create skill reading a person's message as PilotApp's server sends it, the create
skill naming a draft's ask and its material as pilot-store takes them, the pre-rule skill reading
the briefs of a worker's turn and of its writer's answer as PilotApp's server writes them and
naming its writes — a claim and a question to the writer among them — and its hand-on to the plan,
the plan skill naming each mode by its brief's kind line, reading the brief of an item done and the
claimed actions of a worker's turn as the server writes them, naming its writes and copying the
draft's prose into the handbook without its asks, and a work item's fields and brief in one rule
file the skills starting work cite."""

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
# The brief of the job after a worker's turn as PilotApp's BriefService writes it: its kind line, a
# registered document's line in each read state, and a run that registered nothing.
PASS_KIND = "`Pilot's brief · a worker's turn ended · …`"
PASS_DOCUMENT_LINES = (
    "`- <path> (<item id>) — published`",
    "`- <path> (<item id>) — read failed: <reason>`",
    "`Registered nothing this run.`",
)
# The brief of the job after a clarification run's turn, as BriefService writes it: its kind line,
# the run's line, a document asked about, and its last words.
WRITER_ANSWERED_KIND = "`Pilot's brief · the writer answered · …`"
WRITER_ANSWERED_LINES = (
    '`The clarification run: "<title>" (<id>), of the work item "<title>" (<id>)…`',
    "`Asked <stamp> on <path> (<item id>):`",
    "`This pass asks nothing: …`",
)
# pilot-store's ask_writer as it takes its arguments (PilotApp's pilot_mcp/tools.py): the block's
# id names its document.
ASK_WRITER = "`ask_writer` with `block`, `<item id>/<local id>`, and `question`"
# The claim: the block named on the add_item of the work item that does it, then pilot.py's answer
# with the claim's value, pilot.py's CLAIM.
CLAIM_NAMED = "its `claims` the block's id, `<item id>/<local id>`"
# The pass's writes and its hand-on: an answer, a deferral with its plan note, an action's Done and
# a claim through pilot.py, a question to the writer and Pilot's own Done through pilot-store, then
# the plan.
PASS_CALLS = (
    "`pilot.py answer <file> <block id>",
    "`pilot.py defer <file> <block id>",
    "`pilot.py done <file> <block id>",
    CLAIM_NAMED,
    ASK_WRITER,
    "`mark`, `item` the document's id, `mark` `done`, and no `for`",
    "run `/plan`, its mode What is next, in this session",
)
# The brief of the job after a person's close of an item of Pilot's own as PilotApp's BriefService
# writes it: its kind line and the item's line.
ITEM_DONE_KIND = "`Pilot's brief · an item of yours is done · …`"
ITEM_DONE_LINE = '`The item: <path> (<item id>), <kind> "<title>"[, task <id>] — <close>.`'
# The plan skill's modes, each a section of its own.
PLAN_MODES = (
    "## The setup",
    "## What is next",
    "## An action of Pilot's done",
    "## An item done",
    "## The sweep",
    "## The finish decision",
)
# The modes' writes past the setup: a task's status, a note struck, a homeless deferral's note, and
# pilot-store's `finish` on the finish decision's Yes.
PLAN_CALLS = (
    "`pilot.py plan task set <id> --status done`",
    "`pilot.py plan note strike <id>`",
    "`pilot.py plan note add --task <id> --summary <line> --ref <block id> <content>`",
    "the job after its close calls `finish`",
    "`pilot.py done <file> <block id> --note <what was done and what was seen>`",
    "`mark`, `item` the document's id, `mark` `done`, and no `for`",
)
# The claimed actions the brief of a worker's turn names, as BriefService writes them, each open or
# as its close reads.
CLAIMED_ACTIONS = (
    '"The claimed actions given to this work item, as they stand:"',
    (
        "`- <path> (<item id>) <local id>` followed by `open, claimed`, by `open, its claim gone`,"
        " or by its close as it reads"
    ),
)
# A claimed action its run did not reach in a turn that registered documents: the run goes on as a
# work item titled as it, whose brief names no claimed actions, so a note carries them to that
# turn, and nothing retries or hands over an act the run still holds.
CLAIM_CARRIED = (
    "or a note of yours carries them to the brief's work item",
    "After the turn of the work item that continues its run, the brief names none",
    "**Still the run's**, never reached in a turn that registered documents",
    "its run waiting on its documents — gets no second",
)
# The pre-rule skill's section of the routes that wait on work Pilot has not shipped: it holds a
# wait, and neither asking the writer nor a claim.
NOT_YET_THE_PASS_S = "## Not yet the pass's"
# The setup's handbook: the draft's prose without its asks' blocks, a ruled ask's outcome a rule
# line, and the report after the write read for what it says of the handbook.
SETUP_HANDBOOK = (
    "the prose of the draft's `## Rules` and `## Context`, copied, and never an ask's block",
    "an ask fenced there stays in `project.md`",
    "a ruled ask's outcome as a plain rule line",
    "that the write landed is not enough",
)
# A work item's add_item fields and its brief, at home in one rule file that the skills starting
# work cite and none copies.
WORK_ITEMS = "rules/work-items.md"
WORK_ITEM_FIELDS = (
    "`kind` `work`",
    "`title`",
    "`repo`",
    "`cwd`",
    "`model`",
    "`reasoning_effort`",
    "`step`",
    "`attachments`",
    "`brief`",
)
WORK_ITEM_BRIEF = (
    "The task in a line.",
    "copied verbatim from `rules/grants.md`'s \"In a worker's brief\"",
    "never paste the handbook",
)
WORK_ITEM_SKILLS = ("chat", "plan", "pre-rule")


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

    def test_the_setup_copies_the_draft_s_prose_and_none_of_its_asks(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for rule in SETUP_HANDBOOK:
            with self.subTest(rule):
                self.assertIn(rule, text)

    def test_the_plan_skill_names_each_mode_by_its_kind_line(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in (
            SETUP_KIND,
            PASS_KIND,
            WRITER_ANSWERED_KIND,
            ITEM_DONE_KIND,
            "entered from `/pre-rule`",
        ):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_each_mode_is_a_section_of_its_own(self) -> None:
        lines = skill_file("plan").read_text().splitlines()
        for heading in PLAN_MODES:
            with self.subTest(heading):
                self.assertEqual(lines.count(heading), 1)

    def test_an_item_done_reads_the_item_s_line_as_the_server_writes_it(self) -> None:
        self.assertIn(ITEM_DONE_LINE, " ".join(skill_file("plan").read_text().split()))

    def test_an_action_of_pilot_s_done_reads_the_claimed_actions_as_the_server_writes_them(
        self,
    ) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in CLAIMED_ACTIONS:
            with self.subTest(form):
                self.assertIn(form, text)

    def test_a_claimed_action_its_run_still_holds_is_carried_to_the_run_s_next_turn(
        self,
    ) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for form in CLAIM_CARRIED:
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_plan_skill_applies_every_rule_file(self) -> None:
        text = skill_file("plan").read_text()
        for path in sorted((ROOT / "rules").glob("*.md")):
            with self.subTest(path.name):
                self.assertIn(f"`{path.relative_to(ROOT)}`", text)

    def test_the_modes_write_through_pilot_py_and_finish_through_pilot_store(self) -> None:
        text = " ".join(skill_file("plan").read_text().split())
        for call in PLAN_CALLS:
            with self.subTest(call):
                self.assertIn(call, text)


class WorkItemRuleTest(unittest.TestCase):
    def test_the_rule_file_holds_the_fields_and_the_brief(self) -> None:
        text = " ".join((ROOT / WORK_ITEMS).read_text().split())
        for form in (*WORK_ITEM_FIELDS, *WORK_ITEM_BRIEF):
            with self.subTest(form):
                self.assertIn(form, text)

    def test_the_brief_s_grants_text_is_a_section_of_the_grants(self) -> None:
        lines = (ROOT / "rules" / "grants.md").read_text().splitlines()
        self.assertIn("## In a worker's brief", lines)

    def test_the_skills_that_start_work_cite_it_and_carry_no_copy(self) -> None:
        for name in WORK_ITEM_SKILLS:
            text = " ".join(skill_file(name).read_text().split())
            with self.subTest(name):
                self.assertIn(f"`{WORK_ITEMS}`", text)
                for form in ("`reasoning_effort`", "In a worker's brief", "paste the handbook"):
                    self.assertNotIn(form, text)


class PreRuleSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = " ".join(skill_file("pre-rule").read_text().split())

    def test_the_pass_reads_the_brief_as_the_server_writes_it(self) -> None:
        for form in (PASS_KIND, *PASS_DOCUMENT_LINES):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_the_pass_routes_by_the_rule_files(self) -> None:
        for rule in ("`rules/routing.md`", "`rules/grants.md`"):
            with self.subTest(rule):
                self.assertIn(rule, self.text)

    def test_the_pass_writes_through_pilot_py_marks_through_pilot_store_and_hands_on(self) -> None:
        for call in PASS_CALLS:
            with self.subTest(call):
                self.assertIn(call, self.text)

    def test_the_pass_reads_the_writer_answered_brief_as_the_server_writes_it(self) -> None:
        for form in (WRITER_ANSWERED_KIND, *WRITER_ANSWERED_LINES):
            with self.subTest(form):
                self.assertIn(form, self.text)

    def test_asking_the_writer_and_claiming_are_the_pass_s_and_a_wait_is_not_yet(self) -> None:
        _, _, rest = skill_file("pre-rule").read_text().partition(f"\n{NOT_YET_THE_PASS_S}\n")
        not_yet, _, _ = rest.partition("\n## ")
        self.assertIn("**A wait.**", not_yet)
        for route in ("ask_writer", pilot_module().CLAIM):
            with self.subTest(route):
                self.assertNotIn(route, not_yet)


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

    def test_claude_md_names_every_tool_call_the_hook_locks_around(self) -> None:
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
        (entry,) = settings["hooks"]["PreToolUse"]
        text = CLAUDE.read_text()
        for tool in entry["matcher"].split("|"):
            with self.subTest(tool):
                self.assertIn(f"`{tool}`", text)

    def test_every_pilot_py_command_the_map_quotes_is_one_its_parser_takes(self) -> None:
        options = pilot_options()
        for source, text in the_map().items():
            for command in quoted_commands(text):
                with self.subTest(source=source, command=command):
                    self.assertIsNone(command_fault(command, options))

    def test_the_claim_is_quoted_with_the_value_pilot_py_reads_as_one(self) -> None:
        value = f'--value "{pilot_module().CLAIM}"'
        for path in (skill_file("pre-rule"), skill_file("plan"), ROOT / "rules" / "routing.md"):
            with self.subTest(path.relative_to(ROOT)):
                self.assertIn(value, " ".join(path.read_text().split()))

    def test_ask_writer_is_named_by_the_arguments_pilot_store_takes(self) -> None:
        for path in (skill_file("pre-rule"), ROOT / "rules" / "routing.md"):
            with self.subTest(path.relative_to(ROOT)):
                self.assertIn(ASK_WRITER, " ".join(path.read_text().split()))

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
