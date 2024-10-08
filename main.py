"""
Kivy --version = 2.3.0
Kivymd --version = 1.2.0
"""

import re
from datetime import (datetime, date)

from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import ScaleBehavior
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import (CardTransition, SlideTransition)
from kivy.properties import (StringProperty, NumericProperty, BooleanProperty, ColorProperty)
from kivymd.utils.set_bars_colors import set_bars_colors

from kivymd.uix.screenmanager import MDScreenManager
from OyaC_db import DB

Window.size = (350, 680)


class ForgotPassword(MDBoxLayout):
    infor = StringProperty('Answer the following questions correctly to recover your password.')
    question = StringProperty('Did you ever add new item in this week?')
    count_ques = NumericProperty(5)
    true = None
    false = None

    def answer(self, ans):
        if self.count_ques > 0:
            btn = self.ids.btn_box.children
            self.true = btn[0]
            self.false = btn[1]
            self.question = ''
            self.ids.btn_box.clear_widgets()
            self.count_ques -= 1

            if ans:
                Clock.schedule_once(self.new_quest, 1)
            else:
                Clock.schedule_once(self.new_quest, 1)

    def new_quest(self, dt):
        if self.count_ques == 4:
            self.question = '40'
        elif self.count_ques == 3:
            self.question = '3'
        elif self.count_ques == 2:
            self.question = '2'
        elif self.count_ques == 1:
            self.question = '1'

        if self.count_ques > 0:
            Clock.schedule_once(self.new_btn, .1)
        elif self.count_ques == 0:
            self.infor = 'Recovery questions completed'

    def new_btn(self, dt):
        self.ids.btn_box.add_widget(self.true)
        self.ids.btn_box.add_widget(self.false)


class AskPassword(MDBoxLayout):
    infor = StringProperty()
    color = ColorProperty('white')
    btn = None  # it named when added to class PasswordCreation widget

    def dismiss_me(self):
        Clock.schedule_once(self.remove_pop, .2)

    def cancel_dismiss(self):
        Clock.unschedule(self.remove_pop)

    def remove_pop(self, dt):
        self.parent.remove_widget(self)


class PasswordCreation(MDBoxLayout):
    db = DB()
    create = StringProperty("Create your password")
    update = StringProperty("Update your password")
    delete = StringProperty("Delete your password")
    clr = ColorProperty([0, 0, .5, 1])
    is_pwd_created = BooleanProperty(False)

    def create_pwd(self, btn):
        if not self.is_pwd_created:
            self.change_bg_color(btn)
            self.ask_pwd('Create a strong password', 'create')

    def update_pwd(self, btn):
        if self.is_pwd_created:
            self.change_bg_color(btn)
            self.ask_pwd('Insert your current password', 'update')

    def delete_pwd(self, btn):
        if self.is_pwd_created:
            self.change_bg_color(btn)
            self.ask_pwd('Insert your password to delete!', 'delete')

    def change_bg_color(self, btn):
        self.bg_color([1, 1, 1, .9])
        if btn:
            btn.md_bg_color = [0, .7, 0, .7]

    def bg_color(self, clr):
        if not self.is_pwd_created:
            self.ids.create_btn.md_bg_color = clr

        if self.is_pwd_created:
            self.ids.update_btn.md_bg_color = clr
            self.ids.delete_btn.md_bg_color = clr

    def check_pwd(self):
        self.bg_color([1, 1, 1, .9])
        if self.db.get_pwd():
            self.create = "Password created"
            self.is_pwd_created = True

    def ask_pwd(self, infor, btn):
        pop = AskPassword()
        pop.infor = infor
        pop.btn = btn
        self.parent.add_widget(pop)


class CheckPassword(MDBoxLayout):
    db = DB()
    attempt_count = 0
    infor = StringProperty('Write your password to enter and get started')
    color = ColorProperty('white')

    def match_password(self, pwd, root, skip_on_no_pwd=None):
        if pwd and len(pwd) > 3:
            res = self.db.check_pwd(pwd)
            if res:
                root.parent.parent.goto_home = True
                root.parent.remove_widget(root)
                Calculator.pop_opened = False
                Container.count_on_no_pwd_entrance = 0
            else:
                self.attempt_count += 1
                if self.attempt_count <= 5:
                    self.color = 'red'
                    self.infor = "Incorrect password!"
                else:
                    pop_card = root.ids.card_content_box
                    self.color = [0, 1, 0, 1]
                    self.infor = "Forgot password?"
                    pop_card.remove_widget(root.ids.input_box)
                    root.ids.ok_btn.icon = "arrow-right"

        if skip_on_no_pwd:
            if not self.db.get_pwd():  # this is in case of root widget refused to remove skip btn
                root.parent.parent.goto_home = True
                root.parent.remove_widget(root)
                Calculator.pop_opened = False
                Container.count_on_no_pwd_entrance += 1


class Dialog(MDScreen):
    question = StringProperty()


