import kivy
from kivy.vector import Vector

import math

# These methods are translated from the examples provided at:
# http://www.gamasutra.com/view/feature/3015/pool_hall_lessons_fast_accurate_.php

def collisionDistanceForMovingCircleFixedCircle(moving, fixed):
  movevec = Vector(moving.velocity)
  C = Vector(fixed.center) - Vector(moving.center)


  dist = C.length()
  sumRadii = fixed.size[0]/2 + moving.size[0]/2
  dist -= sumRadii
  if movevec.length() < dist:
    return False

  N = movevec.normalize()

  D = N.dot(C)

  if D <= 0:
    return False

  lengthC = C.length()

  F = (lengthC * lengthC) - (D * D)

  sumRadiiSquared = sumRadii * sumRadii

  if F >= sumRadiiSquared:
    return False

  T = sumRadiiSquared - F

  if T < 0:
    return False

  distance = D - math.sqrt(T)

  mag = movevec.length()

  if mag < distance:
    return False

  return movevec.normalize() * distance

def calculateBounceVelocity(moving, fixed):
  N = (Vector(moving.center) - Vector(fixed.center)).normalize()

  v1 = Vector(moving.velocity)

  a1 = v1.dot(N)
  a2 = 0.0

  optimizedP = (2.0 * (a1 - a2)) / (moving.mass + fixed.mass)

  v1Prime = v1 - optimizedP * fixed.mass * N

  return v1Prime
