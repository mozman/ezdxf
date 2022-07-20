# Source: https://github.com/mapbox/earcut
# License: ISC License (MIT compatible)
#
# Copyright (c) 2016, Mapbox
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
# THIS SOFTWARE.
#
# Translation to Python:
# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import List, Optional
import math


class Node:
    def __init__(self, i: int, x: float, y: float):
        self.i: int = i

        # vertex coordinates
        self.x: float = x
        self.y: float = y

        # previous and next vertex nodes in a polygon ring
        self.prev: Optional[Node] = None
        self.next: Optional[Node] = None

        # z-order curve value
        self.z: int = 0

        # previous and next nodes in z-order
        self.prevZ: Optional[int] = None
        self.nextZ: Optional[int] = None

        # indicates whether self is a steiner point
        self.steiner: bool = False


def earcut(
    data: List[float], holeIndices: List[int], dim: int = 2
) -> List[int]:
    hasHoles: bool = len(holeIndices) > 0
    outerLen: int = holeIndices[0] * dim if hasHoles else len(data)
    # exterior vertices in counter-clockwise order
    outerNode: Node = linkedList(data, 0, outerLen, dim, ccw=True)
    triangles: List[int] = []

    if not outerNode or outerNode.next == outerNode.prev:
        return triangles

    minX: float = 0.0
    minY: float = 0.0
    maxX: float = 0.0
    maxY: float = 0.0
    invSize: float = 0.0

    if hasHoles:
        outerNode = eliminateHoles(data, holeIndices, outerNode, dim)

    # if the shape is not too simple, we'll use z-order curve hash later;
    # calculate polygon bbox
    if len(data) > 80 * dim:
        minX = maxX = data[0]
        minY = maxY = data[1]

        for i in range(outerLen):
            x = data[i]
            y = data[i + 1]
            minX = min(minX, x)
            minY = min(minY, y)
            maxX = max(maxX, x)
            maxY = max(maxY, y)

        # minX, minY and invSize are later used to transform coords into
        # integers for z-order calculation
        invSize = max(maxX - minX, maxY - minY)
        invSize = 32767 / invSize if invSize != 0 else 0

    earcutLinked(outerNode, triangles, dim, minX, minY, invSize, 0)
    return triangles


def linkedList(
    data: List[float], start: int, end: int, dim: int, ccw: bool
) -> Node:
    """Create a circular doubly linked list from polygon points in the specified
    winding order
    """
    last: Optional[Node] = None
    sa = signedArea(data, start, end, dim)
    if ccw is (sa < 0):
        for i in range(start, end, dim):
            last = insertNode(i, data[i], data[i + 1], last)
    else:
        for i in range(end - dim, start - 1, -dim):
            last = insertNode(i, data[i], data[i + 1], last)

    # open polygon: where the 1st vertex is not coincident with the last vertex
    if last and equals(last, last.next):
        removeNode(last)
        last = last.next
    return last


def signedArea(data: List[float], start: int, end: int, dim: int) -> float:
    s: float = 0.0
    j: int = end - dim
    for i in range(start, end, dim):
        # error in mapbox code: (data[j] - data[i])
        s += (data[i] - data[j]) * (data[i + 1] + data[j + 1])
        j = i
    # s < 0 is counter-clockwise
    # s > 0 is clockwise
    return s


def area(p: Node, q: Node, r: Node) -> float:
    """Returns signed area of a triangle"""
    return (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)


def isValidDiagonal(a: Node, b: Node):
    """Check if a diagonal between two polygon nodes is valid (lies in polygon
    interior)
    """
    return (
        a.next.i != b.i
        and a.prev.i != b.i
        and not intersectsPolygon(a, b)  # doesn't intersect other edges
        and (
            locallyInside(a, b)
            and locallyInside(b, a)
            and middleInside(a, b)
            and (
                area(a.prev, a, b.prev) or area(a, b.prev, b)
            )  # does not create opposite-facing sectors
            or equals(a, b)
            and area(a.prev, a, a.next) > 0
            and area(b.prev, b, b.next) > 0
        )  # special zero-length case
    )


