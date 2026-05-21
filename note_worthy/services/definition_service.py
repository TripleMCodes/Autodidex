import logging

try:
    import nltk
    from nltk.corpus import wordnet
    # nltk.download("wordnet", quiet=True)
    _WORDNET_AVAILABLE = True
except Exception as e:
    logging.warning(f"DefinitionService: WordNet unavailable: {e}")
    _WORDNET_AVAILABLE = False


class DefinitionService:
    """
    Looks up word definitions via NLTK WordNet.
    Returns a formatted string ready to display in the UI.
    """

    MAX_DEFINITIONS = 3

    def lookup(self, word: str) -> str:
        """
        Return a bullet-formatted definition string for *word*.
        Returns a user-facing error message if the word is empty,
        not found, or WordNet is unavailable.
        """
        word = word.strip().lower()
        if not word:
            return "⚠️ Please enter a word."
        if not _WORDNET_AVAILABLE:
            return "⚠️ Dictionary unavailable (WordNet not installed)."

        synsets = wordnet.synsets(word)
        if not synsets:
            return "❌ No definition found."

        lines = [f"• {s.definition()}" for s in synsets[: self.MAX_DEFINITIONS]]
        return "\n".join(lines)
