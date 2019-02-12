# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-12
# concept for new entity system

# Goals:
# ------
#
# 1. Store DXF entities as wrapped entities in the EntityDB with LAZY SETUP, load time should be fast and most entities
#    are never touched - especially when only data querying
# 2. Cython optimization as secondary goal in mind, but avoid manual memory management (malloc() and free()), use array
# 3.
