# faqs.org

Source: http://www.faqs.org/faqs/graphics/algorithms-faq/

## Subject 1.03: How do I find intersections of 2 2D line segments?

This problem can be extremely easy or extremely difficult; it
depends on your application. If all you want is the intersection
point, the following should work:

Let A,B,C,D be 2-space position vectors.  Then the directed line
segments AB & CD are given by:

    AB=A+r(B-A), r in [0,1]
    CD=C+s(D-C), s in [0,1]

If AB & CD intersect, then

    A+r(B-A)=C+s(D-C), or

    Ax+r(Bx-Ax)=Cx+s(Dx-Cx)
    Ay+r(By-Ay)=Cy+s(Dy-Cy)  for some r,s in [0,1]

Solving the above for r and s yields

        (Ay-Cy)(Dx-Cx)-(Ax-Cx)(Dy-Cy)
    r = -----------------------------  (eqn 1)
        (Bx-Ax)(Dy-Cy)-(By-Ay)(Dx-Cx)

        (Ay-Cy)(Bx-Ax)-(Ax-Cx)(By-Ay)
    s = -----------------------------  (eqn 2)
        (Bx-Ax)(Dy-Cy)-(By-Ay)(Dx-Cx)

Let P be the position vector of the intersection point, then

    P=A+r(B-A) or

    Px=Ax+r(Bx-Ax)
    Py=Ay+r(By-Ay)

By examining the values of r & s, you can also determine some
other limiting conditions:

    If 0<=r<=1 & 0<=s<=1, intersection exists
        r<0 or r>1 or s<0 or s>1 line segments do not intersect

    If the denominator in eqn 1 is zero, AB & CD are parallel
    If the numerator in eqn 1 is also zero, AB & CD are collinear.

If they are collinear, then the segments may be projected to the x- 
or y-axis, and overlap of the projected intervals checked.

If the intersection point of the 2 lines are needed (lines in this
context mean infinite lines) regardless whether the two line
segments intersect, then

    If r>1, P is located on extension of AB
    If r<0, P is located on extension of BA
    If s>1, P is located on extension of CD
    If s<0, P is located on extension of DC


Also note that the denominators of eqn 1 & 2 are identical.

## Subject 1.04: How do I generate a circle through three points?

Let the three given points be a, b, c.  Use _0 and _1 to represent
x and y coordinates. The coordinates of the center p=(p_0,p_1) of
the circle determined by a, b, and c are:
 
    A = b_0 - a_0;
    B = b_1 - a_1;
    C = c_0 - a_0;
    D = c_1 - a_1;
    
    E = A*(a_0 + b_0) + B*(a_1 + b_1);
    F = C*(a_0 + c_0) + D*(a_1 + c_1);
    
    G = 2.0*(A*(c_1 - b_1)-B*(c_0 - b_0));
    
    p_0 = (D*E - B*F) / G;
    p_1 = (A*F - C*E) / G;
  
 If G is zero then the three points are collinear and no finite-radius
 circle through them exists.  Otherwise, the radius of the circle is:
 
    r^2 = (a_0 - p_0)^2 + (a_1 - p_1)^2  
    

## Subject 2.03: How do I find if a point lies within a polygon?

The definitive reference is "Point in Polygon Strategies" by
Eric Haines [Gems IV]  pp. 24-46.  Now also at 
   http://www.erichaines.com/ptinpoly.
The code in the Sedgewick book Algorithms (2nd Edition, p.354) fails
under certain circumstances.  See 
   http://condor.informatik.Uni-Oldenburg.DE/~stueker/graphic/index.html
for a discussion.

The essence of the ray-crossing method is as follows.
Think of standing inside a field with a fence representing the polygon. 
Then walk north. If you have to jump the fence you know you are now 
outside the poly. If you have to cross again you know you are now 
inside again; i.e., if you were inside the field to start with, the total 
number of fence jumps you would make will be odd, whereas if you were 
ouside the jumps will be even.

The code below is from Wm. Randolph Franklin <wrf@ecse.rpi.edu>
(see URL below) with some minor modifications for speed.  It returns 
1 for strictly interior points, 0 for strictly exterior, and 0 or 1 
for points on the boundary.  The boundary behavior is complex but 
determined; in particular, for a partition of a region into polygons, 
each point is "in" exactly one polygon.  
(See p.243 of [O'Rourke (C)] for a discussion of boundary behavior.)

    int pnpoly(int npol, float *xp, float *yp, float x, float y)
    {
      int i, j, c = 0;
      for (i = 0, j = npol-1; i < npol; j = i++) {
        if ((((yp[i]<=y) && (y<yp[j])) ||
             ((yp[j]<=y) && (y<yp[i]))) &&
            (x < (xp[j] - xp[i]) * (y - yp[i]) / (yp[j] - yp[i]) + xp[i]))
    
          c = !c;
      }
      return c;
    }

The code may be further accelerated, at some loss in clarity, by
avoiding the central computation when the inequality can be deduced,
and by replacing the division by a multiplication for those processors
with slow divides.  For code that distinguishes strictly interior
points from those on the boundary, see [O'Rourke (C)] pp. 239-245.
For a method based on winding number, see Dan Sunday,
"Fast Winding Number Test for Point Inclusion in a Polygon,"
http://softsurfer.com/algorithms.htm, March 2001.

## NURBS from Circular Arc
 
Source: [ResearchGate.net](https://www.researchgate.net/publication/283497458_ONE_METHOD_FOR_REPRESENTING_AN_ARC_OF_ELLIPSE_BY_A_NURBS_CURVE/citation/download)

- TY  - BOOK
- AU  - Petkov, Emiliyan
- AU  - Cekov, Liuben
- PY  - 2005/01/01
- T1  - ONE METHOD FOR REPRESENTING AN ARC OF ELLIPSE BY A NURBS CURVE
- DO  - 10.13140/RG.2.1.4541.6403
