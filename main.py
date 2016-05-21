#!/usr/bin/env python

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
from kivy.vector import Vector
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.config import Config

Config.set('graphics', 'fullscreen', 'auto')

import util, math, sys

GRAVITATIONAL_CONSTANT = 5.0
ENERGY_LOST            = 0.9

class AimLine(Widget):
  start_pt = ListProperty([0, 0])
  end_pt = ListProperty([0, 0])

  def __init__(self, start_pt, **kwargs):
    super(AimLine, self).__init__(**kwargs)
    self.start_pt = start_pt
    self.end_pt = start_pt

class StartZone(Widget):
  pass

class EndZone(Widget):
  pass

class DynamicPhysicsEntity(Widget):
  velocity_x = NumericProperty(0)
  velocity_y = NumericProperty(0)
  velocity = ReferenceListProperty(velocity_x, velocity_y)

  def simulate(self, otherEntities):
    distTraveled = Vector(*self.velocity)
    collidedEntity = False

    for entity in otherEntities:
      result = util.collisionDistanceForMovingCircleFixedCircle(self, entity)
      if result:
        if result.length2() < distTraveled.length2():
          distTraveled = result
          collidedEntity = entity

    self.pos = distTraveled + self.pos

    if collidedEntity:
      self.velocity = util.calculateBounceVelocity(self, collidedEntity) * ENERGY_LOST
      self.pos = Vector(self.pos) + Vector(self.velocity) * (1 - (distTraveled.length() / Vector(self.velocity).length()))


  def move(self):
    self.pos = Vector(*self.velocity) + self.pos

  def applyForce(self, force):
    dx, dy = force/self.mass
    self.velocity_x += dx
    self.velocity_y += dy

  # Assumes both self and other are circles
  def collide_widget(self, other):

    return (Vector(self.center) - Vector(other.center)).length() < self.size[0]/2 + other.size[0]/2

  def collide_point(self, point):
    return (Vector(self.center) - Vector(point)).length() < self.size[0]/2


class Control(Widget):
  dynamicEntities = ListProperty([])
  satellite = ObjectProperty(None)
  startZone = ObjectProperty(None)
  endZone = ObjectProperty(None)

  def reset(self):
    self.satellite.center = self.center_x+10, 10
    self.paused = True
    self.not_fired = True
    self.aim_line = None

  # Assumes a single satellite
  def launchSatellite(self, vel=(1.0,0), pos=(100, 100)):
    self.satellite.center = pos
    self.satellite.velocity = vel

  # Currently assumes a single satellite, multiple planets
  def simulatePhysics(self):
    for entity in self.dynamicEntities:
      if entity.canMove:
        self.simulateGravity(entity)

  def simulateGravity(self, entity):
    for other in self.dynamicEntities:
      if other != entity:
        force = self.calculateGravityForce(entity, other)
        entity.applyForce(force)

  def calculateGravityForce(self, on, by):
    path = Vector(by.center) - Vector(on.center)
    return GRAVITATIONAL_CONSTANT * by.mass * path.normalize() / path.length2()

  # Assumes a single satellite
  def update(self, *args):
    if self.paused:
      return
    if self.endZone.collide_widget(self.satellite):
      self.victory()
    self.simulatePhysics()
    others = list(self.dynamicEntities)
    others.remove(self.satellite)
    self.satellite.simulate(others)

  def add_aim_line(self, aim_line):
    self.aim_line = (aim_line)
    self.add_widget(aim_line)

  def on_touch_down(self, touch):
    if not self.startZone.collide_point(touch.pos[0], touch.pos[1]):
      return
    if touch.is_double_tap:
      self.reset()
    elif self.not_fired:
      self.add_aim_line(AimLine(start_pt=touch.pos))

  def on_touch_move(self, touch):
    if not self.aim_line:
      return

    try:
      self.aim_line.end_pt = touch.pos
    except (KeyError), e:
      pass

  def on_touch_up(self, touch):
    if not self.aim_line or not self.not_fired:
      return

    start_v = Vector(self.aim_line.start_pt)
    end_v = Vector(self.aim_line.end_pt)

    velocity_v = start_v - end_v
    l = velocity_v.length()
    if l == 0.:
      return

    velocity_v /= math.sqrt(l)
    velocity_v /= 5

    self.launchSatellite(vel=velocity_v, pos=self.aim_line.start_pt)
    self.not_fired = False
    self.paused = False

    self.remove_aim_line(self.aim_line)

  def remove_aim_line(self, aim_line):
    self.remove_widget(aim_line)
    self.aim_line = None

  def victory(self):
    sys.exit(0)


Factory.register("DynamicPhysicsEntity", DynamicPhysicsEntity)
Factory.register("Control", Control)
Factory.register("StartZone", StartZone)
Factory.register("EndZone", EndZone)

class GravityApp(App):
  def build(self):
    game = Control()
    game.reset()
    game.launchSatellite(Vector(2, 1))
    Clock.schedule_interval(game.update, 1.0/60.0)
    return game

if __name__ == '__main__':
  GravityApp().run()
