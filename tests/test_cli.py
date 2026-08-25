import subprocess
import sys
import json
from pathlib import Path

PYTHON_EXE = sys.executable
ROOT_DIR = Path(__file__).resolve().parent.parent
CLI_SCRIPT = ROOT_DIR / "scripts" / "ads_tool.py"

def run_cli(args):
    cmd = [PYTHON_EXE, str(CLI_SCRIPT)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT_DIR))
    return result

def test_cli_search():
    res = run_cli(["search", "author:Hawking", "--rows", "2", "--fl", "bibcode,title"])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert "docs" in data
    assert len(data["docs"]) == 2

def test_cli_metrics_summary():
    res = run_cli(["metrics", "--bibcodes", "1975CMaPh..43..199H,1974Natur.248...30H", "--summary"])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["total_papers"] == 2
    assert "h_index" in data

def test_cli_export():
    res = run_cli(["export", "--bibcodes", "1975CMaPh..43..199H", "--format", "bibtex"])
    assert res.returncode == 0
    assert "@ARTICLE" in res.stdout
    assert "1975CMaPh..43..199H" in res.stdout

def test_cli_journal():
    res = run_cli(["journal", "summary", "ApJ"])
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert "summary" in data