class NewAddedRowContainer(MDBoxLayout):
    infor = StringProperty('')
    requirement_fulfil = []
    wait = False
    app = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = Calculator

    def add_new_row(self, x, y, z, *args):  # x = btn, y = content counters, z = root and ids of other grid instance
        row_count = int(y.text.split(": ")[1])
        if self.app.limit_container_rows > row_count != self.app.limit_container_rows:
            if not self.wait:
                for text in list(args):
                    x.missed = True
                    if text != '':
                        self.requirement_fulfil.append(text.capitalize())

                num = len(self.requirement_fulfil)
                if num == 7:
                    price_1 = self.app().is_figures(self.requirement_fulfil[4])
                    price_2 = self.app().is_figures(self.requirement_fulfil[5])
                    price_3 = self.app().is_figures(self.requirement_fulfil[6])

                    if price_1 and price_2 and price_3:
                        x.missed = False
                        self.insert(y, z, self.requirement_fulfil)
                    else:
                        self.wait = True
                        self.requirement_fulfil.clear()
                        self.infor = 'Prices field expect numbers and got characters'
                        Clock.schedule_once(self.fade_infor, 5)

                elif 0 < num < 7:
                    self.wait = True
                    self.requirement_fulfil.clear()
                    self.infor = 'Some field missed'
                    Clock.schedule_once(self.fade_infor, 2)
                else:
                    self.wait = True
                    self.infor = 'Empty fields'
                    Clock.schedule_once(self.fade_infor, 2)
        else:
            self.wait = True
            x.missed = True
            self.infor = 'You have reached the free limit'
            Clock.schedule_once(self.fade_infor, 5)

        self.reset_pads_input(z)

    def fade_infor(self, dt):
        self.infor = ''
        self.wait = False

    def field_to_blank(self):
        self.ids.new_item_name.text = ''
        self.ids.pad_1.text = ''
        self.ids.pad_2.text = ''
        self.ids.pad_3.text = ''
        self.ids.price_1.text = ''
        self.ids.price_2.text = ''
        self.ids.price_3.text = ''
        self.requirement_fulfil.clear()

    def insert(self, i, obj, data):
        evt_time = datetime.now().strftime("%H:%M:%S:%p")
        item_name = data[0]
        theme_measure = [data[1], data[2], data[3]]
        _roll_price = data[4]
        _half_price = data[5]
        _packet_price = data[6]
        index = int(i.text.split(": ")[1]) + 1

        self.app().db.add_new_item(
            evt_time, item_name, theme_measure,
            _roll_price, _half_price, _packet_price, "*"
        )
        self.display_newly_added(
            [evt_time, item_name, data[1], data[2], data[3],
             _roll_price, _half_price, _packet_price, index], obj
        )
        self.infor = '1 row added successful'
        Clock.schedule_once(self.fade_infor, 3)
        self.field_to_blank()
        i.text = f"Contents: {index}"

        if index == self.app.limit_container_rows:
            obj.isFull = True

    def display_newly_added(self, data, ind):
        self.app.row = self.app.catch_deleted_row_index[0] if self.app.catch_deleted_row_index else data[8]
        ItemRows.evt_time = data[0]
        ItemRows.my_edit_card = "*"

        ItemRows.itemName = data[1]
        ItemRows.theme_measure_1 = data[2]
        ItemRows.rollPrice = data[5]

        ItemRows.theme_measure_2 = data[3]
        ItemRows.halfPrice = data[6]

        ItemRows.theme_measure_3 = data[4]
        ItemRows.packetPrice = data[7]

        ind.cool_grid.add_widget(ItemRows())  # home calc
        ind.cool_edit_grid.add_widget(ItemRows())  # edit screen
        ind.cool_del_grid.add_widget(ItemRows())  # delete screen
        ind.cool_result_panel.result_text.text = f"Contents: {data[8]}"
        if self.app.catch_deleted_row_index:
            self.app.catch_deleted_row_index.remove(self.app.catch_deleted_row_index[0])

    def reset_pads_input(self, pad):
        for edit_row in pad.cool_edit_grid.children:
            edit_row.ids.edit_card.md_bg_color = [.1, 0, 0, .5]
            edit_row.abc[0].isedit = False
            edit_row.abc[1].isedit = False
            edit_row.abc[2].isedit = False

        for del_row in pad.cool_del_grid.children:
            del_row.ids.edit_card.md_bg_color = [.1, 0, 0, .5]
            del_row.is_del = False


