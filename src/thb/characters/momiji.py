# -*- coding: utf-8 -*-
from __future__ import absolute_import

# -- stdlib --
import itertools

# -- third party --
# -- own --
from game.autoenv import EventHandler, Game, sync_primitive, user_input
from thb.actions import ActionStage, Damage, FinalizeStage, GenericAction, LaunchCard, ShowCards
from thb.actions import UserAction, migrate_cards, user_choose_cards
from thb.cards import AttackCard, CardList, DuelCard, Skill, TreatAs, VirtualCard, t_None
from thb.characters.baseclasses import Character, register_character_to
from thb.inputlets import ChooseOptionInputlet


# -- code --
class DisarmHideAction(UserAction):
    def __init__(self, source, target, cards):
        self.source = source
        self.target = target
        self.cards = cards

    def apply_action(self):
        tgt = self.target
        cl = getattr(tgt, 'momiji_sentry_cl', None)
        if cl is None:
            cl = CardList(tgt, 'momiji_sentry_cl')
            tgt.momiji_sentry_cl = cl
            tgt.showncardlists.append(cl)

        migrate_cards(self.cards, cl)
        return True


class DisarmReturningAction(GenericAction):
    def apply_action(self):
        tgt = self.target
        cl = getattr(tgt, 'momiji_sentry_cl', None)
        cl and migrate_cards(cl, tgt.cards, unwrap=True)
        return True


class DisarmHandler(EventHandler):
    interested = ('action_after',)
    card_usage = 'launch'

    def handle(self, evt_type, act):
        if evt_type == 'action_after' and isinstance(act, Damage):
            g = Game.getgame()
            src, tgt = act.source, act.target
            if not (src and src.has_skill(Disarm)): return act
            if tgt.dead: return act
            pact = g.action_stack[-1]
            pcard = getattr(pact, 'associated_card', None)
            if not pcard: return act

            if not pcard.is_card(AttackCard) and not (pcard.is_card(DuelCard) and pact.source is src):
                return act

            if not user_input([src], ChooseOptionInputlet(self, (False, True))):
                return act

            cl = list(tgt.cards) + list(tgt.showncards)
            g.process_action(ShowCards(tgt, cl, [src]))

            if g.SERVER_SIDE:
                l = [c.is_card(AttackCard) or 'spellcard' in c.category for c in cl]
            else:
                l = [False for c in cl]

            l = sync_primitive(l, g.players)
            cl = list(itertools.compress(cl, l))
            g.process_action(DisarmHideAction(src, tgt, cl))

        elif evt_type == 'action_after' and isinstance(act, FinalizeStage):
            tgt = act.target
            g = Game.getgame()
            g.process_action(DisarmReturningAction(tgt, tgt))

        return act


class Disarm(Skill):
    associated_action = None
    skill_category = ('character', 'passive', 'compulsory')
    target = t_None


class SentryHandler(EventHandler):
    interested = ('action_apply',)
    card_usage = 'launch'

    def handle(self, evt_type, act):
        if evt_type == 'action_apply' and isinstance(act, ActionStage):
            g = Game.getgame()
            for p in g.players:
                if p.dead: continue
                if not p.has_skill(Sentry): continue

                tgt = act.target
                if p is tgt: continue
                self.target = tgt  # for ui

                dist = LaunchCard.calc_distance(p, AttackCard())
                if dist.get(tgt, 1) > 0: continue
                cl = user_choose_cards(self, p, ('cards', 'showncards', 'equips'))
                if not cl: continue
                c = SentryAttack.wrap(cl, tgt)
                g.process_action(LaunchCard(p, [tgt], c))

        return act

    def cond(self, cl):
        if not len(cl) == 1: return False
        return cl[0].is_card(AttackCard)

    def ask_for_action_verify(self, p, cl, tl):
        if not cl:
            return False

        tgt = self.target
        return LaunchCard(p, [tgt], cl[0]).can_fire()


class SentryAttack(TreatAs, VirtualCard):
    treat_as = AttackCard


class Sentry(Skill):
    associated_action = None
    skill_category = ('character', 'passive')
    target = t_None


class SharpEyeHandler(EventHandler):
    interested = ('calcdistance',)
    execute_after = ('AttackCardHandler', 'UFODistanceHandler')

    processing = False

    def handle(self, evt_type, arg):
        if self.processing:
            return arg

        elif evt_type == 'calcdistance':
            src, c, dist = arg
            if not src.has_skill(SharpEye): return arg
            if not c.is_card(AttackCard): return arg

            try:
                self.processing = True
                for p in dist:
                    if p is src: continue
                    d = LaunchCard.calc_distance(p, AttackCard())
                    if d[src] <= 0:
                        dist[p] = 0

            finally:
                self.processing = False

        return arg


class SharpEye(Skill):
    associated_action = None
    skill_category = ('character', 'passive', 'compulsory')
    target = t_None


@register_character_to('common')
class Momiji(Character):
    skills = [Disarm, Sentry, SharpEye]
    eventhandlers_required = [SentryHandler, DisarmHandler, SharpEyeHandler]
    maxlife = 4
