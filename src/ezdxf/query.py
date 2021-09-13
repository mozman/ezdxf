# Purpose: Query language and manipulation object for DXF entities
# Copyright (c) 2013-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    Callable,
    Hashable,
    Dict,
    List,
    Sequence,
    Union,
    cast
)
import re
import operator

from collections import abc
from ezdxf.queryparser import EntityQueryParser
from ezdxf.groupby import groupby

if TYPE_CHECKING:
    from ezdxf.entities import DXFEntity


class EntityQuery(abc.Sequence):
    """EntityQuery is a result container, which is filled with dxf entities
    matching the query string. It is possible to add entities to the container
    (extend), remove entities from the container and to filter the container.

    Query String
    ============

    QueryString := EntityQuery ("[" AttribQuery "]")*

    The query string is the combination of two queries, first the required
    entity query and second the optional attribute query, enclosed in square
    brackets.

    Entity Query
    ------------

    The entity query is a whitespace separated list of DXF entity names or the
    special name ``*``. Where ``*`` means all DXF entities, exclude some entity
    types by appending their names with a preceding ``!`` (e.g. all entities
    except LINE = ``* !LINE``). All DXF names have to be uppercase.

    Attribute Query
    ---------------

    The attribute query is used to select DXF entities by its DXF attributes.
    The attribute query is an addition to the entity query and matches only if
    the entity already match the entity query.
    The attribute query is a boolean expression, supported operators are:

      - not: !term is true, if term is false
      - and: term & term is true, if both terms are true
      - or: term | term is true, if one term is true
      - and arbitrary nested round brackets

    Attribute selection is a term: "name comparator value", where name is a DXF
    entity attribute in lowercase, value is a integer, float or double quoted
    string, valid comparators are:

      - "==" equal "value"
      - "!=" not equal "value"
      - "<" lower than "value"
      - "<=" lower or equal than "value"
      - ">" greater than "value"
      - ">=" greater or equal than "value"
      - "?" match regular expression "value"
      - "!?" does not match regular expression "value"

    Query Result
    ------------

    The EntityQuery() class based on the abstract Sequence() class, contains all
    DXF entities of the source collection, which matches one name of the entity
    query AND the whole attribute query. If a DXF entity does not have or
    support a required attribute, the corresponding attribute search term is
    false.

    Examples:

        - 'LINE[text ? ".*"]' is always empty, because the LINE entity has no
          text attribute.
        - 'LINE CIRCLE[layer=="construction"]' => all LINE and CIRCLE entities
          on layer "construction"
        - '*[!(layer=="construction" & color<7)]' => all entities except those
          on layer == "construction" and color < 7

    """

    def __init__(
        self, entities: Iterable["DXFEntity"] = None, query: str = "*"
    ):
        """
        Setup container with entities matching the initial query.

        Args:
            entities: sequence of wrapped DXF entities (at least GraphicEntity class)
            query: query string, see class documentation

        """
        self.entities: List["DXFEntity"]
        if entities is None:
            self.entities = []
        elif query == "*":
            self.entities = list(entities)
        else:
            match = entity_matcher(query)
            self.entities = [entity for entity in entities if match(entity)]

    def __len__(self) -> int:
        """Returns count of DXF entities."""
        return len(self.entities)

    def __getitem__(self, item):
        """Returns DXFEntity at index `item`, supports negative indices and
        slicing.

        """
        return self.entities.__getitem__(item)

    def __iter__(self) -> Iterator["DXFEntity"]:
        """Returns iterable of DXFEntity objects."""
        return iter(self.entities)

    @property
    def first(self):
        """First entity or ``None``."""
        if len(self.entities):
            return self.entities[0]
        else:
            return None

    @property
    def last(self):
        """Last entity or ``None``."""
        if len(self.entities):
            return self.entities[-1]
        else:
            return None

    def extend(
        self,
        entities: Iterable["DXFEntity"],
        query: str = "*",
        unique: bool = True,
    ) -> "EntityQuery":
        """Extent the :class:`EntityQuery` container by entities matching an
        additional query.

        """
        self.entities.extend(EntityQuery(entities, query))
        if unique:
            self.entities = list(unique_entities(self.entities))
        return self

    def remove(self, query: str = "*") -> None:
        """Remove all entities from :class:`EntityQuery` container matching this
        additional query.

        """
        handles_of_entities_to_remove = frozenset(
            entity.dxf.handle for entity in self.query(query)
        )
        self.entities = [
            entity
            for entity in self.entities
            if entity.dxf.handle not in handles_of_entities_to_remove
        ]

    def query(self, query: str = "*") -> "EntityQuery":
        """Returns a new :class:`EntityQuery` container with all entities
        matching this additional query.

        raises: ParseException (pyparsing.py)

        """
        return EntityQuery(self.entities, query)

    def groupby(
        self, dxfattrib: str = "", key: Callable[["DXFEntity"], Hashable] = None
    ) -> Dict[Hashable, List["DXFEntity"]]:
        """Returns a dict of entity lists, where entities are grouped by a DXF
        attribute or a key function.

        Args:
            dxfattrib: grouping DXF attribute as string like ``'layer'``
            key: key function, which accepts a DXFEntity as argument, returns
                grouping key of this entity or None for ignore this object.
                Reason for ignoring: a queried DXF attribute is not supported by
                this entity

        """
        return groupby(self.entities, dxfattrib, key)


