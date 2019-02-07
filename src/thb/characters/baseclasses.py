# -*- coding: utf-8 -*-

# -- stdlib --
from collections import defaultdict
from typing import Dict, Iterable, List, Set, Type

# -- third party --
# -- own --
from game.autoenv import EventHandler, GameObject
from game.base import AbstractPlayer
from thb.cards.base import Skill
from utils.misc import partition


# -- code --
# common, id8, faith, kof, 3v3, testing
# -id8, ...
characters_by_category: Dict[str, Set[Type['Character']]] = defaultdict(set)


class Character(GameObject):
    # ----- Class Variables -----
    character_classes: Dict[str, Type['Character']] = {}
    eventhandlers_required: List[Type[EventHandler]] = []
    categories: Iterable[str]

    # ----- Instance Variables -----
    disabled_skills: Dict[str, Set[Type[Skill]]]

    def __init__(self, player: AbstractPlayer):
        self.player = player
        self.disabled_skills = defaultdict(set)

    def get_skills(self, skill):
        return [s for s in self.skills if issubclass(s, skill)]

    def has_skill(self, skill):
        if self.dead:
            return False

        if any(issubclass(skill, s) for l in self.disabled_skills.values() for s in l):
            return False

        return self.get_skills(skill)

    def disable_skill(self, skill: Type[Skill], reason: str):
        self.disabled_skills[reason].add(skill)

    def reenable_skill(self, reason):
        self.disabled_skills.pop(reason, '')

    def __repr__(self):
        return '<Char: {}>'.format(self.__class__.__name__)

    def __getattr__(self, k):
        return getattr(self.player, k)

    def __setattr__(self, k, v):
        GameObject.__setattr__(self, k, v)
        if not k.startswith('__') and k.endswith('__'):
            assert not hasattr(self.player, k)


def register_character_to(*cats):
    sets = [characters_by_category[c] for c in set(cats)]

    def register(cls: Type[Character]):
        Character.character_classes[cls.__name__] = cls

        for s in sets:
            s.add(cls)

        cls.categories = cats
        return cls

    return register


def get_characters(*categories):
    cats: Set[str] = set(categories)
    chars: Set[Type[Character]] = set()
    pos, neg = partition(lambda c: not c.startswith('-'), cats)
    chars.update(*[characters_by_category[c] for c in pos])
    chars.difference_update(*[characters_by_category['-' + c] for c in pos])
    chars.difference_update(*[characters_by_category[c.strip('-')] for c in neg])
    return list(sorted(chars, key=lambda i: i.__name__))


def mixin_character(g, player, char_cls):
    assert issubclass(char_cls, Character)

    player.index = g.get_playerid(player)

    old = None
    if isinstance(player, Character):
        old = player.__class__
        player = player.player

    new = char_cls(player)
    new.skills = list(char_cls.skills)
    new.maxlife = char_cls.maxlife
    new.life = char_cls.maxlife
    new.dead = False
    return new, old
