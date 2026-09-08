from typing import Annotated

from fastapi import APIRouter, Depends

from lib.auth import AuthUser, require_auth
from lib.db.games import list_games
from lib.db.results import list_results
from lib.stats import compute_stats

router = APIRouter()


@router.get("")
def get_stats(_: Annotated[AuthUser, Depends(require_auth)]):
    results = list_results()
    games = list_games()
    return compute_stats(results, games)
