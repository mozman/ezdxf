#!/usr/bin/env python3
# encoding: utf-8
# Purpose: 
# Created: 28.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT-License

import sys
if sys.version_info.major > 2: # for Python 3
    from .pyparsing200 import *
else: # for Python 2
    from .pyparsing157 import *

#TODO: boolean operation parser, see pyparsing example: simpleBool.py

# Entity Query Parser
# -------------------
# EntityQueryParser := ("*" | EntityName+) AttributeQuerys?
# AttributeQuerys := "[" AttributeQuery ("&" + AttributeQuery)* "]"
# AttributeQuery := AttributeName Relation AttributeValue
# AttributeName := alphanums
# Relation := "==" | "!=" | "<" | "<=" | ">" | ">=" | "?" | "!?"
# AttributeValue := dblQuotedString | number
#
# examples:
#     'LINE CIRCLE[layer=="construction"]' ; all LINE and CIRCLE entities on layer "construction"
#     '*[layer=="construction"]' ; all entities on layer "construction"

sign = oneOf('+ -')
LBRK = Suppress('[')
RBRK = Suppress(']')
AND = Suppress('&')

integer_constant = Word(nums)
fractional_constant = Combine(Optional(integer_constant) + '.' + integer_constant) \
                    ^ Combine(integer_constant + '.')
number = Combine(Optional(sign) + integer_constant) \
       ^ Combine(Optional(sign) + fractional_constant)
number.addParseAction(lambda t: float(t[0]))
string_ = dblQuotedString.addParseAction(lambda t: t[0][1:-1])

EntityName = Word(alphanums)
AttribName = Word(alphanums)
Relation = oneOf(['==', '!=', '<', '<=', '>', '>=', '?', '!?'])
AttribValue = string_ | number
AttribQuery = Group(AttribName + Relation + AttribValue)
AttribQuerys =(AttribQuery + ZeroOrMore( AND + AttribQuery)).setResultsName('Attributes')
EntityNames = Group(Literal('*') | OneOrMore(EntityName)).setResultsName('EntityNames')
EntityQueryParser = EntityNames + Optional(LBRK + AttribQuerys + RBRK)
