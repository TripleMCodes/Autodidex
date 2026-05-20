class ColorService:
    """
    Maps a session count to a GitHub-style activity colour.

    Keeping this as a class (rather than a loose module-level function)
    makes it easy to swap the palette, mock in tests, or subclass for
    different colour schemes.
    """

    # Thresholds are checked in order; first match wins.
    _THRESHOLDS: list[tuple[int | None, str]] = [
        (0,  "#ebedf0"),  # no activity
        (1,  "#c6e48b"),  # light green
        (2,  "#7bc96f"),
        (3,  "#239a3b"),
        (5,  "#1f7c32"),  # count 4–5
        (8,  "#134D1F"),  # count 6–8
        (14, "#03300C"),  # count 9–14
        (None, "#011405"), # 15+
    ]

    def get(self, count: int) -> str:
        """Return the hex colour string for *count* sessions."""
        for threshold, colour in self._THRESHOLDS:
            if threshold is None or count <= threshold:
                return colour
        return self._THRESHOLDS[-1][1]
