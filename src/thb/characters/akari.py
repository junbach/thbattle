# -*- coding: utf-8 -*-

# -- stdlib --
from typing import List, Type

# -- third party --
# -- own --
from game.autoenv import EventHandler
from thb.cards import Skill, t_None
from thb.characters.baseclasses import Character, register_character_to


# -- code --
class AkariSkill(Skill):
    associated_action = None
    skill_category: List[str] = []
    target = t_None


@register_character_to('special')
class Akari(Character):
    # dummy player for hidden choices
    skills = [AkariSkill]
    eventhandlers_required: List[Type[EventHandler]] = []
    maxlife = 0