class HelperPad(MDRaisedButton, ScaleBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripple_color = "c7c7c7"

    def scale_down(self):
        scl = .98
        self.scale_value_x = scl
        self.scale_value_y = scl

    def scale_up(self):
        Clock.schedule_once(self._scale_up, .2)

    def _scale_up(self, dt):
        self.scale_value_x = 1
        self.scale_value_y = 1


class Card(MDCard, ScaleBehavior):

    def scale_down(self):
        scl = .98
        self.scale_value_x = scl
        self.scale_value_y = scl

    def scale_up(self):
        Clock.schedule_once(self._scale_up, .2)

    def _scale_up(self, dt):
        self.scale_value_x = 1
        self.scale_value_y = 1


class ItemRows(MDBoxLayout):
    evt_time = StringProperty()
    itemName = StringProperty()

    theme_measure_1 = StringProperty()
    theme_measure_2 = StringProperty()
    theme_measure_3 = StringProperty()

    rollPrice = NumericProperty()
    halfPrice = NumericProperty()
    packetPrice = NumericProperty()

    my_edit_card = StringProperty()


class TheGridLayer(MDGridLayout):
    app = None
    quantity = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = Calculator
        self.ripple_color = "c7c7c7"
        Clock.schedule_once(self.get_item, 2.5)

    def get_item(self, dt):
        result = self.app.db.retrieve_item()
        for i in result:
            if self.quantity >= 20:
                self.format_and_display_items(i)

    def format_and_display_items(self, data):
        self.quantity += 1
        self.app.row = self.quantity
        ItemRows.evt_time = data[0]
        ItemRows.itemName = 'P-name'  # data[1]
        ItemRows.theme_measure_1 = data[2]
        ItemRows.rollPrice = data[5]

        ItemRows.theme_measure_2 = data[3]
        ItemRows.halfPrice = data[6]

        ItemRows.theme_measure_3 = data[4]
        ItemRows.packetPrice = data[7]

        ItemRows.my_edit_card = data[8]

        self.add_widget(ItemRows())
        if self.abc:
            self.abc[0].ids.res_cont.text = "Contents: " + str(self.quantity)
            self.abc[1].ids.content_txt.text = "Contents: " + str(self.quantity)


class Container(MDScreenManager):
    goto_home = True
    count_on_no_pwd_entrance = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_pre_enter()

    def get_main_screen(self):
        Calculator.is_edit_or_del_container = False
        self.ids.manager.transition.direction = 'right'
        self.ids.manager.current = 'main'

        root_task = self.ids.task_scr.my_sub_manager.my_players
        Calculator().reset_edit_pads(root_task)
        Calculator().reset_del_pads(root_task)

    def get_edit_screen(self):
        Calculator.is_edit_or_del_container = True
        self.ids.manager.transition.direction = 'left'
        self.ids.manager.current = 'setting'

    def setting(self):
        self.change_scr('left', 'pwd_scr')

    def customise(self):
        self.change_scr('left', 'task_screen')

    def back_to_setting_screen(self):
        if self.goto_home:
            self.change_scr('right', 'app_content')

    def change_scr(self, direction, scr_name):
        self.transition = SlideTransition()
        self.transition.duration = .5
        self.transition.direction = direction
        self.current = scr_name

    def my_transition(self, x, y):
        y.transition = SlideTransition()
        y.transition.duration = .5

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.direct_app_content_page, 3)

    def direct_app_content_page(self, dt):
        self.transition = CardTransition()
        self.transition.duration = .3
        self.current = 'app_content'

    def check_password(self, scr):
        Calculator.pop_opened = True
        self.goto_home = False

        if Calculator.db.get_pwd():
            if len(scr.children) > 1:
                scr.remove_widget(scr.children[0])

            check_pwd = CheckPassword()
            check_pwd.ids.nav_box.remove_widget(check_pwd.ids.skip)
            check_pwd.ids.box.remove_widget(check_pwd.ids.no_pwd)
            scr.add_widget(check_pwd)

        else:
            if len(scr.children) > 1:
                scr.remove_widget(scr.children[0])
            scr.add_widget(self.no_password())

    def no_password(self):
        txt = None
        if self.count_on_no_pwd_entrance < 1:
            txt = "You have to create a password for your items security, this will prevent " \
                  "any abrupt or unauthorised addition, edition or deletion of any of your items."
        else:
            txt = 'Hi once again, password is recommended for your items safety,' \
                  '[color=#CB37CC] please create password[/color] to avoid any kind of frustration.'

        check_pwd = CheckPassword()
        check_pwd.infor = txt
        check_pwd.ids.box.remove_widget(check_pwd.ids.yes_pwd)
        return check_pwd


