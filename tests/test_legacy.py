"""Upgrading a clone from Harvey, Andorinha's old name, must never lose data.

Covers the file moves (andorinha/legacy.py), HARVEY_* settings, and the old
`harvey` command (the harvey/ package), including a clone that ran `git pull`
without reinstalling.
"""

import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import harvey
import harvey.cli
import andorinha.legacy as legacy
from tests.test_dashboard_live_status import client, env  # noqa: F401  (fixtures)

ROOT = Path(__file__).resolve().parent.parent


def _sellbird_install(root: Path, *, db=b"upstream db", local=b"product: upstream\n"):
    """A checkout that ran under the upstream name, before this fork."""
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "sellbird.db").write_bytes(db)
    (root / "data" / "sellbird.log").write_text("log\n")
    (root / "sellbird.local.yaml").write_bytes(local)


def _harvey_install(root: Path, *, db=b"old db", local=b"product: old\n"):
    (root / "data").mkdir()
    (root / "data" / "harvey.db").write_bytes(db)
    (root / "data" / "harvey.log").write_text("log\n")
    (root / "harvey.local.yaml").write_bytes(local)


# ── files ──


def test_moves_a_harvey_install_to_the_new_names(tmp_path):
    _harvey_install(tmp_path)
    (tmp_path / "data" / "harvey.db-wal").write_bytes(b"recent writes")

    notes = legacy.migrate_files(tmp_path)

    assert (tmp_path / "data" / "andorinha.db").read_bytes() == b"old db"
    assert (tmp_path / "data" / "andorinha.db-wal").read_bytes() == b"recent writes"
    assert (tmp_path / "data" / "andorinha.log").exists()
    assert (tmp_path / "andorinha.local.yaml").read_bytes() == b"product: old\n"
    assert not (tmp_path / "data" / "harvey.db").exists()
    assert "Moved data/harvey.db to data/andorinha.db." in notes


def test_nothing_to_do_says_nothing(tmp_path):
    assert legacy.migrate_files(tmp_path) == []


def test_runs_once(tmp_path):
    _harvey_install(tmp_path)
    legacy.migrate_files(tmp_path)
    assert legacy.migrate_files(tmp_path) == []


def test_never_overwrites_a_file_under_the_new_name(tmp_path):
    _harvey_install(tmp_path)
    (tmp_path / "andorinha.local.yaml").write_text("product: new\n")

    notes = legacy.migrate_files(tmp_path)

    assert (tmp_path / "andorinha.local.yaml").read_text() == "product: new\n"
    assert (tmp_path / "harvey.local.yaml").read_bytes() == b"product: old\n"
    assert any("Left harvey.local.yaml alone" in n for n in notes)
    # The files without a conflict still move.
    assert (tmp_path / "data" / "andorinha.db").exists()


def test_waits_while_harvey_is_still_running(tmp_path, monkeypatch):
    _harvey_install(tmp_path)
    (tmp_path / "data" / "harvey.pid").write_text("4242")
    monkeypatch.setattr("andorinha.pidfile.pid_alive", lambda pid: pid == 4242)

    notes = legacy.migrate_files(tmp_path)

    assert notes == ["Harvey is still running here (process 4242). Stop it, then run "
                     "Andorinha again to move its files over."]
    assert (tmp_path / "data" / "harvey.db").exists()
    assert not (tmp_path / "data" / "andorinha.db").exists()


def test_clears_a_dead_harveys_pidfile(tmp_path, monkeypatch):
    _harvey_install(tmp_path)
    (tmp_path / "data" / "harvey.pid").write_text("4242")
    monkeypatch.setattr("andorinha.pidfile.pid_alive", lambda pid: False)

    legacy.migrate_files(tmp_path)

    assert not (tmp_path / "data" / "harvey.pid").exists()
    assert (tmp_path / "data" / "andorinha.db").exists()


# ── settings ──


def test_harvey_settings_fill_in_unset_andorinha_ones():
    env = {"HARVEY_HUMANIZER_SKILL": "/old/skill.md", "HARVEY_UID": "501",
           "ANDORINHA_UID": "1000", "PATH": "/bin"}

    adopted = legacy.adopt_legacy_env(env)

    assert adopted == ["ANDORINHA_HUMANIZER_SKILL"]
    assert env["ANDORINHA_HUMANIZER_SKILL"] == "/old/skill.md"
    assert env["ANDORINHA_UID"] == "1000"  # the new name always wins


