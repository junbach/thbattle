# -*- coding: utf-8 -*-
from __future__ import annotations

# -- stdlib --
# -- third party --
# -- own --
from thb.actions import DrawCards, PlayerTurn, PrepareStage, UserAction, ttags
from thb.cards.base import Skill, t_None
from thb.characters.base import Character, register_character_to
from thb.mode import THBEventHandler


# -- code --
class UltimateSpeed(Skill):
    associated_action = None
    skill_category = ['character', 'passive']
    target = t_None()


class UltimateSpeedAction(UserAction):
    def apply_action(self):
        g = self.game
        return g.process_action(DrawCards(self.target, 1))


class UltimateSpeedHandler(THBEventHandler):
    interested = ['choose_target', 'post_calcdistance']

    def handle(self, evt_type, arg):
        def is_card(card):
            return 'skill' not in card.category or 'treat_as' in card.category

        if evt_type == 'post_calcdistance':
            src, card, dist = arg

            if not is_card(card):
                return arg

            if ttags(src)['aya_count'] < 2:
                return arg

            g = self.game
            current = PlayerTurn.get_current(g).target
            if current is not src:
                return arg

            for k in dist:
                dist[k] = 0

        elif evt_type == 'choose_target':
            lca, _ = arg
            g = self.game

            if not is_card(lca.card):
                return arg

            src = lca.source

            if not src.has_skill(UltimateSpeed): return arg

            # if not isinstance(lca, ActionStageLaunchCard):
            try:
                current = PlayerTurn.get_current(g).target
            except IndexError:
                return arg

            if current is not src:
                return arg

            ttags(src)['aya_count'] += 1
            if ttags(src)['aya_count'] == 2:
                g.process_action(UltimateSpeedAction(src, src))

        return arg


@register_character_to('common')
class Aya(Character):
    skills = [UltimateSpeed]
    eventhandlers = [UltimateSpeedHandler]
    maxlife = 4
