"""
Provides ``count_tokens`` which uses the ``cl100k_base`` tiktoken encoding
(same vocabulary as GPT-4 / Nova) to count tokens in a text string.

The encoding is loaded once at module import time and reused for every call.

Usage
-----
    from app.ingestion.token_counter import count_tokens
    n = count_tokens("def hello(): pass")
"""

import tiktoken

# Load once at module level — this is a ~3 MB binary file; caching it avoids
# repeated disk reads on every request.
_ENCODING = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the number of tokens in *text* using the cl100k_base encoding.

    Parameters
    ----------
    text:
        Any UTF-8 string.

    Returns
    -------
    int
        Token count.  Returns 0 for empty strings.
    """
    if not text:
        return 0
    return len(_ENCODING.encode(text))