def intersectsPolygon(a: Node, b: Node) -> bool:
    """Check if a polygon diagonal intersects any polygon segments"""
    p = a
    while True:
        if (
            p.i != a.i
            and p.next.i != a.i
            and p.i != b.i
            and p.next.i != b.i
            and intersects(p, p.next, a, b)
        ):
            return True
        p = p.next
        if p is a:
            break
    return False


def equals(p1: Node, p2: Node) -> bool:
    return p1.x == p2.x and p1.y == p2.y


def sign(num: float) -> int:
    if num < 0.0:
        return -1
    if num > 0.0:
        return 1
    return 0


def onSegment(p: Node, q: Node, r: Node) -> bool:
    return (
        max(p.x, r.x) >= q.x >= min(p.x, r.x)
        and max(p.y, r.y) >= q.y >= min(p.y, r.y)
    )


def intersects(p1: Node, q1: Node, p2: Node, q2: Node) -> bool:
    """check if two segments intersect"""
    o1 = sign(area(p1, q1, p2))
    o2 = sign(area(p1, q1, q2))
    o3 = sign(area(p2, q2, p1))
    o4 = sign(area(p2, q2, q1))

    if o1 != o2 and o3 != o4:
        return True  # general case

    if o1 == 0 and onSegment(p1, p2, q1):
        return True  # p1, q1 and p2 are collinear and p2 lies on p1q1
    if o2 == 0 and onSegment(p1, q2, q1):
        return True  # p1, q1 and q2 are collinear and q2 lies on p1q1
    if o3 == 0 and onSegment(p2, p1, q2):
        return True  # p2, q2 and p1 are collinear and p1 lies on p2q2
    if o4 == 0 and onSegment(p2, q1, q2):
        return True  # p2, q2 and q1 are collinear and q1 lies on p2q2
    return False


def compareX(a: Node, b: Node) -> float:
    return a.x - b.x


def insertNode(i: int, x: float, y: float, last: Optional[Node]) -> Node:
    """create a node and optionally link it with previous one (in a circular doubly linked list)"""
    p = Node(i, x, y)

    if last is None:
        p.prev = p
        p.next = p
    else:
        p.next = last.next
        p.prev = last
        last.next.prev = p
        last.next = p
    return p


def removeNode(p: Node) -> None:
    p.next.prev = p.prev
    p.prev.next = p.next

    if p.prevZ:
        p.prevZ.nextZ = p.nextZ
    if p.nextZ:
        p.nextZ.prevZ = p.prevZ


def eliminateHoles(
    data: List[float], holeIndices: List[int], outerNode: Node, dim: int
) -> Node:
    """link every hole into the outer loop, producing a single-ring polygon
    without holes
    """
    queue = []
    length = len(holeIndices)
    for i in range(len(holeIndices)):
        start = holeIndices[i] * dim
        end = holeIndices[i + 1] * dim if (i < length - 1) else len(data)
        # hole vertices in clockwise order
        _list = linkedList(data, start, end, dim, ccw=False)
        if _list is _list.next:
            _list.steiner = True
        queue.append(getLeftmost(_list))
    queue.sort(key=lambda n: n.x)

    #  process holes from left to right
    for i in range(len(queue)):
        outerNode = eliminateHole(queue[i], outerNode)
    return outerNode


def eliminateHole(hole: Node, outerNode: Node) -> Node:
    """Find a bridge between vertices that connects hole with an outer ring and
    link it
    """
    bridge = findHoleBridge(hole, outerNode)
    if bridge is None:
        return outerNode

    bridgeReverse = splitPolygon(bridge, hole)

    # filter collinear points around the cuts
    filterPoints(bridgeReverse, bridgeReverse.next)
    return filterPoints(bridge, bridge.next)


def filterPoints(start: Optional[Node], end: Node = None) -> Optional[Node]:
    """eliminate colinear or duplicate points"""
    if start is None:
        return start
    if end is None:
        end = start

    p = start

    while True:
        again = False
        if not p.steiner and (
            equals(p, p.next) or area(p.prev, p, p.next) == 0
        ):
            removeNode(p)
            p = end = p.prev
            if p is p.next:
                break
            again = True
        else:
            p = p.next
        if not again or p is end:
            break
    return end