class Calculator(MDApp):
    title = 'OyaC'

    limit_container_rows = 36
    calc_limit_count_numbers = 99999999999
    quantity_count = 0
    press_time = 0
    inc = 0

    obj_ids = []
    temp_selection_index = []
    is_the_all_row_selected = []
    identical = []
    catch_touch = []
    catch_deleted_row_index = []
    long_press_btn = [None]
    long_press_val = [0]
    index_of_row_to_edit_or_delete = [0]
    focus_btn = [None]

    row = NumericProperty()
    result_color = ColorProperty([0, 0, 0, .7])
    result_bg_color = ColorProperty("#a5c4db")
    result = StringProperty('0')
    item_list = StringProperty("Selected items: 0")
    item_list_color = ColorProperty([0, 0, 0, .8])

    is_edit_or_del_container = BooleanProperty(False)
    may_i_edit = BooleanProperty(False)
    pop_opened = BooleanProperty(False)
    stop_count = BooleanProperty(False)

    home_calc = None
    task_scr_manager = None

    db = DB()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
        self.set_bars_colors()
        self.home_calc = self.root.ids.grid
        self.task_scr_manager = self.root.ids.task_scr.my_sub_manager.my_players

        if date.today().strftime("%A") == 'Monday':
            self.theme_cls.primary_palette = 'Teal'
        else:
            self.theme_cls.primary_palette = 'Cyan'

    def set_bars_colors(self):
        set_bars_colors(
            self.theme_cls.primary_color,  # status bar color
            self.theme_cls.primary_color,  # navigation bar color
            icons_color="Light",
        )

    # Calc Operation
    def on_press(self, obj):
        if not self.is_edit_or_del_container:
            self.press_time = Clock.get_time()
            self.press_identifier(obj, True)

        elif self.is_edit_or_del_container:
            if obj not in self.catch_touch:
                self.show_selected_card_to_edit(obj)

    def on_release(self, obj):
        if not self.is_edit_or_del_container:
            self.press_identifier(obj, False)
            self.mute_helper_pad_obj()  # if called helper_pad won't work

    def press_identifier(self, obj, press_down):
        if not self.stop_count:
            _price = int(obj.price)
            _qnt = int(obj.quantity)

            if Clock.get_time() - self.press_time <= 0.5 and not press_down:
                self.quantity_count = _qnt
                self.quantity_count += 1
                self.do_math(obj, _price, _qnt)
            else:
                self.long_press_val[0] = _price
                self.long_press_btn[0] = obj

    def _sum_all(self, price):
        if not self.stop_count:
            prev_total = self.remove_comma(self.result)
            total = int(prev_total) + price if self.result != '0' else price

            if total <= self.calc_limit_count_numbers:
                self.result = self.put_comma(total)
            else:
                self.result_color = [.7, 0, 0, 1]
                self.item_list_color = [.7, 0, 0, 1]
                self.stop_count = True
                self.result = self.put_comma(total)

    def put_comma(self, number):
        num = str(number)
        num_len = len(self.remove_comma(num))
        if num_len < 4:
            return num
        elif num_len == 4:
            return num[:1] + ',' + num[1:]
        elif num_len == 5:
            return num[:2] + ',' + num[2:]
        elif num_len == 6:
            return num[:3] + ',' + num[3:]
        elif num_len == 7:
            return num[:1] + ',' + num[1:][:3] + ',' + num[1:][3:]
        elif num_len == 8:
            return num[:2] + ',' + num[2:][:3] + ',' + num[2:][3:]
        elif num_len == 9:
            return num[:3] + ',' + num[3:][:3] + ',' + num[3:][3:]
        elif num_len == 10:
            return num[:1] + ',' + num[1:][:3] + ',' + num[1:][6:] + ',' + num[1:][6:]
        elif num_len == 11:
            return num[:2] + ',' + num[2:][:3] + ',' + num[2:][6:] + ',' + num[2:][6:]

    def remove_comma(self, num):  # return value is str
        if num != 0 and ',' in str(num):
            gathered_num = list()
            try:
                for n in num:
                    if n != ',':
                        gathered_num.append(n)
                return ''.join(gathered_num)
            except Exception:
                self.stop_count = True
                self.result_color = [.7, 0, 0, 1]
                self.item_list_color = [.7, 0, 0, 1]
                self.item_list = "err"
                print('Wrong')
                Clock.schedule_once(self.reset_everything_on_current_window, 7)
                return True
        else:
            return str(num)

    def check_row(self, obj):
        if obj is not None:
            if obj.index.endswith('roll'):
                return 1
            elif obj.index.endswith('half'):
                return 2
            elif obj.index.endswith('packet'):
                return 3

    def subtract(self, obj):
        if self.result != 0:
            row = self.check_row(obj)
            if row == 1 and obj.roll_count > 0:
                obj.roll_count = obj.roll_count - 1
                self.result = self.put_comma(self.parse_result() - int(obj.price))

            elif row == 2 and obj.half_roll_count > 0:
                obj.half_roll_count = obj.half_roll_count - 1
                self.result = self.put_comma(self.parse_result() - int(obj.price))

            elif row == 3 and obj.packet_count > 0:
                obj.packet_count = obj.packet_count - 1
                self.result = self.put_comma(self.parse_result() - int(obj.price))

            self.subtract_selected_item(obj, 'one')

    def subtract_all(self, obj):
        if obj.price:
            total_count_of_del_item = 0
            row = self.check_row(obj)
            obj.price = int(obj.price)
            if self.parse_result() != 0:
                if row == 1:
                    total_count_of_del_item = obj.price * int(obj.roll_count)
                    obj.roll_count = 0

                elif row == 2:
                    total_count_of_del_item = obj.price * int(obj.half_roll_count)
                    obj.half_roll_count = 0

                elif row == 3:
                    total_count_of_del_item = obj.price * int(obj.packet_count)
                    obj.packet_count = 0

                self.result = self.put_comma((self.parse_result() - total_count_of_del_item))
                self.subtract_selected_item(obj, 'all')

    def helper_pad(self, obj):
        val = self.long_press_val[0]
        y = int(obj.text)
        pad_btn = self.long_press_btn[0]

        if pad_btn is not None and val != 0 and not self.stop_count:
            total = val * y
            self.do_helper_pad_math(pad_btn, total, y)

    def do_helper_pad_math(self, obj, price, quant):
        if self.check_row(obj) == 1:
            self._sum_all(price)
            obj.roll_count = quant if obj.roll_count == '0' else int(obj.roll_count) + quant

        elif self.check_row(obj) == 3:
            self._sum_all(price)
            obj.packet_count = quant if obj.packet_count == '0' else int(obj.packet_count) + quant

        self.count_selected_item(obj)

    def parse_result(self):
        return int(self.remove_comma(self.result))

    def do_math(self, obj, price, quant):
        if self.check_row(obj) == 1:
            self._sum_all(price)
            obj.roll_count = self.quantity_count

        elif self.check_row(obj) == 2:
            if quant <= 1:
                self._sum_all(price)
                obj.half_roll_count = self.quantity_count

        elif self.check_row(obj) == 3:
            self._sum_all(price)
            obj.packet_count = self.quantity_count

        self.count_selected_item(obj)

    def count_selected_item(self, c):
        self.selected_card(c)
        if c.index.split('-')[0] not in self.temp_selection_index:
            self.temp_selection_index.append(c.index.split('-')[0])
            self.inc += 1
            self.item_list = "Selected items: " + str(self.inc)

    def subtract_selected_item(self, c, q):
        if c is not None:
            row = self.check_row(c)
            if row == 1 and c.roll_count == 0:
                self.surrender(c, q)
            elif row == 2 and c.half_roll_count == 0:
                self.surrender(c, q)
            elif row == 3 and c.packet_count == 0:
                self.surrender(c, q)
            self.resolve_calc_limit_count_numbers()

    def resolve_calc_limit_count_numbers(self):
        if int(self.remove_comma(self.result)) < self.calc_limit_count_numbers:
            self.result_color = [0, 0, 0, .7]
            self.item_list_color = [0, 0, 0, .8]
            self.stop_count = False

    def surrender(self, x, q):
        ind = x.index.split('-')[0]
        if x.index in self.is_the_all_row_selected:
            self.is_the_all_row_selected.remove(x.index)
            self.identical.remove(ind)

        if q == 'one':
            self.focus_btn[0] = None
        elif q == 'all':
            self.long_press_btn[0] = None

        if self.identical.count(ind) == 0:
            self.inc -= 1
            self.item_list = "Selected items: " + str(self.inc)
            self.temp_selection_index.remove(ind)

    def selected_card(self, obj):
        ind = obj.index
        _filter = []
        self.focus_btn[0] = obj

        if ind not in self.is_the_all_row_selected:
            self.obj_ids.append(obj)
            self.is_the_all_row_selected.append(ind)
            _filter.append(ind)
            for i in _filter:
                split_ind = i.split('-')[0]
                _filter.clear()
                if self.identical.count(split_ind) <= 3:
                    self.identical.append(split_ind)

    def delete_current(self):
        if self.focus_btn[0] is not None and self.long_press_btn[0] is None:
            self.subtract(self.focus_btn[0])

    def delete_specific(self):
        if self.long_press_btn[0] is not None:
            self.subtract_all(self.long_press_btn[0])

    def mute_helper_pad_obj(self):
        self.long_press_val[0] = 0
        self.long_press_btn[0] = None

    def reset_everything_on_current_window(self, dt=None):
        self.result = '0'
        self.inc = 0
        self.item_list = "Selected items: 0"
        self.mute_helper_pad_obj()
        self.resolve_calc_limit_count_numbers()
        for obj in self.obj_ids:
            self.quantity_count = 0
            if obj.index.endswith('roll'):
                obj.roll_count = self.quantity_count
            elif obj.index.endswith('half'):
                obj.half_roll_count = self.quantity_count
            elif obj.index.endswith('packet'):
                obj.packet_count = self.quantity_count

        self.obj_ids.clear()
        self.temp_selection_index.clear()
        self.is_the_all_row_selected.clear()
        self.identical.clear()
        self.long_press_val[0] = 0
        self.long_press_btn[0] = None
        self.focus_btn[0] = None

    def back_to_setting_screen(self, direction, scr_name):
        self.root.transition = SlideTransition()
        self.root.transition.duration = .5
        self.root.transition.direction = direction
        self.root.current = scr_name

    old_pwd = None

    def password_collection(self, pwd_txt, ask_pwd_root):
        ids = self.root.ids.pwd_crt.ids
        btn = ask_pwd_root.btn
        if pwd_txt:
            if len(pwd_txt) > 3:
                check_pwd = self.db.check_pwd(pwd_txt)
                if btn == 'create':
                    if not check_pwd:
                        self.db.create_pwd(pwd_txt)
                        ask_pwd_root.ids.pwd.text = ''
                        self.remove_pwd_pop(ask_pwd_root)
                        self.root.ids.pwd_crt.is_pwd_created = True
                        ids.crt_txt.text = "Password created"
                        ids.upd_txt.text = "Update your password"
                        ids.del_txt.text = "Delete your password"

                elif btn == 'update':
                    if check_pwd:
                        ask_pwd_root.color = [0, 1, 0, 1]
                        ask_pwd_root.ids.pwd.text = ''
                        ask_pwd_root.infor = "Create new password"
                        ask_pwd_root.btn = "new_pwd"
                        self.old_pwd = check_pwd

                    else:
                        ask_pwd_root.color = 'red'
                        ask_pwd_root.infor = "Incorrect password"

                elif btn == 'new_pwd':
                    if self.old_pwd:
                        self.db.update_pwd(self.old_pwd[0], pwd_txt)
                        ask_pwd_root.ids.pwd.text = ''
                        ids.upd_txt.text = "Password updated"
                        ids.del_txt.text = "Delete your password"
                        self.remove_pwd_pop(ask_pwd_root)
                        self.old_pwd = None

                    else:
                        ask_pwd_root.color = 'red'
                        ask_pwd_root.infor = "Sorry try again"
                        ask_pwd_root.ids.pwd.text = ''
                        ask_pwd_root.btn = "new_pwd"

                elif btn == 'delete':
                    if check_pwd:
                        self.db.delete_pwd(pwd_txt)
                        ask_pwd_root.ids.pwd.text = ''
                        self.remove_pwd_pop(ask_pwd_root)
                        self.root.ids.pwd_crt.is_pwd_created = False
                        ids.crt_txt.text = "Create your password"
                        ids.upd_txt.text = "Update your password"
                        ids.del_txt.text = "Password deleted"
                    else:
                        ask_pwd_root.color = 'red'
                        ask_pwd_root.infor = "Incorrect password"
            else:
                ask_pwd_root.color = 'red'
                ask_pwd_root.infor = "Too short password"

    def remove_pwd_pop(self, pop):
        pop.color = [0, 1, 0, 1]
        pop.infor = 'Done!'
        Clock.schedule_once(lambda x: pop.parent.remove_widget(pop), 1)

    def forgot_password(self):
        self.back_to_setting_screen('left', 'forget_pwd')

    # Task Screen   ---------------------------------------
    def is_edit_container(self, x, y, z):
        if not self.pop_opened:
            if not z:
                if x.text == 'Edit item':
                    if y.current == 'add_row_scr':
                        y.transition.direction = 'left'
                        y.current = 'edit_row_scr'

                    elif y.current == 'del_row_scr' or y.current == 'about':
                        y.transition.direction = 'right'
                        y.current = 'edit_row_scr'
                    self.may_i_edit = True

                elif x.text == 'Delete':
                    if y.current == 'add_row_scr' or y.current == 'edit_row_scr':
                        y.transition.direction = 'left'
                        y.current = 'del_row_scr'

                    elif y.current == 'about':
                        y.transition.direction = 'right'
                        y.current = 'del_row_scr'

            else:
                y.current = z

    def is_delete_screen(self):
        if self.root.ids.task_scr.my_sub_manager.current == 'del_row_scr':
            return True
        else:
            return False

    check_row_no = []
    catch_touch_bg = []

    def show_selected_card_to_edit(self, card_obj):
        is_del_scr = self.is_delete_screen()
        my_no = card_obj.parent.row
        ind = card_obj.index.split('-')[0]

        if not self.pop_opened:
            if ind not in self.check_row_no:
                self.check_row_no.append(ind)

            if not is_del_scr:
                card_obj.parent.is_del = False
                self.catch_touch.append(card_obj)

                num = len(self.catch_touch)
                if num == 2:
                    btn1 = self.catch_touch[0]
                    btn2 = self.catch_touch[1]

                    if len(self.check_row_no) > 1 and self.check_row_no[1] != my_no:
                        btn1.parent.ids.edit_card.md_bg_color = [.1, 0, 0, .5]
                        btn2.parent.ids.edit_card.md_bg_color = "#33d651"
                        self.check_row_no.remove(self.check_row_no[0])

                    btn1.isedit = False
                    btn2.isedit = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch[1].index
                    self.catch_touch.remove(btn1)

                elif num == 1:
                    card_obj.isedit = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch[0].index
                    card_obj.parent.ids.edit_card.md_bg_color = "#33d651"

                self.reset_del_pads()
                self.ready_to_edit(card_obj)

            if is_del_scr:
                card_obj.isedit = False
                self.catch_touch_bg.append(card_obj)
                num = len(self.catch_touch_bg)

                if num == 2:
                    btn1 = self.catch_touch_bg[0]
                    btn2 = self.catch_touch_bg[1]

                    if len(self.check_row_no) > 1 and self.check_row_no[1] != my_no:
                        btn1.parent.ids.edit_card.md_bg_color = [.1, 0, 0, .5]
                        btn2.parent.ids.edit_card.md_bg_color = \
                            "#33d651" if card_obj.parent.ids.edit_result.text == '#' else [.9, 0, 0, 1]
                        self.check_row_no.remove(self.check_row_no[0])

                    btn1.parent.is_del = False
                    btn2.parent.is_del = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch_bg[1].index
                    self.catch_touch_bg.remove(btn1)

                elif num == 1:
                    card_obj.parent.is_del = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch_bg[0].index
                    card_obj.parent.ids.edit_card.md_bg_color = \
                        "#33d651" if card_obj.parent.ids.edit_result.text == '#' else [.9, 0, 0, 1]

                self.reset_edit_pads()
                self.ask_to_delete(card_obj)

    def ready_to_edit(self, card_obj):
        self.card_tobe_edited_part(card_obj)
        self.edit_scr_pop('up', 'edit_container_scr')

    card_name_tobe_edited = [0]

    def card_tobe_edited_part(self, obj):
        self.card_name_tobe_edited[0] = obj

    gather_provided_input = [0, 0, 0]
    provided = [0, 0, 0]
    wait = False

    def sanctify_edited_row_input(self, a, x, y, z):
        self.gather_provided_input = [0, 0, 0]
        self.provided = [0, 0, 0]
        if not self.wait:
            if x['item_name'].text:
                self.gather_provided_input[0] = dict(name=self.space_less(x['item_name'].text.capitalize()))

            if y['pad'].text:
                self.gather_provided_input[1] = dict(pad=self.space_less(y['pad'].text.capitalize()))

            if z['price'].text:
                if self.is_figures(z['price'].text):
                    a.is_char = False
                    self.gather_provided_input[2] = dict(price=self.space_less(z['price'].text))
                else:
                    a.is_char = True
                    self.gather_provided_input = [0, 0, 0]

            _input = self.gather_provided_input
            if _input[0] != 0 and _input[0].get('name') is not None:
                self.provided[0] = _input[0]['name']
            if _input[1] != 0 and _input[1].get('pad') is not None:
                self.provided[1] = _input[1]['pad']
            if _input[2] != 0 and _input[2].get('price') is not None:
                self.provided[2] = _input[2]['price']

            if _input != [0, 0, 0]:
                self.collect_input(self.provided)
                Clock.schedule_once(self.close_edit_scr, 0.5)
                self.wait = True

                # Reset Input Field
                x['item_name'].text = ''
                y['pad'].text = ''
                z['price'].text = ''

    def close_edit_scr(self, dt=None):
        self.edit_scr_pop('down', "edit_row_scr")
        self.wait = False

        if isinstance(dt, list):
            for ele in dt:
                ele.text = ''

    def reset_edit_pads(self, alt=None):
        for row in self.abc('edit', alt).children:
            row.ids.edit_card.md_bg_color = [.1, 0, 0, .5]
            row.abc[0].isedit = False
            row.abc[1].isedit = False
            row.abc[2].isedit = False

    def reset_del_pads(self, alt=None):
        for row in self.abc('del', alt).children:
            row.ids.edit_card.md_bg_color = [.1, 0, 0, .5]
            row.is_del = False

    def edit_scr_pop(self, direction, screen):
        mng = self.root.ids.task_scr.my_sub_manager
        scr = mng.current
        if scr == "edit_row_scr":
            self._switch_screen(mng, direction, screen)
        elif scr == 'edit_container_scr':
            self._switch_screen(mng, direction, screen)

    def _switch_screen(self, mng, _dir, _scr):
        mng.transition = CardTransition()
        mng.transition.duration = 1
        mng.transition.direction = _dir
        mng.current = _scr
        self.pop_opened = False
        mng.parent.parent.parent.parent.goto_home = True

        if _dir == 'up':
            self.pop_opened = True
            mng.parent.parent.parent.parent.goto_home = False

    def collect_input(self, val):
        parent_scr = self.abc('edit')
        card = self.card_name_tobe_edited[0]
        db_index = card.parent.evt_time
        row_id = card.parent.row
        card_name = card.index.split('-')[1]

        if val[0] != 0 and val[1] != 0 and val[2] != 0:  # ================== 1, 2, 3
            self.update_item_name(parent_scr, row_id, val[0])
            values = (val[0], val[1], val[2], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_1 = %s, roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_2 = %s, half_roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_half_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_3 = %s, packet_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_packet(parent_scr, row_id, val[1], val[2])

        elif val[0] != 0 and val[1] != 0 and val[2] == 0:  # ================== 1, 2
            self.update_item_name(parent_scr, row_id, val[0])
            values = (val[0], val[1], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_1 = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_roll(parent_scr, row_id, val[1])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_2 = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_half_roll(parent_scr, row_id, val[1])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_3 = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_packet(parent_scr, row_id, val[1])

        elif val[0] != 0 and val[1] == 0 and val[2] != 0:  # ================== 1, 3
            self.update_item_name(parent_scr, row_id, val[0])
            values = (val[0], val[2], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET item_name = %s, roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET item_name = %s, half_roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_half_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET item_name = %s, packet_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_packet(parent_scr, row_id, price=val[2])

        elif val[0] == 0 and val[1] != 0 and val[2] != 0:  # ================== 2, 3
            values = (val[1], val[2], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET theme_measure_1 = %s, roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET theme_measure_2 = %s, half_roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_half_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET theme_measure_3 = %s, packet_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_packet(parent_scr, row_id, val[1], val[2])

        elif val[0] != 0 and val[1] == 0 and val[2] == 0:  # ================== 1
            self.update_item_name(parent_scr, row_id, val[0])
            values = (val[0], db_index)

            query = "UPDATE Oya_Item SET item_name = %s WHERE event_time = %s"
            self.db.update_item(query, values)

        elif val[0] == 0 and val[1] != 0 and val[2] == 0:  # ================== 2
            values = (val[1], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET theme_measure_1 = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_roll(parent_scr, row_id, mea=val[1])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET theme_measure_2 = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_half_roll(parent_scr, row_id, mea=val[1])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET theme_measure_3 = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_packet(parent_scr, row_id, mea=val[1])

        elif val[0] == 0 and val[1] == 0 and val[2] != 0:  # ================== 3
            values = (val[2], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET half_roll_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_half_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET packet_price = %s WHERE event_time = %s"
                self.db.update_item(query, values)
                self.update_packet(parent_scr, row_id, price=val[2])

    def space_less(self, char):
        if char:
            return re.sub(r'\s+', '', char)

    def is_figures(self, fig):
        try:
            if re.match(r'^-?\d+$', fig):
                return True
            elif re.match(r'^-?\d+\.\d+$', fig):
                return True
            else:
                return False
        except Exception:
            return False

    def abc(self, scr_order, alt=None):
        if scr_order == 'edit':
            if not self.task_scr_manager:
                return alt[0]
            return self.task_scr_manager[0]

        elif scr_order == 'del':
            if not self.task_scr_manager:
                return alt[1]
            return self.task_scr_manager[1]

    def update_item_name(self, scr, ind, name):
        if scr and ind:
            for child in scr.children:
                if child.row == ind:
                    child.item_names = name  # edit screen
                    for home_child in self.home_calc.children:
                        if home_child.row == ind:
                            home_child.item_names = name  # home calc screen
                    for edit_child in self.abc('del').children:
                        if edit_child.row == ind:
                            edit_child.item_names = name  # delete screen

    def update_roll(self, obj, ind=None, mea=None, price=None):
        if obj and ind:
            self.update(0, ind, mea, price)

    def update_half_roll(self, obj, ind=None, mea=None, price=None):
        if obj and ind:
            self.update(1, ind, mea, price)

    def update_packet(self, obj, ind=None, mea=None, price=None):
        if obj and ind:
            self.update(2, ind, mea, price)

    def update(self, row, ind, mea=None, price=None):
        card = self.card_name_tobe_edited[0].my_parts
        card[0].text = str(mea) if mea else card[0].text  # roll theme measurement
        card[1].text = str(price) if price else card[1].text  # roll price+

        # home calc scr
        for home_card in self.home_calc.children:
            if home_card.row == ind:
                home_card.abc[row].my_parts[0].text = str(mea) if mea else home_card.abc[row].my_parts[0].text
                home_card.abc[row].my_parts[1].text = str(price) if price else home_card.abc[row].my_parts[
                    1].text

        for del_card in self.abc('del').children:
            if del_card.row == ind:
                del_card.abc[row].my_parts[0].text = str(mea) if mea else del_card.abc[row].my_parts[0].text
                del_card.abc[row].my_parts[1].text = str(price) if price else del_card.abc[row].my_parts[
                    1].text

    popup = None
    catch_del_touch = []

    def ask_to_delete(self, obj):
        if obj not in self.catch_del_touch and not self.pop_opened:
            self.popup = self.task_scr_manager[2]

            if obj.parent.ids.edit_result.text != '#':
                Dialog.question = 'Do you sure you want to delete this row?'
            else:
                Dialog.question = "Default row can't be deleted"

            self.popup.add_widget(Dialog(name='dialog'))
            self.catch_del_touch.append(obj)
            self.pop_opened = True
            self.popup.parent.parent.parent.parent.parent.parent.goto_home = False

    def delete_row(self, x, pop, cmd):
        parent = self.catch_del_touch[0].parent
        if self.catch_del_touch:
            if parent.ids.edit_result.text != '#':
                if cmd:
                    del_scr = self.abc('del')
                    children = del_scr.children

                    for child in children:
                        if child == parent:

                            home_calc_children = self.home_calc.children
                            for home_child in home_calc_children:
                                if home_child.row == parent.row:

                                    edit_row = self.task_scr_manager[0].children
                                    for edit_child in edit_row:
                                        if edit_child.row == parent.row:
                                            self.catch_deleted_row_index.append(parent.row)
                                            self.db.delete_item(parent.evt_time)  # db deletion
                                            del_scr.remove_widget(parent)

                                            # other screens
                                            self.task_scr_manager[0].remove_widget(edit_child)
                                            self.home_calc.remove_widget(home_child)

                                            remain = int(
                                                self.root.ids.result_panel.result_text.text.split(':')[1]) - 1
                                            self.task_scr_manager[3].bg_color = [0, 0, 0, .1]
                                            self.task_scr_manager[3].abc.text_color = [0, .7, 0, 1]
                                            self.task_scr_manager[3].abc.text = "Contents: " + str(remain)
                                            self.root.ids.result_panel.result_text.text = "Contents: " + str(
                                                remain)

                                            self.popup.remove_widget(pop)
                                            self.pop_opened = False
                                            self.popup.parent.parent.parent.parent.parent.parent.goto_home = True

                                            self.catch_del_touch.clear()
                                            self.catch_touch.clear()

        if not cmd:
            self.popup.remove_widget(pop)
            self.pop_opened = False
            self.popup.parent.parent.parent.parent.parent.parent.goto_home = True

            self.catch_del_touch.clear()
            self.catch_touch.clear()


if __name__ == "__main__":
    Calculator().run()
