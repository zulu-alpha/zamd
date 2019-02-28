"""Tests for common, helper functions"""


def test_make_filename_safe():
    """Check that the returned filename comes out as expected"""
    from app.helpers import make_filename_safe

    assert make_filename_safe("cTab.pbo.Gundy.bisign") == "ctab.pbo.gundy.bisign"
    assert (
        make_filename_safe("[BW] Bush Wars v1.3 (Recce Challenge Addition)")
        == "bw_bush_wars_v1.3_recce_challenge_addition"
    )