# main ear slicing loop which triangulates a polygon (given as a linked list)
def earcutLinked(
    ear: Optional[Node],
    triangles: List[int],
    dim: int,
    minX: float,
    minY: float,
    invSize: float,
    pass_: int,
) -> None:
    if ear is None:
        return

    # interlink polygon nodes in z-order
    if not pass_ and invSize:
        indexCurve(ear, minX, minY, invSize)

    stop = ear

    # iterate through ears, slicing them one by one
    while ear.prev is not ear.next:
        prev = ear.prev
        next = ear.next

        is_ear = (
            isEarHashed(ear, minX, minY, invSize) if invSize else isEar(ear)
        )
        if is_ear:
            # cut off the triangle
            triangles.append(prev.i // dim)
            triangles.append(ear.i // dim)
            triangles.append(next.i // dim)

            removeNode(ear)

            # skipping the next vertex leads to less sliver triangles
            ear = next.next
            stop = next.next
            continue

        ear = next

        # if we looped through the whole remaining polygon and can't find any more ears
        if ear is stop:
            # try filtering points and slicing again
            if not pass_:
                earcutLinked(
                    filterPoints(ear), triangles, dim, minX, minY, invSize, 1
                )

            # if this didn't work, try curing all small self-intersections locally
            elif pass_ == 1:
                ear = cureLocalIntersections(filterPoints(ear), triangles, dim)
                earcutLinked(ear, triangles, dim, minX, minY, invSize, 2)

            # as a last resort, try splitting the remaining polygon into two
            elif pass_ == 2:
                splitEarcut(ear, triangles, dim, minX, minY, invSize)
            break


def isEar(ear: Node) -> bool:
    """check whether a polygon node forms a valid ear with adjacent nodes"""
    a: Node = ear.prev
    b: Node = ear
    c: Node = ear.next

    if area(a, b, c) >= 0:
        return False  # reflex, can't be an ear

    # now make sure we don't have other points inside the potential ear
    ax = a.x
    bx = b.x
    cx = c.x
    ay = a.y
    by = b.y
    cy = c.y

    # triangle bbox; min & max are calculated like this for speed
    x0 = min(ax, bx, cx)
    x1 = max(ax, bx, cx)
    y0 = min(ay, by, cy)
    y1 = max(ay, by, cy)
    p: Node = c.next

    while p is not a:
        if (
            x0 <= p.x <= x1
            and y0 <= p.y <= y1
            and pointInTriangle(ax, ay, bx, by, cx, cy, p.x, p.y)
            and area(p.prev, p, p.next) >= 0
        ):
            return False
        p = p.next

    return True


def isEarHashed(ear: Node, minX: float, minY: float, invSize: float):
    a: Node = ear.prev
    b: Node = ear
    c: Node = ear.next

    if area(a, b, c) >= 0:
        return False  # reflex, can't be an ear

    ax = a.x
    bx = b.x
    cx = c.x
    ay = a.y
    by = b.y
    cy = c.y

    # triangle bbox; min & max are calculated like this for speed
    x0 = min(ax, bx, cx)
    x1 = max(ax, bx, cx)
    y0 = min(ay, by, cy)
    y1 = max(ay, by, cy)

    # z-order range for the current triangle bbox;
    minZ = zOrder(x0, y0, minX, minY, invSize)
    maxZ = zOrder(x1, y1, minX, minY, invSize)

    p: Optional[Node] = ear.prevZ
    n: Optional[Node] = ear.nextZ

    # look for points inside the triangle in both directions
    while p and p.z >= minZ and n and n.z <= maxZ:
        if (
            x0 <= p.x <= x1
            and y0 <= p.y <= y1
            and p is not a
            and p is not c
            and pointInTriangle(ax, ay, bx, by, cx, cy, p.x, p.y)
            and area(p.prev, p, p.next) >= 0
        ):
            return False
        p = p.prevZ

        if (
            x0 <= n.x <= x1
            and y0 <= n.y <= y1
            and n is not a
            and n is not c
            and pointInTriangle(ax, ay, bx, by, cx, cy, n.x, n.y)
            and area(n.prev, n, n.next) >= 0
        ):
            return False
        n = n.nextZ

    # look for remaining points in decreasing z-order
    while p and p.z >= minZ:
        if (
            x0 <= p.x <= x1
            and y0 <= p.y <= y1
            and p is not a
            and p is not c
            and pointInTriangle(ax, ay, bx, by, cx, cy, p.x, p.y)
            and area(p.prev, p, p.next) >= 0
        ):
            return False
        p = p.prevZ

    # look for remaining points in increasing z-order
    while n and n.z <= maxZ:
        if (
            x0 <= n.x <= x1
            and y0 <= n.y <= y1
            and n is not a
            and n is not c
            and pointInTriangle(ax, ay, bx, by, cx, cy, n.x, n.y)
            and area(n.prev, n, n.next) >= 0
        ):
            return False
        n = n.nextZ
    return True


def getLeftmost(start: Node) -> Node:
    """Find the leftmost node of a polygon ring"""
    p = start
    leftmost = start
    while True:
        if p.x < leftmost.x or (p.x == leftmost.x and p.y < leftmost.y):
            leftmost = p
        p = p.next
        if p is start:
            break
    return leftmost


def pointInTriangle(
    ax: float,
    ay: float,
    bx: float,
    by: float,
    cx: float,
    cy: float,
    px: float,
    py: float,
) -> bool:
    """Check if a point lies within a convex triangle"""
    return (
        (cx - px) * (ay - py) >= (ax - px) * (cy - py)
        and (ax - px) * (by - py) >= (bx - px) * (ay - py)
        and (bx - px) * (cy - py) >= (cx - px) * (by - py)
    )


def sectorContainsSector(m: Node, p: Node):
    """Whether sector in vertex m contains sector in vertex p in the same
    coordinates.
    """
    return area(m.prev, m, p.prev) < 0 and area(p.next, m, m.next) < 0


def indexCurve(start: Node, minX: float, minY: float, invSize: float):
    """Interlink polygon nodes in z-order"""
    p = start
    while True:
        if p.z == 0:
            p.z = zOrder(p.x, p.y, minX, minY, invSize)
        p.prevZ = p.prev
        p.nextZ = p.next
        p = p.next
        if p is start:
            break

    p.prevZ.nextZ = None
    p.prevZ = None

    sortLinked(p)


def zOrder(
    x0: float, y0: float, minX: float, minY: float, invSize: float
) -> int:
    """Z-order of a point given coords and inverse of the longer side of data
    bbox.
    """
    # coords are transformed into non-negative 15-bit integer range
    x = int((x0 - minX) * invSize)
    y = int((y0 - minY) * invSize)

    x = (x | (x << 8)) & 0x00FF00FF
    x = (x | (x << 4)) & 0x0F0F0F0F
    x = (x | (x << 2)) & 0x33333333
    x = (x | (x << 1)) & 0x55555555

    y = (y | (y << 8)) & 0x00FF00FF
    y = (y | (y << 4)) & 0x0F0F0F0F
    y = (y | (y << 2)) & 0x33333333
    y = (y | (y << 1)) & 0x55555555

    return x | (y << 1)


# Simon Tatham's linked list merge sort algorithm
# http://www.chiark.greenend.org.uk/~sgtatham/algorithms/listsort.html
def sortLinked(head: Node) -> Node:
    inSize = 1

    while True:
        p = head
        head = None
        tail = None
        numMerges = 0

        while p:
            numMerges += 1
            q = p
            pSize = 0
            for i in range(inSize):

                pSize += 1
                q = q.nextZ
                if not q:
                    break

            qSize = inSize
            while pSize > 0 or (qSize > 0 and q):
                if pSize != 0 and qSize == 0 or not q or p.z <= q.z:
                    e = p
                    p = p.nextZ
                    pSize -= 1
                else:
                    e = q
                    q = q.nextZ
                    qSize -= 1

                if tail:
                    tail.nextZ = e
                else:
                    head = e

                e.prevZ = tail
                tail = e

            p = q

        tail.nextZ = None
        inSize *= 2
        if numMerges <= 1:
            break

    return head


def splitPolygon(a: Node, b: Node) -> Node:
    """Link two polygon vertices with a bridge.

    If the vertices belong to the same ring, it splits polygon into two.
    If one belongs to the outer ring and another to a hole, it merges it into a
    single ring.
    """
    a2 = Node(a.i, a.x, a.y)
    b2 = Node(b.i, b.x, b.y)
    an = a.next
    bp = b.prev

    a.next = b
    b.prev = a

    a2.next = an
    an.prev = a2

    b2.next = a2
    a2.prev = b2

    bp.next = b2
    b2.prev = bp

    return b2


# go through all polygon nodes and cure small local self-intersections
def cureLocalIntersections(start: Node, triangles: List[int], dim: int) -> Node:
    p = start
    while True:
        a = p.prev
        b = p.next.next

        if (
            not equals(a, b)
            and intersects(a, p, p.next, b)
            and locallyInside(a, b)
            and locallyInside(b, a)
        ):
            triangles.append(a.i // dim)
            triangles.append(p.i // dim)
            triangles.append(b.i // dim)

            # remove two nodes involved
            removeNode(p)
            removeNode(p.next)
            p = start = b

        p = p.next
        if p is start:
            break
    return filterPoints(p)


def splitEarcut(
    start: Node,
    triangles: List[int],
    dim: int,
    minX: float,
    minY: float,
    invSize: float,
) -> None:
    """Try splitting polygon into two and triangulate them independently"""
    # look for a valid diagonal that divides the polygon into two
    a = start
    while True:
        b = a.next.next
        while b is not a.prev:
            if a.i != b.i and isValidDiagonal(a, b):
                # split the polygon in two by the diagonal
                c = splitPolygon(a, b)

                # filter colinear points around the cuts
                a = filterPoints(a, a.next)
                c = filterPoints(c, c.next)

                # run earcut on each half
                earcutLinked(a, triangles, dim, minX, minY, invSize, 0)
                earcutLinked(c, triangles, dim, minX, minY, invSize, 0)
                return
            b = b.next
        a = a.next
        if a is start:
            break


# David Eberly's algorithm for finding a bridge between hole and outer polygon
def findHoleBridge(hole: Node, outerNode: Node) -> Optional[Node]:
    p = outerNode
    hx = hole.x
    hy = hole.y
    qx = math.inf
    m: Optional[Node] = None
    # find a segment intersected by a ray from the hole's leftmost point to the left;
    # segment's endpoint with lesser x will be potential connection point
    while True:
        if hy <= p.y and hy >= p.next.y and p.next.y != p.y:
            x = p.x + (hy - p.y) * (p.next.x - p.x) / (p.next.y - p.y)
            if hx >= x > qx:
                qx = x
                m = p if p.x < p.next.x else p.next
                if x == hx:
                    return (
                        m  # hole touches outer segment; pick leftmost endpoint
                    )
        p = p.next
        if p is outerNode:
            break

    if m is None:
        return None

    # look for points inside the triangle of hole point, segment intersection and endpoint;
    # if there are no points found, we have a valid connection;
    # otherwise choose the point of the minimum angle with the ray as connection point
    stop = m
    mx = m.x
    my = m.y
    tanMin = math.inf
    p = m

    while True:
        if (
            hx >= p.x >= mx
            and hx != p.x
            and pointInTriangle(
                hx if hy < my else qx,
                hy,
                mx,
                my,
                qx if hy < my else hx,
                hy,
                p.x,
                p.y,
            )
        ):

            tan = abs(hy - p.y) / (hx - p.x)  # tangential

            if locallyInside(p, hole) and (
                tan < tanMin
                or (
                    tan == tanMin
                    and (
                        p.x > m.x or (p.x == m.x and sectorContainsSector(m, p))
                    )
                )
            ):
                m = p
                tanMin = tan

        p = p.next
        if p is stop:
            break
    return m


def locallyInside(a: Node, b: Node) -> bool:
    """Check if a polygon diagonal is locally inside the polygon"""
    return (
        area(a, b, a.next) >= 0 and area(a, a.prev, b) >= 0
        if area(a.prev, a, a.next) < 0
        else area(a, b, a.prev) < 0 or area(a, a.next, b) < 0
    )


def middleInside(a: Node, b: Node) -> bool:
    """Check if the middle point of a polygon diagonal is inside the polygon"""
    p = a
    inside = False
    px = (a.x + b.x) / 2
    py = (a.y + b.y) / 2
    while True:
        if (
            ((p.y > py) != (p.next.y > py))
            and p.next.y != p.y
            and (px < (p.next.x - p.x) * (py - p.y) / (p.next.y - p.y) + p.x)
        ):
            inside = not inside
        p = p.next
        if p is a:
            break

    return inside
