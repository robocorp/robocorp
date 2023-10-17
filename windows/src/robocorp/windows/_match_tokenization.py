"""
Utilities for tokenizing a locator.
"""

import enum
from typing import Iterator, Optional

from ._errors import ParseError
from ._match_common import _valid_strategies


class TokenKind(enum.Enum):
    strategy = 1
    value = 2
    parens_start = 3  # ')'
    parens_end = 4  # '('
    or_token = 5  # or
    and_token = 6  # and
    match_child = 7  # '>'
    desktop = 8  # special case as desktop doesn't need a ':'.


class Token:
    quoted = False

    def __init__(self, token: str, kind: TokenKind):
        self.token = token
        self.kind = kind

    def __bool__(self):
        return bool(self.token)

    def __str__(self):
        return f"{self.token} ({self.kind})"

    __repr__ = __str__


class QuotedToken(Token):
    quoted = True

    def __init__(self, token: str, kind: TokenKind):
        self.token = token
        self.kind = kind

    def __bool__(self):
        return bool(self.token)

    def __str__(self):
        return f'"{self.token}" ({self.kind})'

    __repr__ = __str__


class _Tokenizer:
    def __init__(self, input_str: str) -> None:
        self._input_str = input_str
        self._char_pos = 0
        self._len = len(self._input_str)
        self._start_token_pos = self._char_pos

    def _peek_token(self):
        start_token_pos = self._start_token_pos
        if start_token_pos == -1:
            return None
        curr_token_pos = self._char_pos
        token = self._input_str[start_token_pos:curr_token_pos]
        return token

    def _make_token(self, token_kind) -> Optional[Token]:
        token = self._peek_token()
        if not token:
            return None
        self._start_token_pos = -1  # Reset the start pos
        if token_kind == TokenKind.value:
            # Convert to or/and if needed
            if token == "or":
                return Token(token, TokenKind.or_token)
            elif token == "and":
                return Token(token, TokenKind.and_token)
            elif token == ">":
                return Token(token, TokenKind.match_child)
            elif token == "desktop":
                return Token(token, TokenKind.desktop)

        return Token(token, token_kind)

    def _make_token_remove_quotes(self, token_kind) -> Optional[Token]:
        token = self._peek_token()
        if not token:
            return None
        self._start_token_pos = -1  # Reset the start pos
        return QuotedToken(token[1:-1], token_kind)

    def _skip_spaces(self):
        input_str = self._input_str
        char_pos = self._char_pos

        while char_pos < self._len:
            c = input_str[char_pos]
            if c in (" ", "\t"):
                char_pos += 1
                continue
            break
        return char_pos

    def _consume_up_to_next_quote(self):
        input_str = self._input_str
        char_pos = self._char_pos
        initial_quote_pos = char_pos
        while char_pos < self._len:
            c = input_str[char_pos]
            if c == "\\":
                char_pos += 1
                char_pos += 1
                continue

            if c == '"':
                return char_pos
            char_pos += 1
        raise ParseError(
            f"Unbalanced quote found at index: {initial_quote_pos}.", initial_quote_pos
        )

    def tokenize(self) -> Iterator[Token]:
        input_str = self._input_str

        while self._char_pos < self._len:
            c = input_str[self._char_pos]

            if c in (" ", "\t"):
                tok = self._make_token(TokenKind.value)
                if tok:
                    yield tok
                self._char_pos += 1
                self._start_token_pos = self._char_pos
                continue

            if c == '"':
                self._start_token_pos = self._char_pos
                self._char_pos += 1
                self._char_pos = self._consume_up_to_next_quote()
                self._char_pos += 1
                tok = self._make_token_remove_quotes(TokenKind.value)
                if tok:
                    yield tok
                self._char_pos += 1
                continue

            if c in ("(", ")"):
                tok = self._make_token(TokenKind.value)
                if tok:
                    yield tok
                self._start_token_pos = self._char_pos
                self._char_pos += 1

                parens_token = self._make_token(
                    TokenKind.parens_start if c == "(" else TokenKind.parens_end
                )
                assert parens_token
                yield parens_token
                continue

            if c == "\\":
                self._char_pos += 1
                self._char_pos += 1
                continue

            if c == ":":
                tok = self._peek_token()
                if tok in _valid_strategies:
                    tok = self._make_token(TokenKind.strategy)
                    assert tok
                    yield tok

                self._char_pos += 1
                self._char_pos = self._skip_spaces()
                continue

            if self._start_token_pos == -1:
                self._start_token_pos = self._char_pos

            self._char_pos += 1

        tok = self._make_token(TokenKind.value)
        if tok:
            yield tok
