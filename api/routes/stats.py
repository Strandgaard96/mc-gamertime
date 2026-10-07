from typing import Annotated

from fastapi import APIRouter, Depends, Query

import lib.seasons as seasons_lib
from lib.auth import AuthUser, require_auth
from lib.db.games import list_games
from lib.db.results import list_results
from lib.stats import compute_stats

router = APIRouter()


@router.get("")
def get_stats(
    _: Annotated[AuthUser, Depends(require_auth)],
    season: Annotated[str | None, Query(pattern=seasons_lib.SEASON_PATTERN)] = None,
):
    results = list_results()
    if season:
        results = seasons_lib.results_in_season(results, season)
    return compute_stats(results, list_games())


@router.get("/seasons")
def get_seasons(_: Annotated[AuthUser, Depends(require_auth)]):
    return seasons_lib.list_seasons(list_results(), seasons_lib.today_utc())
