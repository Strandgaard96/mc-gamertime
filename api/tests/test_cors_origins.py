"""CORS allow-list parsing (main.parse_allowed_origins).

The list feeds CORSMiddleware with allow_credentials=True, so every entry is a
peer the browser will send the session cookie to. Parsing must widen the
allow-list only for explicitly configured http(s) origins.
"""

from main import DEV_ORIGINS, parse_allowed_origins


def test_empty_env_means_same_origin_only():
    assert parse_allowed_origins("", dev=False) == []


def test_splits_and_trims_comma_separated_origins():
    raw = " https://a.example , https://b.example "
    assert parse_allowed_origins(raw, dev=False) == ["https://a.example", "https://b.example"]


def test_skips_blank_entries_from_stray_commas():
    assert parse_allowed_origins("https://a.example,,", dev=False) == ["https://a.example"]


def test_strips_trailing_slash_so_origin_header_matches():
    # A browser's Origin header never carries a trailing slash.
    assert parse_allowed_origins("https://a.example/", dev=False) == ["https://a.example"]


def test_deduplicates():
    raw = "https://a.example,https://a.example/"
    assert parse_allowed_origins(raw, dev=False) == ["https://a.example"]


def test_wildcard_is_dropped_not_honoured():
    # "*" with credentials is rejected by browsers and would be a real hole if
    # a server ever honoured it.
    assert parse_allowed_origins("*", dev=False) == []
    assert parse_allowed_origins("*,https://a.example", dev=False) == ["https://a.example"]


def test_null_origin_is_dropped():
    assert parse_allowed_origins("null", dev=False) == []


def test_schemeless_entry_is_dropped():
    assert parse_allowed_origins("a.example", dev=False) == []


def test_localhost_never_added_outside_dev():
    assert parse_allowed_origins("https://a.example", dev=False) == ["https://a.example"]


def test_dev_adds_localhost_origins():
    assert parse_allowed_origins("", dev=True) == DEV_ORIGINS
    assert parse_allowed_origins("https://a.example", dev=True) == [
        "https://a.example",
        *DEV_ORIGINS,
    ]


def test_dev_origin_listed_explicitly_is_not_duplicated():
    assert parse_allowed_origins(DEV_ORIGINS[0], dev=True) == DEV_ORIGINS
