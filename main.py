import re
from datetime import datetime

from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import ScaleBehavior
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import (CardTransition, SlideTransition, FadeTransition)
from kivy.properties import (StringProperty, NumericProperty, BooleanProperty, ColorProperty)
from kivy.core.window import Window

import mysql.connector
from kivymd.uix.screenmanager import MDScreenManager

Window.size = (350, 680)


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

        self.reset_pads(z)

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

        self.app().add_new_item(
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
        self.app.row = self.app.deleted_row_index[0] if self.app.deleted_row_index else data[8]
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
        if self.app.deleted_row_index:
            self.app.deleted_row_index.remove(self.app.deleted_row_index[0])

    def reset_pads(self, pad):
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
        Clock.schedule_once(self.get_item, 2)

    def get_item(self, dt):
        self.app.cursor.execute(f"SELECT * FROM Oya_Item")
        result = self.app.cursor.fetchall()
        for i in result:
            self.format_and_display_items(i)

    def format_and_display_items(self, data):
        self.quantity += 1
        self.app.row = self.quantity
        ItemRows.evt_time = data[0]
        ItemRows.itemName = data[1]
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_pre_enter()

    def get_main_screen(self):
        if self.goto_home:
            Calculator.is_edit_or_del_container = False
            self.ids.manager.transition.direction = 'right'
            self.ids.manager.current = 'main'

            root_task = self.ids.task_scr.my_sub_manager.my_players
            Calculator().reset_edit_pads(root_task)
            Calculator().reset_del_pads(root_task)

    def get_edit_screen(self):
        Calculator.is_edit_or_del_container = True
        self.ids.manager.transition.direction = 'left'
        self.ids.manager.current = 'task_screen'

    def my_transition(self, x, y):
        y.transition = SlideTransition()
        y.transition.duration = .5

    def on_pre_enter(self, *args):
        Clock.schedule_once(self.direct_app_content_page, 3)

    def direct_app_content_page(self, dt):
        self.transition = FadeTransition()
        self.transition.duration = .3
        self.current = 'app_content'


class Calculator(MDApp):
    title = 'OyaC'

    default_row = 11
    limit_container_rows = 36
    calc_limit_count_numbers = 9
    quantity_count = 0
    press_time = 0
    inc = 0

    obj_ids = []
    temp_selection_index = []
    is_the_all_row_selected = []
    identical = []
    catch_touch = []
    deleted_row_index = []
    long_press_val = [0]
    index_of_row_to_edit_or_delete = [0]
    btn_rep = [None]
    focus_btn = [None]

    row = NumericProperty()
    result = NumericProperty(0)
    result_color = ColorProperty([0, 0, 0, .7])
    result_bg_color = ColorProperty("#a5c4db")
    item_list = StringProperty("Selected items: 0")
    item_list_color = ColorProperty([0, 0, 0, .8])

    is_edit_or_del_container = BooleanProperty(False)
    may_i_edit = BooleanProperty(False)
    pop_opened = BooleanProperty(False)

    home_calc = None
    task_scr_manager = None

    c = ['Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan', 'Teal',
         'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray']

    # Mysql db connection
    db = mysql.connector.connect(host="127.0.0.1", user="root", password="Lmr977552", database="Oya_Oya_C")
    cursor = db.cursor()

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = self.c[7]
        self.home_calc = self.root.ids.grid
        self.task_scr_manager = self.root.ids.task_scr.my_sub_manager.my_players

    def on_start(self):
        # self.root.ids.manager.current = 'task_screen'
        pass

    # DB Operation
    def add_new_item(self, evt_time, item_name, theme_measure, roll, half, packet, status):
        statement = "INSERT INTO Oya_Item(event_time, item_name, theme_measure_1, theme_measure_2, theme_measure_3, " \
                    "roll_price, half_roll_price, packet_price, row_status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(statement, [evt_time, item_name, theme_measure[0], theme_measure[1],
                                        theme_measure[2], roll, half, packet, status])
        self.db.commit()

    def delete_item(self, evt):
        self.cursor.execute("DELETE FROM Oya_Item WHERE event_time = %s", (evt,))
        self.db.commit()

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
        res_len = len(str(self.result))
        if res_len <= self.calc_limit_count_numbers:
            _price = int(obj.price)
            _qnt = int(obj.quantity)

            if Clock.get_time() - self.press_time <= 0.5 and not press_down:
                self.quantity_count = _qnt
                self.quantity_count += 1
                self._separate(obj, _price, _qnt)
            else:
                self.long_press_val[0] = _price
                self.btn_rep[0] = obj

        else:
            self.item_list = "You have reached limit"
            self.result_color = [.7, 0, 0, 1]
            self.item_list_color = [.7, 0, 0, 1]

    def _separate(self, x, y, z):
        if x.index.startswith('1'):
            self.do_math(x, y, z)
        elif x.index.startswith('2'):
            self.do_math(x, y, z)
        elif x.index.startswith('3'):
            self.do_math(x, y, z)
        elif x.index.startswith('4'):
            self.do_math(x, y, z)
        elif x.index.startswith('5'):
            self.do_math(x, y, z)
        elif x.index.startswith('6'):
            self.do_math(x, y, z)
        elif x.index.startswith('7'):
            self.do_math(x, y, z)
        elif x.index.startswith('8'):
            self.do_math(x, y, z)
        elif x.index.startswith('9'):
            self.do_math(x, y, z)
        elif x.index.startswith('10'):
            self.do_math(x, y, z)
        elif x.index.startswith('11'):
            self.do_math(x, y, z)
        elif x.index.startswith('12'):
            self.do_math(x, y, z)
        elif x.index.startswith('13'):
            self.do_math(x, y, z)
        elif x.index.startswith('14'):
            self.do_math(x, y, z)
        elif x.index.startswith('15'):
            self.do_math(x, y, z)
        elif x.index.startswith('16'):
            self.do_math(x, y, z)
        elif x.index.startswith('17'):
            self.do_math(x, y, z)
        elif x.index.startswith('18'):
            self.do_math(x, y, z)
        elif x.index.startswith('19'):
            self.do_math(x, y, z)
        elif x.index.startswith('20'):
            self.do_math(x, y, z)
        elif x.index.startswith('21'):
            self.do_math(x, y, z)
        elif x.index.startswith('22'):
            self.do_math(x, y, z)
        elif x.index.startswith('23'):
            self.do_math(x, y, z)
        elif x.index.startswith('24'):
            self.do_math(x, y, z)
        elif x.index.startswith('25'):
            self.do_math(x, y, z)
        elif x.index.startswith('26'):
            self.do_math(x, y, z)
        elif x.index.startswith('27'):
            self.do_math(x, y, z)
        elif x.index.startswith('28'):
            self.do_math(x, y, z)
        elif x.index.startswith('29'):
            self.do_math(x, y, z)
        elif x.index.startswith('30'):
            self.do_math(x, y, z)
        elif x.index.startswith('31'):
            self.do_math(x, y, z)
        elif x.index.startswith('32'):
            self.do_math(x, y, z)
        elif x.index.startswith('33'):
            self.do_math(x, y, z)
        elif x.index.startswith('34'):
            self.do_math(x, y, z)
        elif x.index.startswith('35'):
            self.do_math(x, y, z)
        elif x.index.startswith('36'):
            self.do_math(x, y, z)

    def _sum_all(self, x):
        self.result = self.result + x if self.result != 0 else x

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
                self.result = self.result - int(obj.price)

            elif row == 2 and obj.half_roll_count > 0:
                obj.half_roll_count = obj.half_roll_count - 1
                self.result = self.result - int(obj.price)

            elif row == 3 and obj.packet_count > 0:
                obj.packet_count = obj.packet_count - 1
                self.result = self.result - int(obj.price)

            self.subtract_selected_item(obj, 'one')

    def subtract_all(self, obj):
        if obj.price:
            total_count_of_del_item = 0
            row = self.check_row(obj)
            obj.price = int(obj.price)
            if self.result != 0:
                if row == 1:
                    total_count_of_del_item = obj.price * int(obj.roll_count)
                    obj.roll_count = 0

                elif row == 2:
                    total_count_of_del_item = obj.price * int(obj.half_roll_count)
                    obj.half_roll_count = 0

                elif row == 3:
                    total_count_of_del_item = obj.price * int(obj.packet_count)
                    obj.packet_count = 0

                self.result = self.result - total_count_of_del_item
                self.subtract_selected_item(obj, 'all')

    def helper_pad(self, obj):
        x = self.long_press_val[0]
        y = int(obj.text)
        i = self.btn_rep[0]

        if i is not None and x != 0:
            total = x * y
            self.do_helper_pad_math(i, total, y)

    def do_helper_pad_math(self, _id, x, y):
        if _id.index.endswith('roll'):
            self._sum_all(x)
            _id.roll_count = y if _id.roll_count == '0' else int(_id.roll_count) + y

        elif _id.index.endswith('packet'):
            self._sum_all(x)
            _id.packet_count = y if _id.packet_count == '0' else int(_id.packet_count) + y

        self.count_selected_item(_id)

    def do_math(self, obj, x, y):
        if obj.index.endswith('roll'):
            self._sum_all(x)
            obj.roll_count = self.quantity_count

        elif obj.index.endswith('half'):
            if y <= 1:
                self._sum_all(x)
                obj.half_roll_count = self.quantity_count

        elif obj.index.endswith('packet'):
            self._sum_all(x)
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

    def surrender(self, x, q):
        ind = x.index.split('-')[0]
        self.is_the_all_row_selected.remove(x.index)
        self.identical.remove(ind)
        if q == 'one':
            self.focus_btn[0] = None
        elif q == 'all':
            self.btn_rep[0] = None

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
        if self.focus_btn[0] is not None and self.btn_rep[0] is None:
            self.subtract(self.focus_btn[0])

    def delete_specific(self):
        if self.btn_rep[0] is not None:
            self.subtract_all(self.btn_rep[0])

    def mute_helper_pad_obj(self):
        self.long_press_val[0] = 0
        self.btn_rep[0] = None

    def reset_everything_on_current_window(self):
        self.result = 0
        self.inc = 0
        self.item_list = "Selected items: 0"
        self.mute_helper_pad_obj()
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
        self.btn_rep[0] = None
        self.focus_btn[0] = None
        # Clock.schedule_interval(self.do, 1)
        # self._reset()

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

        if _dir == 'up':
            self.pop_opened = True
            Container.goto_home = False

        elif _dir == 'down':
            self.pop_opened = False
            Container.goto_home = True

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
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_2 = %s, half_roll_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_half_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_3 = %s, packet_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_packet(parent_scr, row_id, val[1], val[2])

        elif val[0] != 0 and val[1] != 0 and val[2] == 0:  # ================== 1, 2
            self.update_item_name(parent_scr, row_id, val[0])
            values = (val[0], val[1], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_1 = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_roll(parent_scr, row_id, val[1])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_2 = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_half_roll(parent_scr, row_id, val[1])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET item_name = %s, theme_measure_3 = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_packet(parent_scr, row_id, val[1])

        elif val[0] != 0 and val[1] == 0 and val[2] != 0:  # ================== 1, 3
            self.update_item_name(parent_scr, row_id, val[0])
            values = (val[0], val[2], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET item_name = %s, roll_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET item_name = %s, half_roll_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_half_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET item_name = %s, packet_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_packet(parent_scr, row_id, price=val[2])

        elif val[0] == 0 and val[1] != 0 and val[2] != 0:  # ================== 2, 3
            values = (val[1], val[2], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET theme_measure_1 = %s, roll_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET theme_measure_2 = %s, half_roll_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_half_roll(parent_scr, row_id, val[1], val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET theme_measure_3 = %s, packet_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_packet(parent_scr, row_id, val[1], val[2])

        elif val[0] != 0 and val[1] == 0 and val[2] == 0:  # ================== 1
            self.update_item_name(parent_scr, row_id, val[0])
            values = (val[0], row_id)

            query = "UPDATE Oya_Item SET item_name = %s WHERE event_time = %s"
            self.cursor.execute(query, values)
            self.db.commit()

        elif val[0] == 0 and val[1] != 0 and val[2] == 0:  # ================== 2
            values = (val[1], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET theme_measure_1 = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_roll(parent_scr, row_id, mea=val[1])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET theme_measure_2 = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_half_roll(parent_scr, row_id, mea=val[1])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET theme_measure_3 = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_packet(parent_scr, row_id, mea=val[1])

        elif val[0] == 0 and val[1] == 0 and val[2] != 0:  # ================== 3
            values = (val[2], db_index)

            if card_name == 'roll':
                query = "UPDATE Oya_Item SET roll_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'half':
                query = "UPDATE Oya_Item SET half_roll_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
                self.update_half_roll(parent_scr, row_id, price=val[2])

            elif card_name == 'packet':
                query = "UPDATE Oya_Item SET packet_price = %s WHERE event_time = %s"
                self.cursor.execute(query, values)
                self.db.commit()
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
                home_card.abc[row].my_parts[1].text = str(price) if price else home_card.abc[row].my_parts[1].text

        for del_card in self.abc('del').children:
            if del_card.row == ind:
                del_card.abc[row].my_parts[0].text = str(mea) if mea else del_card.abc[row].my_parts[0].text
                del_card.abc[row].my_parts[1].text = str(price) if price else del_card.abc[row].my_parts[1].text

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
            Container.goto_home = False

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
                                            self.deleted_row_index.append(parent.row)
                                            self.delete_item(parent.evt_time)  # db deletion
                                            del_scr.remove_widget(parent)

                                            # other screens
                                            self.task_scr_manager[0].remove_widget(edit_child)
                                            self.home_calc.remove_widget(home_child)

                                            remain = int(self.root.ids.result_panel.result_text.text.split(':')[1]) - 1
                                            self.task_scr_manager[3].color = [0, 0, 0, .1]
                                            self.task_scr_manager[3].abc.text_color = [0, .7, 0, 1]
                                            self.task_scr_manager[3].abc.text = "Contents: " + str(remain)
                                            self.root.ids.result_panel.result_text.text = "Contents: " + str(remain)

                                            self.popup.remove_widget(pop)
                                            self.pop_opened = False
                                            Container.goto_home = True

                                            self.catch_del_touch.clear()
                                            self.catch_touch.clear()

        if not cmd:
            self.popup.remove_widget(pop)
            self.pop_opened = False
            Container.goto_home = True

            self.catch_del_touch.clear()
            self.catch_touch.clear()

    x = 0

    def _reset(self):
        if self.x == len(self.c):
            self.x = 0
        print(self.x)
        self.theme_cls.primary_palette = self.c[self.x]
        self.x += 1

    def do(self, dt):
        self.x += 1
        self.add_new_item(datetime.now().strftime("%H:%M:%S:%p"), 'Inyass', ['Roll', 'Half', 'Packet'], 1, 2, 3, '#')
        print(self.x)
        if self.x == 25:
            Clock.unschedule(self.do)

    def test_me(self, *args):
        print("Tested: ", args)


if __name__ == "__main__":
    Calculator().run()
