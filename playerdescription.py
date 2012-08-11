#!/usr/bin/env python3

import json

# I used it like this:
# encode:
# PlayerDescriptionEncoder().encode(description))

###########################
# A Player's Description
# comprehensive
# includes everything the server needs to know!
#
# PlayerDescription contains: 
# * name, camp, role (mole or not)
# * abilities, skills ranges
###########################
class PlayerDescription:
  def __init__(self, name, camp, role, abilities, skills):
    self.name = name
    self.camp = camp
    self.role = role
    self.abilities = abilities
    self.skills = skills

############################      
# JSON encoder for PlayerDescription
# just includes all attributes of a PlayerDescription
############################
class PlayerDescriptionEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, PlayerDescription):
      return[obj.name, obj.camp, obj.role, obj.abilities, obj.skills]
    return json.JSONEncoder.default(self, obj)

###########################
# Skill
#
# Contains: skill type, passive, range
###########################
class Skill:
  def __init__(self, skill, passive, rangeMin, rangeMax):
    self.skill = skill
    self.passive = passive
    self.rangeMin = rangeMin
    self.rangeMax = rangeMax

############################      
# JSON encoder for Skill
# just includes all attributes of a Skill
############################
class SkillEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Skill):
      return[obj.skill, obj.passive, obj.rangeMin, obj.rangeMax]
    return json.JSONEncoder.default(self, obj)