def test_harvey_setting_reaches_a_module_that_reads_it_at_import():
    code = "import andorinha.humanize as h; print(h.SKILL_PATH)"
    env = {k: v for k, v in os.environ.items() if not k.startswith(("HARVEY_", "ANDORINHA_"))}
    env["HARVEY_HUMANIZER_SKILL"] = "/old/skill.md"
    out = subprocess.run([sys.executable, "-c", code], env=env, cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    assert Path(out.strip()) == Path("/old/skill.md")  # Windows prints \old\skill.md


# ── the old command ──


def test_old_command_says_it_moved_then_runs_andorinha(monkeypatch, capsys):
    ran = []
    monkeypatch.setattr("andorinha.cli.main", lambda: ran.append(sys.argv[0]))
    monkeypatch.setattr(sys, "argv", ["harvey", "status"])

    harvey.cli.main()

    assert ran == ["andorinha"]
    assert "Harvey is now Andorinha" in capsys.readouterr().err


@pytest.mark.parametrize("module", ["harvey", "andorinha"])
def test_both_names_run_as_modules(module):
    result = subprocess.run([sys.executable, "-m", module, "--help"], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "andorinha" in result.stdout
    assert ("Harvey is now Andorinha" in result.stderr) == (module == "harvey")


def test_package_declares_every_old_command():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert project["project"]["name"] == "andorinha"
    assert project["project"]["scripts"] == {"andorinha": "andorinha.cli:main",
                                             "sellbird": "sellbird.cli:main",
                                             "harvey": "harvey.cli:main"}
    include = project["tool"]["setuptools"]["packages"]["find"]["include"]
    assert "harvey*" in include
    assert "sellbird*" in include


def test_old_files_stay_out_of_git():
    ignored = (ROOT / ".gitignore").read_text().splitlines()
    assert {"harvey.local.yaml", "harvey.local.yaml.*", "data/", "*.db"} <= set(ignored)


# ── the dashboard says it once ──


def test_moving_files_leaves_the_dashboard_notice(tmp_path):
    _harvey_install(tmp_path)
    legacy.migrate_files(tmp_path)
    assert legacy.welcome_pending(tmp_path)
    legacy.dismiss_welcome(tmp_path)
    assert not legacy.welcome_pending(tmp_path)
    legacy.dismiss_welcome(tmp_path)  # twice is fine


def test_no_notice_when_nothing_moved(tmp_path):
    assert legacy.migrate_files(tmp_path) == []
    assert not legacy.welcome_pending(tmp_path)


def test_no_notice_when_every_file_was_left_alone(tmp_path):
    (tmp_path / "harvey.local.yaml").write_text("product: old\n")
    (tmp_path / "andorinha.local.yaml").write_text("product: new\n")
    legacy.migrate_files(tmp_path)
    assert not legacy.welcome_pending(tmp_path)


def test_the_dashboard_shows_the_notice_until_dismissed(client, tmp_path, monkeypatch):
    root = tmp_path / "install"
    root.mkdir()
    _harvey_install(root)
    legacy.migrate_files(root)
    monkeypatch.setattr(legacy, "PROJECT_ROOT", root)
    assert client.get("/api/rename-notice").json() == {"show": True}
    assert client.post("/api/rename-notice/dismiss").json()["success"]
    assert client.get("/api/rename-notice").json() == {"show": False}


# ── the fork's own rename: a checkout that ran as Sellbird ──


def test_moves_a_sellbird_install_to_the_new_names(tmp_path):
    _sellbird_install(tmp_path)
    (tmp_path / "data" / "sellbird.db-wal").write_bytes(b"recent writes")

    legacy.migrate_files(tmp_path)

    assert (tmp_path / "data" / "andorinha.db").read_bytes() == b"upstream db"
    assert (tmp_path / "data" / "andorinha.db-wal").read_bytes() == b"recent writes"
    assert (tmp_path / "andorinha.local.yaml").read_bytes() == b"product: upstream\n"
    assert not (tmp_path / "data" / "sellbird.db").exists()


def test_a_sellbird_file_never_overwrites_an_andorinha_one(tmp_path):
    _sellbird_install(tmp_path)
    (tmp_path / "andorinha.local.yaml").write_bytes(b"product: mine\n")

    legacy.migrate_files(tmp_path)

    assert (tmp_path / "andorinha.local.yaml").read_bytes() == b"product: mine\n"
    assert (tmp_path / "sellbird.local.yaml").exists()


def test_sellbird_environment_variables_are_honoured():
    env = {"SELLBIRD_MAX_SENDS": "7"}
    assert legacy.adopt_legacy_env(env) == ["ANDORINHA_MAX_SENDS"]
    assert env["ANDORINHA_MAX_SENDS"] == "7"


def test_an_andorinha_variable_wins_over_a_sellbird_one():
    env = {"SELLBIRD_MAX_SENDS": "7", "ANDORINHA_MAX_SENDS": "9"}
    assert legacy.adopt_legacy_env(env) == []
    assert env["ANDORINHA_MAX_SENDS"] == "9"
