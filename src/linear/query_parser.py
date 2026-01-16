"""Query string parser for Linear CLI filters.

Supports syntax like:
    team:ENG AND priority:1
    team:ENG OR team:DESIGN
    status:"in progress" AND created-after:2025-01-01
    (team:ENG OR team:DESIGN) AND priority:1
"""

import re
from typing import Any


class QueryParseError(Exception):
    """Raised when query string cannot be parsed."""

    pass


class Token:
    """A token in the query string."""

    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Tokenizer:
    """Tokenize a query string into tokens."""

    def __init__(self, query: str):
        self.query = query
        self.pos = 0

    def peek(self) -> str | None:
        """Peek at the current character without consuming it."""
        if self.pos >= len(self.query):
            return None
        return self.query[self.pos]

    def advance(self) -> str | None:
        """Consume and return the current character."""
        if self.pos >= len(self.query):
            return None
        char = self.query[self.pos]
        self.pos += 1
        return char

    def skip_whitespace(self):
        """Skip whitespace characters."""
        char = self.peek()
        while char and char.isspace():
            self.advance()
            char = self.peek()

    def read_quoted_string(self) -> str:
        """Read a quoted string (handles both single and double quotes)."""
        quote = self.advance()  # consume opening quote
        chars = []
        while True:
            char = self.peek()
            if char is None:
                raise QueryParseError(
                    f"Unterminated string starting at position {self.pos}"
                )
            if char == quote:
                self.advance()  # consume closing quote
                break
            if char == "\\":
                self.advance()
                next_char = self.advance()
                if next_char:
                    chars.append(next_char)
            else:
                chars.append(self.advance())
        return "".join(chars)

    def read_word(self) -> str:
        """Read a word (alphanumeric, dash, underscore, or colon)."""
        chars = []
        while True:
            char = self.peek()
            if char is None:
                break
            if char.isalnum() or char in "-_@.":
                chars.append(self.advance())
            else:
                break
        return "".join(chars)

    def tokenize(self) -> list[Token]:
        """Tokenize the query string."""
        tokens = []

        while self.pos < len(self.query):
            self.skip_whitespace()

            char = self.peek()
            if char is None:
                break

            # Parentheses
            if char == "(":
                self.advance()
                tokens.append(Token("LPAREN", "("))
                continue
            if char == ")":
                self.advance()
                tokens.append(Token("RPAREN", ")"))
                continue

            # Quoted string
            if char in ('"', "'"):
                value = self.read_quoted_string()
                tokens.append(Token("VALUE", value))
                continue

            # Colon (field separator)
            if char == ":":
                self.advance()
                tokens.append(Token("COLON", ":"))
                continue

            # Word (field name, value, or operator)
            word = self.read_word()
            if not word:
                raise QueryParseError(
                    f"Unexpected character '{char}' at position {self.pos}"
                )

            # Check if it's an operator
            if word.upper() in ("AND", "OR"):
                tokens.append(Token("OPERATOR", word.upper()))
            else:
                tokens.append(Token("WORD", word))

        return tokens


