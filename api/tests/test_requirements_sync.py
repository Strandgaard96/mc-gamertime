import re
import tomllib
from pathlib import Path

_API_DIR = Path(__file__).parent.parent


def _pkg_name(dep: str) -> str:
    return re.split(r"[\[><=!;@ \t]", dep.strip())[0].lower().replace("-", "_")


def test_runtime_deps_present_in_requirements_txt():
    with open(_API_DIR / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    pyproject_names = {_pkg_name(d) for d in data["project"]["dependencies"]}

    req_lines = (_API_DIR / "requirements.txt").read_text().splitlines()
    req_names = {
        _pkg_name(line) for line in req_lines if line.strip() and not line.strip().startswith("#")
    }

    missing = pyproject_names - req_names
    assert not missing, (
        "These packages are in pyproject.toml [project.dependencies] but missing\n"
        "from requirements.txt — Lambda will crash on cold start with ImportModuleError:\n"
        + "\n".join(f"  {pkg}" for pkg in sorted(missing))
        + "\n\nFix: add them to api/requirements.txt with a pinned version."
    )
