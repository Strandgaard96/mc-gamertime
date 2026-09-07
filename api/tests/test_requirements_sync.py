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


def _pinned(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    return {
        _pkg_name(line): line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    }


def test_selfhost_requirements_are_lambda_set_minus_aws_sdk_plus_uvicorn():
    """The Docker image installs requirements-selfhost.txt (no boto3/mangum). It
    must otherwise carry the same pins as requirements.txt, so a bump in one
    can't silently diverge from the other."""
    lambda_reqs = _pinned(_API_DIR / "requirements.txt")
    selfhost_reqs = _pinned(_API_DIR / "requirements-selfhost.txt")

    aws_only = {"boto3", "mangum"}
    assert aws_only <= set(lambda_reqs), "boto3/mangum must stay in requirements.txt (Lambda)"
    assert not aws_only & set(selfhost_reqs), "boto3/mangum must not be in the selfhost image"

    expected = {k: v for k, v in lambda_reqs.items() if k not in aws_only}
    actual = {k: v for k, v in selfhost_reqs.items() if k != "uvicorn"}
    assert actual == expected, "requirements-selfhost.txt drifted from requirements.txt"
    assert "uvicorn" in selfhost_reqs, "the container's server must be pinned in selfhost reqs"
