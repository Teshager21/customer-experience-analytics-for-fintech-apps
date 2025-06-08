import pytest
from features.theme_clustering import assign_themes


class TestAssignThemes:
    """Unit tests for the assign_themes function."""

    @pytest.mark.parametrize(
        "keywords, expected_themes",
        [
            (["login issue", "password reset"], ["Account Access Issues"]),
            (["app crash", "very slow"], ["Reliability", "Transaction Performance"]),
            (
                ["great support", "poor interface"],
                ["Customer Support", "User Experience"],
            ),
            (["new feature", "update required"], ["Feature Requests"]),
            (
                ["login", "support", "feature"],
                ["Account Access Issues", "Customer Support", "Feature Requests"],
            ),
            ([], ["Miscellaneous"]),
            (["randomword", "unknown term"], ["Miscellaneous"]),
        ],
    )
    def test_assign_themes_expected_cases(self, keywords, expected_themes):
        """Test that known keywords correctly map to their corresponding themes."""
        result = assign_themes(keywords)
        assert set(result) == set(expected_themes)

    def test_assign_themes_case_insensitivity(self):
        """Ensure the matching is case-insensitive (if intended)."""
        # This will fail if `assign_themes` is case-sensitive
        result = assign_themes(["Login", "SUPPORT"])
        assert "Account Access Issues" in result
        assert "Customer Support" in result

    def test_assign_themes_no_matches(self):
        """Test that unknown keywords return 'Miscellaneous'."""
        result = assign_themes(["foo", "bar", "baz"])
        assert result == ["Miscellaneous"]

    def test_assign_themes_partial_matches(self):
        """Test that partial substring matches work as expected."""
        result = assign_themes(["app crashing", "login failed"])
        assert "Reliability" in result
        assert "Account Access Issues" in result