class QueryParser:
    """Parse a query string into a filter structure."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token | None:
        """Peek at the current token."""
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def advance(self) -> Token | None:
        """Consume and return the current token."""
        if self.pos >= len(self.tokens):
            return None
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def expect(self, token_type: str) -> Token:
        """Expect a specific token type and consume it."""
        token = self.advance()
        if token is None or token.type != token_type:
            raise QueryParseError(
                f"Expected {token_type}, got {token.type if token else 'EOF'}"
            )
        return token

    def parse(self) -> dict[str, Any]:
        """Parse the tokens into a filter structure."""
        if not self.tokens:
            return {}

        expr = self.parse_or_expr()

        # Check if we consumed all tokens
        if self.peek() is not None:
            raise QueryParseError(f"Unexpected token: {self.peek()}")

        return expr

    def parse_or_expr(self) -> dict[str, Any]:
        """Parse an OR expression (lowest precedence)."""
        left = self.parse_and_expr()

        or_terms = [left]
        token = self.peek()
        while token and token.type == "OPERATOR" and token.value == "OR":
            self.advance()  # consume OR
            right = self.parse_and_expr()
            or_terms.append(right)
            token = self.peek()

        if len(or_terms) == 1:
            return left

        return {"or": or_terms}

    def parse_and_expr(self) -> dict[str, Any]:
        """Parse an AND expression (higher precedence than OR)."""
        left = self.parse_primary()

        and_terms = [left]
        token = self.peek()
        while token and token.type == "OPERATOR" and token.value == "AND":
            self.advance()  # consume AND
            right = self.parse_primary()
            and_terms.append(right)
            token = self.peek()

        if len(and_terms) == 1:
            return left

        return {"and": and_terms}

    def parse_primary(self) -> dict[str, Any]:
        """Parse a primary expression (field:value or grouped expression)."""
        token = self.peek()

        if token is None:
            raise QueryParseError("Unexpected end of query")

        # Grouped expression
        if token.type == "LPAREN":
            self.advance()  # consume (
            expr = self.parse_or_expr()
            self.expect("RPAREN")
            return expr

        # Field:value expression
        field_token = self.expect("WORD")
        self.expect("COLON")

        value_token = self.peek()
        if value_token is None:
            raise QueryParseError(f"Expected value after {field_token.value}:")

        if value_token.type == "VALUE":
            self.advance()
            value = value_token.value
        elif value_token.type == "WORD":
            self.advance()
            value = value_token.value
        else:
            raise QueryParseError(f"Expected value, got {value_token.type}")

        return self.build_filter(field_token.value, value)

    def build_filter(self, field: str, value: str) -> dict[str, Any]:
        """Build a GraphQL filter from a field:value pair."""
        field_lower = field.lower()

        # Date range filters
        if field_lower in ("created-after", "created_after", "createdafter"):
            from linear.api.issues import _to_iso_datetime

            return {
                "createdAt": {
                    "gte": _to_iso_datetime(self._normalize_date(value), True)
                }
            }

        if field_lower in ("created-before", "created_before", "createdbefore"):
            from linear.api.issues import _to_iso_datetime

            return {
                "createdAt": {
                    "lt": _to_iso_datetime(self._normalize_date(value), False)
                }
            }

        if field_lower in ("updated-after", "updated_after", "updatedafter"):
            from linear.api.issues import _to_iso_datetime

            return {
                "updatedAt": {
                    "gte": _to_iso_datetime(self._normalize_date(value), True)
                }
            }

        if field_lower in ("updated-before", "updated_before", "updatedbefore"):
            from linear.api.issues import _to_iso_datetime

            return {
                "updatedAt": {
                    "lt": _to_iso_datetime(self._normalize_date(value), False)
                }
            }

        # Team filter
        if field_lower == "team":
            return {"team": {"key": {"eqIgnoreCase": value}}}

        # Status/state filter
        if field_lower in ("status", "state"):
            return {"state": {"name": {"eqIgnoreCase": value}}}

        # Assignee filter
        if field_lower == "assignee":
            return {"assignee": {"email": {"eq": value}}}

        # Creator filter
        if field_lower == "creator":
            return {"creator": {"email": {"eq": value}}}

        # Priority filter
        if field_lower == "priority":
            try:
                priority_int = int(value)
                return {"priority": {"eq": priority_int}}
            except ValueError:
                raise QueryParseError(f"Invalid priority value: {value} (must be 0-4)")

        # Project filter
        if field_lower == "project":
            # Check if it's a UUID
            if len(value) == 36 and "-" in value:
                return {"project": {"id": {"eq": value}}}
            else:
                return {"project": {"name": {"contains": value}}}

        # Label filter
        if field_lower == "label":
            return {"labels": {"name": {"in": [value]}}}

        raise QueryParseError(f"Unknown field: {field}")

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date format from YYYYMMDD to YYYY-MM-DD."""
        # If already in YYYY-MM-DD format, return as is
        if "-" in date_str:
            return date_str

        # Convert YYYYMMDD to YYYY-MM-DD
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"

        return date_str


def parse_query(query: str) -> dict[str, Any]:
    """Parse a query string into a GraphQL filter structure.

    Args:
        query: Query string (e.g., "team:ENG AND priority:1")

    Returns:
        GraphQL filter dictionary

    Raises:
        QueryParseError: If the query cannot be parsed

    Examples:
        >>> parse_query("team:ENG")
        {'team': {'key': {'eqIgnoreCase': 'ENG'}}}

        >>> parse_query("team:ENG OR team:DESIGN")
        {'or': [
            {'team': {'key': {'eqIgnoreCase': 'ENG'}}},
            {'team': {'key': {'eqIgnoreCase': 'DESIGN'}}}
        ]}

        >>> parse_query("team:ENG AND priority:1")
        {'and': [
            {'team': {'key': {'eqIgnoreCase': 'ENG'}}},
            {'priority': {'eq': 1}}
        ]}
    """
    tokenizer = Tokenizer(query)
    tokens = tokenizer.tokenize()

    parser = QueryParser(tokens)
    return parser.parse()
