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

sign = oneOf('+ -')
LBRK = Suppress('[')
RBRK = Suppress(']')

integer_constant = Word(nums)
fractional_constant = Combine(Optional(integer_constant) + '.' + integer_constant) \
                    ^ Combine(integer_constant + '.')
number = Combine(Optional(sign) + integer_constant) \
       ^ Combine(Optional(sign) + fractional_constant)
number.addParseAction(lambda t: float(t[0]))
string_ = dblQuotedString.addParseAction(lambda t: t[0][1:-1])

EntityName = (Literal('*') | Word(alphanums)).setResultsName('EntityName')
AttribName = Word(alphas)
RelationExpr = oneOf(['==', '!=', '^', '$', '?'])
# == equal
# != not equal
# ^ starts with
# $ ends with
# ? contains
AttribValue = string_ | number
AttribQuery = Group(AttribName + RelationExpr + AttribValue)
AttribQuerys = OneOrMore(AttribQuery).setResultsName('Attributes')
EntityQueryParser = EntityName + Optional(LBRK + AttribQuerys + RBRK)