def entity_matcher(query: str) -> Callable[["DXFEntity"], bool]:
    query_args = EntityQueryParser.parseString(query, parseAll=True)
    entity_matcher_ = build_entity_name_matcher(query_args.EntityQuery)
    attrib_matcher = build_entity_attributes_matcher(
        query_args.AttribQuery, query_args.AttribQueryOptions
    )

    def matcher(entity: "DXFEntity") -> bool:
        return entity_matcher_(entity) and attrib_matcher(entity)

    return matcher


def build_entity_name_matcher(
    names: Sequence[str],
) -> Callable[["DXFEntity"], bool]:
    def match(e: "DXFEntity") -> bool:
        return _match(e.dxftype())

    _match = name_matcher(query=" ".join(names))
    return match


class Relation:
    CMP_OPERATORS = {
        "==": operator.eq,
        "!=": operator.ne,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "?": lambda e, regex: regex.match(e) is not None,
        "!?": lambda e, regex: regex.match(e) is None,
    }
    VALID_CMP_OPERATORS = frozenset(CMP_OPERATORS.keys())

    def __init__(self, relation: Sequence, ignore_case: bool):
        name, op, value = relation
        self.dxf_attrib = name
        self.compare = Relation.CMP_OPERATORS[op]
        self.convert_case = to_lower if ignore_case else lambda x: x

        re_flags = re.IGNORECASE if ignore_case else 0
        if "?" in op:
            self.value = re.compile(
                value + "$", flags=re_flags
            )  # always match whole pattern
        else:
            self.value = self.convert_case(value)

    def evaluate(self, entity: "DXFEntity") -> bool:
        try:
            value = self.convert_case(entity.dxf.get_default(self.dxf_attrib))
            return self.compare(value, self.value)
        except AttributeError:  # entity does not support this attribute
            return False
        except ValueError:  # entity supports this attribute, but has no value for it
            return False


def to_lower(value):
    return value.lower() if hasattr(value, "lower") else value


class BoolExpression:
    OPERATORS = {
        "&": operator.and_,
        "|": operator.or_,
    }

    def __init__(self, tokens: Sequence):
        self.tokens = tokens

    def __iter__(self):
        return iter(self.tokens)

    def evaluate(self, entity: "DXFEntity") -> bool:
        if isinstance(
            self.tokens, Relation
        ):  # expression is just one relation, no bool operations
            return self.tokens.evaluate(entity)

        values = []  # first in, first out
        operators = []  # first in, first out
        for token in self.tokens:
            if hasattr(token, "evaluate"):
                values.append(token.evaluate(entity))
            else:  # bool operator
                operators.append(token)
        values.reverse()
        for op in operators:  # as queue -> first in, first out
            if op == "!":
                value = not values.pop()
            else:
                value = BoolExpression.OPERATORS[op](values.pop(), values.pop())
            values.append(value)
        return values.pop()


def _compile_tokens(
    tokens: Union[str, Sequence], ignore_case: bool
) -> Union[str, Relation, BoolExpression]:
    def is_relation(tokens: Sequence) -> bool:
        return len(tokens) == 3 and tokens[1] in Relation.VALID_CMP_OPERATORS

    if isinstance(tokens, str):  # bool operator as string
        return tokens

    tokens = tuple(tokens)
    if is_relation(tokens):
        return Relation(tokens, ignore_case)
    else:
        return BoolExpression(
            [_compile_tokens(token, ignore_case) for token in tokens]
        )


def build_entity_attributes_matcher(
    tokens: Sequence, options: str
) -> Callable[["DXFEntity"], bool]:
    if not len(tokens):
        return lambda x: True
    ignore_case = "i" == options  # at this time just one option is supported
    expr = BoolExpression(_compile_tokens(tokens, ignore_case))  # type: ignore

    def match_bool_expr(entity: "DXFEntity") -> bool:
        return expr.evaluate(entity)

    return match_bool_expr


def unique_entities(entities: Iterable["DXFEntity"]) -> Iterable["DXFEntity"]:
    """Yield all unique entities, order of all entities will be preserved. """
    handles = set()
    for entity in entities:
        handle = entity.dxf.handle
        if handle not in handles:
            handles.add(handle)
            yield entity


def name_query(names: Iterable[str], query: str = "*") -> Iterable[str]:
    """ Filters `names` by `query` string. The `query` string of entity names
    divided by spaces. The special name "*" matches any given name, a
    preceding "!" means exclude this name. Excluding names is only useful if
    the match any name is also given (e.g. "LINE !CIRCLE" is equal to just
    "LINE", where "* !CIRCLE" matches everything except CIRCLE").

    Args:
        names: iterable of names to test
        query: query string of entity names separated by spaces

    Returns: yield matching names

    """
    match = name_matcher(query)
    return (name for name in names if match(name))


def name_matcher(query: str = "*") -> Callable[[str], bool]:
    def match(e: str) -> bool:
        if take_all:
            return e not in exclude
        else:
            return e in include

    match_strings = set(query.upper().split())
    take_all = False
    exclude = set()
    include = set()
    for name in match_strings:
        if name == "*":
            take_all = True
        elif name.startswith("!"):
            exclude.add(name[1:])
        else:
            include.add(name)

    return match


def new(
    entities: Iterable["DXFEntity"] = None, query: str = "*"
) -> EntityQuery:
    """Start a new query based on sequence `entities`. The `entities` argument
    has to be an iterable of :class:`~ezdxf.entities.DXFEntity` or inherited
    objects and returns an :class:`EntityQuery` object.

    """
    return EntityQuery(entities, query)
