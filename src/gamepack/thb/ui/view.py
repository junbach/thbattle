# -*- coding: utf-8 -*-
import pyglet
from pyglet.gl import *
from pyglet import graphics
from pyglet.window import mouse
from client.ui.base import Control, message as ui_message
from client.ui.controls import *
from client.ui import resource as common_res
from client.ui import shaders, soundmgr
import resource as gres
from utils import IRP

from .game_controls import *

from game.autoenv import EventHandler, Action, GameError

import logging
log = logging.getLogger('THBattleUI')

import effects, inputs

from .. import actions

class UIEventHook(EventHandler):

    def evt_user_input(self, input):
        irp = IRP()
        irp.__dict__.update(input.__dict__)
        ui_message('evt_user_input', irp)
        irp.wait()
        input.input = irp.input
        return input

    # evt_user_input_timeout, InputControllers handle this

    def handle(self, evt, data):
        name = 'evt_%s' % evt
        try:
            f = getattr(self, name)
        except AttributeError:
            ui_message(name, data)
            return data

        return f(data)

class THBattleUI(Control):
    portrait_location = [
        (60, 300, Colors.blue),
        (250, 450, Colors.orange),
        (450, 450, Colors.blue),
        (640, 300, Colors.orange),
        (450, 150, Colors.blue),
        (250, 150, Colors.orange),
    ]

    def __init__(self, game, *a, **k):
        self.game = game
        self.hook = hook = UIEventHook()
        game.event_handlers.append(hook)
        Control.__init__(self, *a, **k)

        self.handcard_area = HandCardArea(
            parent=self, x=238, y=9, zindex=3,
            width=93*5+42, height=145,
        )

        self.deck_area = PortraitCardArea(
            parent=self, width=1, height=1,
            x=self.width//2, y=self.height//2, zindex=4,
        )

        @self.handcard_area.event
        def on_selection_change():
            self.dispatch_event('on_selection_change')

        self.dropcard_area = DropCardArea(
            parent=self, x=0, y=324, zindex=3,
            width=820, height=125,
        )

        class Animations(pyglet.graphics.Batch, Control):
            def __init__(self, **k):
                pyglet.graphics.Batch.__init__(self)
                Control.__init__(
                    self, x=0, y=0,
                    width=0, height=0, zindex=2,
                    **k
                )

            def hit_test(self, x, y):
                return False

        self.animations = Animations(parent=self)
        self.selecting_player = 0

    def init(self):
        orange, blue = Colors.orange, Colors.blue
        ports = self.char_portraits = [
            GameCharacterPortrait(parent=self, color=color, x=x, y=y, tag_placement=tp)
            for x, y, tp, color in (
                (3, 1, 'me', blue),
                (669, 280, 'left', orange),
                (155+180+180, 520, 'bottom', blue),
                (155+180, 520, 'bottom', orange),
                (155, 520, 'bottom', blue),
                (3, 280, 'right', orange),
            )[:len(self.game.players)]
        ] # FIXME: this is for testing

        pl = self.game.players
        shift = pl.index(self.game.me)
        for i, c in enumerate(ports):
            p = pl[(shift + i) % self.game.n_persons]
            c.player = p
            c.update()

        ports[0].equipcard_area.selectable = True # it's TheChosenOne

        self.begin_select_player()
        self.end_select_player()
        self.skill_box = SkillSelectionBox(
            parent=self, x=161, y=9, width=70, height=22*6-4
        )

        soundmgr.switch_bgm(gres.bgm_game)

    def player2portrait(self, p):
        for port in self.char_portraits:
            if port.player == p:
                break
        else:
            raise ValueError
        return port

    def update_skillbox(self):
        g = self.game
        skills = getattr(g.me, 'skills', None)
        if skills is None:
            # before girl chosen
            return
        skills = [(i, s) for i, s in enumerate(skills) if not getattr(s.ui_meta, 'no_display', False)]
        self.skill_box.set_skills(
            (s.ui_meta.name, i) for i, s in skills
        )

        for sb, (_, skill) in zip(self.skill_box.buttons, skills):
            if skill.ui_meta.clickable(g):
                sb.state = Button.NORMAL

    def on_message(self, _type, *args):
        if _type == 'evt_game_begin':
            for port in self.char_portraits:
                port.update()
            self.update_skillbox()

        elif _type == 'evt_action_before' and isinstance(args[0], actions.PlayerTurn):
            self.current_turn = args[0].target

        elif _type == 'player_change':
            for i, pd in enumerate(args[0]):
                if pd.get('id', -1) == -1:
                    p = self.game.players[i]
                    port = self.player2portrait(p)
                    port.dropped = True
                    port.update()

        if _type.startswith('evt_'):
            inputs.handle_event(self, _type[4:], args[0])
            effects.handle_event(self, _type[4:], args[0])

    def draw(self):
        self.draw_subcontrols()

    def ray(self, f, t):
        if f == t: return
        sp = self.player2portrait(f)
        dp = self.player2portrait(t)
        x0, y0 = sp.x + sp.width/2, sp.y + sp.height/2
        x1, y1 = dp.x + dp.width/2, dp.y + dp.height/2
        Ray(x0, y0, x1, y1, parent=self, zindex=10)

    def prompt(self, s):
        self.prompt_raw(u'|B|cff0000ff>> |r' + unicode(s) + u'\n')

    def prompt_raw(self, s):
        self.parent.events_box.append(s)

    def begin_select_player(self, disables=[]):
        #if self.selecting_player: return
        self.selecting_player = True
        #self.selected_players = []
        for p in self.game.players:
            try:
                port = self.player2portrait(p)
            except ValueError:
                print p, self.game.players
                print p, self.game.players
                print p, self.game.players
                print p, self.game.players
                print p, self.game.players
                print p, self.game.players
                return

            if p in disables:
                port.disabled = True
                port.selected = False
                try:
                    self.selected_players.remove(p)
                except ValueError:
                    pass
            else:
                port.disabled = False

    def get_selected_players(self):
        return self.selected_players

    def set_selected_players(self, players):
        for p in self.char_portraits:
            p.selected = False

        for p in players:
            self.player2portrait(p).selected = True

        self.selected_players = players[:]

    def end_select_player(self):
        #if not self.selecting_player: return
        self.selecting_player = False
        self.selected_players = []
        for p in self.char_portraits:
            p.selected = False
            p.disabled = False

    def get_selected_cards(self):
        return [
            cs.associated_card
            for cs in self.handcard_area.cards
            if cs.hca_selected
        ] + [
            cs.associated_card
            for cs in self.player2portrait(self.game.me).equipcard_area.cards
            if cs.selected
        ]

    def get_selected_skills(self):
        skills = self.game.me.skills
        return sorted([
            skills[i] for i in self.skill_box.get_selected_index()
        ], key=lambda s: s.sort_index)

    def on_mouse_click(self, x, y, button, modifier):
        c = self.control_frompoint1(x, y)
        if isinstance(c, GameCharacterPortrait) and self.selecting_player and not c.disabled:
            cc = c.control_frompoint1(x-c.x, y-c.y)
            if not (cc and cc.hit_test(x-c.x, y-c.y)):
                sel = c.selected
                psel = self.selected_players
                if sel:
                    c.selected = False
                    psel.remove(c.player)
                else:
                    c.selected = True
                    psel.append(c.player)
                self.dispatch_event('on_selection_change')
        return True

THBattleUI.register_event_type('on_selection_change')
