"""
Kivy --version = 2.3.0
Kivymd --version = 1.2.0
"""

import threading
import webbrowser

from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import ScaleBehavior
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import (CardTransition, SlideTransition, FadeTransition)
from kivy.properties import (StringProperty, NumericProperty, BooleanProperty, ColorProperty)
from kivymd.utils.set_bars_colors import set_bars_colors
from kivymd.uix.screenmanager import MDScreenManager

from OyaC_DB import DB

import random
import re
from datetime import (date)

Window.size = (350, 680)


class AskPassword(MDBoxLayout):
    infor = StringProperty()
    color = ColorProperty('white')
    btn = None  # it named when added to class PasswordCreation widget

    def dismiss_me(self):
        Clock.schedule_once(self.remove_pop, .2)

    def cancel_dismiss(self):
        Clock.unschedule(self.remove_pop)

    def remove_pop(self, dt):
        if self.parent:
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
    infor = StringProperty('Enter your password and get started')
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


class AddRowContainer(MDGridLayout):
    infor = StringProperty()
    isFull = BooleanProperty(False)
    infor_color = ColorProperty([.7, 0, 0, 1])
    collected_name = []
    collected_price = []
    wait = False
    app = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = Calculator()
        self.db = DB()
        self.err_color = [.7, 0, 0, 1]

    def add_new_row(self, content_counter, name, price):
        row_count = int(content_counter.text.split(": ")[1])
        if (Calculator.limit_container_rows > row_count != Calculator.limit_container_rows) and not self.isFull:
            if not self.wait:
                self.collected_name.clear()
                self.collected_price.clear()
                for nm in name:
                    if nm:
                        nm = self.app.space_less(nm.capitalize(), count=True)
                        if len(nm) <= 9:
                            self.collected_name.append(nm)

                nm_len = len(self.collected_name)
                if 0 < nm_len < 4:
                    self.wait = True
                    self.infor = 'Some field missed'
                    Clock.schedule_once(self.fade_infor, 2)

                for pr in price:
                    if pr.text:
                        pr.text_color_normal = [0, .7, 0, 1]
                        pr.line_color_normal = [0, 0, 0, .7]
                        val = pr.text.replace(',', '')
                        val = self.app.space_less(val)

                        if self.app.is_figures(val) and len(val) <= 7:
                            if float(val) > 0:
                                self.collected_price.append(self.app.put_comma(val))
                            else:
                                pr.text_color_normal = self.err_color
                                pr.line_color_normal = self.err_color
                                self.wait = True
                                self.collected_price.clear()
                                self.infor = 'Invalid'
                                Clock.schedule_once(self.fade_infor, 2)
                        else:
                            pr.text_color_normal = self.err_color
                            pr.line_color_normal = self.err_color
                            self.wait = True
                            self.collected_price.clear()
                            self.infor = 'Invalid'
                            Clock.schedule_once(self.fade_infor, 2)

                pr_len = len(self.collected_price)
                if 0 < pr_len < 3:
                    self.wait = True
                    txt = 'Some field missed'
                    if self.infor == 'Invalid':
                        txt = self.infor
                    self.infor = txt
                    Clock.schedule_once(self.fade_infor, 5)

                if nm_len == 4 and pr_len == 3:
                    self.insert(content_counter, self.collected_name, self.collected_price)

                self.reset_pads_input()
        else:
            self.wait = True
            self.isFull = True
            self.infor = 'You have reached the free limit.'
            Clock.schedule_once(self.fade_infor, 10)

    def fade_infor(self, dt):
        self.infor = ''
        self.wait = False
        self.infor_color = [.7, 0, 0, 1]

    def field_to_blank(self):
        self.ids.new_item_name.text = ''
        self.ids.pad_1.text = ''
        self.ids.pad_2.text = ''
        self.ids.pad_3.text = ''
        self.ids.price_1.text = ''
        self.ids.price_2.text = ''
        self.ids.price_3.text = ''

    def insert(self, content_counter, name, price):
        row_id = self.db.generate_id()
        index = int(content_counter.text.split(": ")[1]) + 1

        self.db.insert_items(
            [row_id, name[0], name[1], name[2], name[3],
             price[0], price[1], price[2], "*"]
        )
        self.display_new_row(
            [row_id, name[0], name[1], name[2], name[3],
             price[0], price[1], price[2], index]
        )

        self.infor_color = [0, .7, 0, 1]
        self.infor = "[font=Font/Merienda-Black.ttf]1[/font] row added successfully."
        Clock.schedule_once(self.fade_infor, 5)
        self.field_to_blank()
        content_counter.text = f"Contents: {index}"

        Clock.schedule_once(lambda dt: self.check_row_limit(index=index), 5)

    def display_new_row(self, data):
        self.app.row = Calculator.catch_deleted_row_index[0] if Calculator.catch_deleted_row_index else data[8]
        ItemsRow.row_id = data[0]

        ItemsRow.itemName = data[1]
        ItemsRow.theme_measure_1 = data[2]
        ItemsRow.rollPrice = data[5]

        ItemsRow.theme_measure_2 = data[3]
        ItemsRow.halfPrice = data[6]

        ItemsRow.theme_measure_3 = data[4]
        ItemsRow.packetPrice = data[7]
        
        if self.cool_grid:
            ItemsRow.edit_icon = ''

        self.cool_grid.add_widget(ItemsRow())  # home calc

        ItemsRow.edit_icon = ItemsRow.new_icon
        self.cool_edit_grid.add_widget(ItemsRow())  # edit screen
        self.cool_del_grid.add_widget(ItemsRow())  # delete screen
        self.cool_result_panel.result_text.text = f"Contents: {data[8]}"

        if Calculator.catch_deleted_row_index:
            Calculator.catch_deleted_row_index.remove(Calculator.catch_deleted_row_index[0])

    def reset_pads_input(self):
        for edit_row in self.cool_edit_grid.children:
            edit_row.ids.edit_icon.text_color = [.1, 0, 0, .7]
            edit_row.abc[0].isedit = False
            edit_row.abc[1].isedit = False
            edit_row.abc[2].isedit = False

        for del_row in self.cool_del_grid.children:
            del_row.ids.edit_icon.text_color = [.1, 0, 0, .7]
            del_row.is_del = False

    def check_row_limit(self, index):
        if index == Calculator.limit_container_rows:
            self.isFull = True
            self.infor = 'You have reached the free limit.'

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


class ItemsRow(MDBoxLayout):
    def_icon = 'cards-diamond'
    new_icon = 'cards-diamond-outline'

    row_id = StringProperty()
    itemName = StringProperty()

    theme_measure_1 = StringProperty()
    theme_measure_2 = StringProperty()
    theme_measure_3 = StringProperty()

    rollPrice = NumericProperty()
    halfPrice = NumericProperty()
    packetPrice = NumericProperty()

    edit_icon = StringProperty()


class TheGridLayer(MDGridLayout):
    app = None
    loader = None
    result = None
    quantity = 0
    countdown_rows = 25
    countdown_time = 100

    self_alias = list()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # work on the installation process of the application
        # reference the class widget: TheGridLayer to add its widget children
        self.self_alias.append(self)
        self.app = Calculator
        self.ripple_color = "c7c7c7"
        Clock.schedule_once(lambda x: self.install(), 1)

    def install(self):
        table = Calculator.db.check_table_existence()
        if not table:
            if self.abc:
                self.loader = self.abc[2].ids.loader_text
                self.loader.text = ''
                self.app.db.create_item_tables()
                Clock.schedule_interval(self.start_installation, .3)
        else:
            Clock.schedule_once(self.get_item, 1.5)

    def get_item(self, dt=None):
        if not self.app.items:
            self.result = self.app.db.get_items()
        else:
            self.result = self.app.items[0]

        if self.result:
            for i in self.result:
                threading.Thread(target=self.format_and_display_items(i)).start()

    def format_and_display_items(self, data):
        self.quantity += 1
        self.app.row = self.quantity
        ItemsRow.row_id = data[0]
        ItemsRow.itemName = data[1]
        ItemsRow.theme_measure_1 = data[2]
        ItemsRow.rollPrice = data[5]

        ItemsRow.theme_measure_2 = data[3]
        ItemsRow.halfPrice = data[6]

        ItemsRow.theme_measure_3 = data[4]
        ItemsRow.packetPrice = data[7]

        if data[8] == '#':
            ItemsRow.edit_icon = ItemsRow.def_icon if not self.abc else ''
        else:
            ItemsRow.edit_icon = ItemsRow.new_icon if not self.abc else ''

        self.add_widget(ItemsRow())
        if self.abc:
            self.abc[0].ids.res_cont.text = "Contents: " + str(self.quantity)
            self.abc[1].ids.content_txt.text = "Contents: " + str(self.quantity)

    def start_installation(self, dt):
        if not self.countdown_time < 5:
            self.countdown_time -= random.choice([5, 3, 5, 4])
        else:
            self.countdown_time = 0

        self.countdown_rows -= 1

        self.loader.font_name = "Font/TurretRoad-Medium.ttf"
        self.loader.text = f"Please wait for  [color=#CB37CC]{self.countdown_time}[/color]  \n OyaC is arranging your items"
        self.app.db.auto_insertion(self.countdown_rows)

        if self.countdown_rows == 0 or self.countdown_time == 0:
            self.loader.font_name = "Font/Jaro-Regular.ttf"
            self.loader.text = 'now is loading . . .'

        if self.countdown_rows == 0:
            for cl in self.self_alias:
                cl.get_item()
            Clock.unschedule(self.start_installation)

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

    @staticmethod
    def my_transition(x, y):
        y.transition = SlideTransition()
        y.transition.duration = .5

    def on_pre_enter(self, *args):
        has_table = Calculator.db.check_table_existence()
        if not has_table:
            Clock.schedule_once(self.direct_app_content_page, 25)
        else:
            Clock.schedule_once(self.direct_app_content_page, 7)

    def direct_app_content_page(self, dt):
        if 'loading' in self.ids.loader.ids.loader_text.text:
            Clock.unschedule(self.direct_app_content_page)
            self.transition = CardTransition()
            self.transition.duration = .3
            self.current = 'app_content'
        else:
            Clock.schedule_interval(self.direct_app_content_page, 1)

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

        # check OyaC rows if reached limit stop else go
        add_container_id = self.ids.sub_manager.my_players[3]
        if int(add_container_id.abc.text.split(':')[1]) >= Calculator.limit_container_rows:
            add_container_id.infor = 'You have reached the free limit.'
            add_container_id.isFull = True

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
    ref = "[ref=subscribe][color=#ff0000][u][b]Subscribe[/b][/u][/color][/ref]"

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
    check_row_no = []
    catch_touch_bg = []
    catch_del_touch = []
    catch_deleted_row_index = []
    focus_btn = [0]
    long_press_btn = [0]
    long_press_val = [0]
    card_name_tobe_edited = [0]
    gather_provided_input = ['0', '0', '0']
    index_of_row_to_edit_or_delete = [0]

    row = NumericProperty()
    result_color = ColorProperty([0, 0, 0, .7])
    result_bg_color = ColorProperty("#a5c4db")
    result = StringProperty('0')
    subs_ref = StringProperty(ref)
    item_list = StringProperty("Selected items: 0")
    item_list_color = ColorProperty('blue')

    is_edit_or_del_container = BooleanProperty(False)
    may_i_edit = BooleanProperty(False)
    pop_opened = BooleanProperty(False)
    stop_count = BooleanProperty(False)
    wait = False

    popup = None
    old_pwd = None
    home_calc = None
    task_scr_manager = None

    items = list()

    db = DB()
    tm = None

    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = "M3"
        self.set_bars_colors()
        self.home_calc = self.root.ids.grid
        self.task_scr_manager = self.root.ids.task_scr.my_sub_manager.my_players
        result = self.db.get_items()
        if result:
            self.items.append(result)

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
            self.show_selected_card_to_edit(obj)

    def on_release(self, obj):
        if not self.is_edit_or_del_container:
            self.press_identifier(obj, False)
            self.mute_helper_pad_obj()  # if called helper_pad won't work

    def press_identifier(self, obj, press_down):
        if not self.stop_count:
            _price = self.remove_comma(obj.price)
            _qnt = self.remove_comma(obj.quantity)

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
            total = prev_total + price if self.result != '0' else price

            if total <= self.calc_limit_count_numbers:
                self.result = self.put_comma(round(total, 2))
            else:
                self.result_color = [.7, 0, 0, 1]
                self.item_list_color = [.7, 0, 0, 1]
                self.stop_count = True
                self.result = self.put_comma(round(total, 2))

    @staticmethod
    def put_comma(val):
        if '.' in str(val):
            x = str(val).split('.')
            return f"{int(x[0]):,}.{x[1]}"
        else:
            return f'{int(val):,}'

    @staticmethod
    def remove_comma(val):
        if '.' in str(val):
            x = str(val).split('.')
            return float(f"{int(x[0].replace(',', ''))}.{x[1]}")
        else:
            return int(str(val).replace(',', ''))

    @staticmethod
    def check_row(obj):
        if obj != 0:
            if obj.index.endswith('roll'):
                return 1
            elif obj.index.endswith('half'):
                return 2
            elif obj.index.endswith('packet'):
                return 3

    def subtract(self, obj):
        if self.result != '0':
            row = self.check_row(obj)
            total = self.parse_result() - self.remove_comma(obj.price)
            total = total if total > 0.0 else 0

            if row == 1 and obj.roll_count > 0:
                obj.roll_count = obj.roll_count - 1
                self.result = self.put_comma(round(total, 2))

            elif row == 2 and obj.half_roll_count > 0:
                obj.half_roll_count = obj.half_roll_count - 1
                self.result = self.put_comma(round(total, 2))

            elif row == 3 and obj.packet_count > 0:
                obj.packet_count = obj.packet_count - 1
                self.result = self.put_comma(round(total, 2))

            self.subtract_selected_item(obj, 'one')

    def subtract_all(self, obj):
        if obj.price:
            total_count_of_del_item = 0
            row = self.check_row(obj)
            obj.price = self.remove_comma(obj.price)

            if self.result != '0':
                if row == 1:
                    total_count_of_del_item = obj.price * int(obj.roll_count)
                    obj.roll_count = 0

                elif row == 2:
                    total_count_of_del_item = obj.price * int(obj.half_roll_count)
                    obj.half_roll_count = 0

                elif row == 3:
                    total_count_of_del_item = obj.price * int(obj.packet_count)
                    obj.packet_count = 0

                total = (self.parse_result() - total_count_of_del_item)
                total = total if total > 0.0 else 0
                self.result = self.put_comma(round(total, 2))
                self.subtract_selected_item(obj, 'all')

    def helper_pad(self, obj):
        val = self.long_press_val[0]
        y = int(obj.text)
        pad_btn: str = self.long_press_btn[0]

        if pad_btn != 0 and val != 0 and not self.stop_count:
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
        return self.remove_comma(self.result)

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
        if c != 0:
            row = self.check_row(c)
            if row == 1 and c.roll_count == 0:
                self.surrender(c, q)
            elif row == 2 and c.half_roll_count == 0:
                self.surrender(c, q)
            elif row == 3 and c.packet_count == 0:
                self.surrender(c, q)
            self.resolve_calc_limit_count_numbers()

    def resolve_calc_limit_count_numbers(self):
        if self.remove_comma(self.result) < self.calc_limit_count_numbers:
            self.result_color = [0, 0, 0, .7]
            self.item_list_color = 'blue'
            self.stop_count = False

    def surrender(self, x, q):
        ind = x.index.split('-')[0]
        if x.index in self.is_the_all_row_selected:
            self.is_the_all_row_selected.remove(x.index)
            if ind in self.identical:
                self.identical.remove(ind)

        if q == 'one':
            self.focus_btn[0] = 0
        elif q == 'all':
            self.long_press_btn[0] = 0

        if self.identical.count(ind) == 0:
            self.inc -= 1
            self.item_list = "Selected items: " + str(self.inc)
            if ind in self.temp_selection_index:
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
        if self.focus_btn[0] != 0 and self.long_press_btn[0] == 0:
            self.subtract(self.focus_btn[0])

    def delete_specific(self):
        if self.long_press_btn[0] != 0:
            self.subtract_all(self.long_press_btn[0])

    def mute_helper_pad_obj(self):
        self.long_press_val[0] = 0
        self.long_press_btn[0] = 0

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
        self.long_press_btn[0] = 0
        self.focus_btn[0] = 0

    def back_to_setting_screen(self, direction, scr_name):
        self.root.transition = SlideTransition()
        self.root.transition.duration = .5
        self.root.transition.direction = direction
        self.root.current = scr_name

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

    @staticmethod
    def remove_pwd_pop(pop):
        pop.color = [0, 1, 0, 1]
        pop.infor = 'Done!'
        Clock.schedule_once(lambda x: pop.parent.remove_widget(pop), 1)

    def forgot_password(self, from_add_row_widget=None):
        if from_add_row_widget:
            from_add_row_widget.count_me += 1
            if from_add_row_widget.count_me >= 3:
                self.back_to_setting_screen('left', 'forget_pwd')
                from_add_row_widget.count_me = 0
        else:
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
                        btn1.parent.ids.edit_icon.text_color = [.1, 0, 0, .7]
                        btn2.parent.ids.edit_icon.text_color = "#33d651"
                        self.check_row_no.remove(self.check_row_no[0])

                    btn1.isedit = False
                    btn2.isedit = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch[1].index
                    self.catch_touch.remove(btn1)

                elif num == 1:
                    card_obj.isedit = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch[0].index
                    card_obj.parent.ids.edit_icon.text_color = "#33d651"

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
                        btn1.parent.ids.edit_icon.text_color = [.1, 0, 0, .7]
                        btn2.parent.ids.edit_icon.text_color = \
                            "#33d651" if card_obj.parent.ids.edit_icon.icon == 'cards-diamond' else [.9, 0, 0, 1]
                        self.check_row_no.remove(self.check_row_no[0])
                    btn1.parent.is_del = False
                    btn2.parent.is_del = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch_bg[1].index
                    self.catch_touch_bg.remove(btn1)

                elif num == 1:
                    card_obj.parent.is_del = True
                    self.index_of_row_to_edit_or_delete[0] = self.catch_touch_bg[0].index
                    card_obj.parent.ids.edit_icon.text_color = \
                        "#33d651" if card_obj.parent.ids.edit_icon.icon == 'cards-diamond' else [.9, 0, 0, 1]

                self.reset_edit_pads()
                self.ask_to_delete(card_obj)

    def ready_to_edit(self, card_obj):
        self.card_tobe_edited_part(card_obj)
        self.edit_scr_pop('up', 'edit_container_scr')

    def card_tobe_edited_part(self, obj):
        self.card_name_tobe_edited[0] = obj

    def sanctify_edited_row_input(self, widget, item_name, pad, price):
        self.gather_provided_input = ['0', '0', '0']
        widget.is_char = False
        if not self.wait:
            if item_name.text:
                val = self.space_less(item_name.text.capitalize(), count=True)
                if len(val) <= 9:
                    self.gather_provided_input[0] = val

            if pad.text:
                val = self.space_less(pad.text.capitalize(), count=True)
                if len(val) <= 9:
                    self.gather_provided_input[1] = val

            if price.text:
                price.text_color_normal = [0, .7, 0, 1]
                price.line_color_normal = [0, 0, 0, .7]

                val = price.text.replace(',', '')
                val = self.space_less(val)

                if self.is_figures(val):
                    if len(val) <= 7:
                        if float(val) > 0:
                            self.gather_provided_input[2] = self.put_comma(val)
                        else:
                            price.text_color_normal = 'red'
                            price.line_color_normal = 'red'
                else:
                    price.text_color_normal = 'red'
                    price.line_color_normal = 'red'
                    widget.is_char = True

            if self.gather_provided_input != ['0', '0', '0'] and not widget.is_char:
                self.collect_input(self.gather_provided_input)
                Clock.schedule_once(self.close_edit_scr, 0.5)
                self.wait = True

                # Reset Input Field
                item_name.text = ''
                pad.text = ''
                price.text = ''

    def close_edit_scr(self, dt=None):
        self.edit_scr_pop('down', "edit_row_scr")
        self.wait = False

        if isinstance(dt, list):
            for ele in dt:
                ele.text = ''

    def reset_edit_pads(self, alt=None):
        for row in self.abc('edit', alt).children:
            row.ids.edit_icon.text_color = [.1, 0, 0, .7]
            row.abc[0].isedit = False
            row.abc[1].isedit = False
            row.abc[2].isedit = False

    def reset_del_pads(self, alt=None):
        for row in self.abc('del', alt).children:
            row.ids.edit_icon.text_color = [.1, 0, 0, .7]
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
        mng.transition.duration = .5
        if _dir == 'down':
            mng.transition = FadeTransition()
            mng.transition.duration = .2

        mng.transition.direction = _dir
        mng.current = _scr
        self.pop_opened = False
        mng.parent.parent.parent.parent.goto_home = True

        if _dir == 'up':
            self.pop_opened = True
            mng.parent.parent.parent.parent.goto_home = False

    def collect_input(self, val):
        if self.abc('edit'):
            part_index = None
            parent_scr = self.abc('edit')
            card = self.card_name_tobe_edited[0]
            row_id = card.parent.row_id
            row = card.parent.row

            if val[0] != '0':
                self.update_item_name(parent_scr, row, val[0])

            if val[0] == '0':
                val[0] = card.parent.abc[3]
            if val[1] == '0':
                val[1] = card.my_parts[0].text
            if val[2] == '0':
                val[2] = card.my_parts[1].text

            values = (val[0], val[1], val[2], row_id)

            if self.check_row(card) == 1:
                query = ("""
                    UPDATE OyaC SET item_name = ?, theme_measure_1 = ?, 
                    roll_price = ? WHERE item_id = ?
                         """)
                self.db.update_item(query, values)
                part_index = 0

            if self.check_row(card) == 2:
                query = ("""
                    UPDATE OyaC SET item_name = ?, theme_measure_2 = ?, 
                    half_price = ? WHERE item_id = ?
                         """)
                self.db.update_item(query, values)
                part_index = 1

            if self.check_row(card) == 3:
                query = ("""
                    UPDATE OyaC SET item_name = ?, theme_measure_3 = ?, 
                    packet_price = ? WHERE item_id = ?
                         """)
                self.db.update_item(query, values)
                part_index = 2

            self.update(part_index, row, val[1], val[2])

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

    def update(self, row, ind, mea, price):
        card = self.card_name_tobe_edited[0].my_parts
        card[0].text = mea
        card[1].text = price

        # home calc scr
        for home_card in self.home_calc.children:
            if home_card.row == ind:
                home_card.abc[row].my_parts[0].text = mea
                home_card.abc[row].my_parts[1].text = price

        for del_card in self.abc('del').children:
            if del_card.row == ind:
                del_card.abc[row].my_parts[0].text = mea
                del_card.abc[row].my_parts[1].text = price

    def ask_to_delete(self, obj):
        if obj not in self.catch_del_touch and not self.pop_opened:
            self.popup = self.task_scr_manager[2]

            if obj.parent.ids.edit_icon.icon != 'cards-diamond':
                Dialog.question = 'Do you sure you want to delete this row?'
            else:
                Dialog.question = "Default row can't be deleted"

            self.popup.add_widget(Dialog(name='dialog'))
            self.catch_del_touch.append(obj)
            self.pop_opened = True
            self.popup.parent.parent.parent.parent.parent.parent.goto_home = False

    def delete_row(self, pop, cmd):
        if self.catch_del_touch:
            parent = self.catch_del_touch[0].parent

            if cmd and parent.ids.edit_icon.icon != 'cards-diamond':
                self.remove_row(self.abc('del'), parent.row_id)
                self.remove_row(self.home_calc, parent.row_id)
                self.remove_row(self.task_scr_manager[0], parent.row_id)
                self.db.delete_item(parent.row_id)  # db deletion

                remain = int(self.root.ids.result_panel.result_text.text.split(':')[1]) - 1
                self.task_scr_manager[3].abc.text = "Contents: " + str(remain)
                self.root.ids.result_panel.result_text.text = "Contents: " + str(remain)
                if remain < self.limit_container_rows:
                    self.task_scr_manager[3].infor = ''
                    self.task_scr_manager[3].isFull = False

                self.popup.remove_widget(pop)
                self.pop_opened = False
                self.popup.parent.parent.parent.parent.parent.parent.goto_home = True

                self.catch_del_touch.clear()
                self.catch_touch_bg.clear()
                self.catch_touch.clear()

        if not cmd:
            self.popup.remove_widget(pop)
            self.pop_opened = False
            self.popup.parent.parent.parent.parent.parent.parent.goto_home = True

            self.catch_del_touch.clear()
            self.catch_touch.clear()

    @staticmethod
    def space_less(char, count=False):
        if count:
            return re.sub(r'\s+', ' ', char, 2)
        else:
            return re.sub(r'\s+', '', char)

    @staticmethod
    def is_figures(fig):
        try:
            if re.match(r'^-?\d+$', fig):
                return True
            elif re.match(r'^-?\d+\.\d+$', fig):
                return True
            else:
                return False
        except Exception as e:
            return False

    @staticmethod
    def remove_row(parent, e):
        for child in parent.children:
            if child.row_id == e:
                parent.remove_widget(child)

    def subscribe(self):
        subc1 = "[ref=subscribe][color=#ff0000][u][b][size=15]Subscribe[/size][/b][/u][/color][/ref]"
        self.subs_ref = subc1
        Clock.schedule_once(self.animate_subscribe_txt, .5)
        webbrowser.open("http://localhost:3000/WebG/Home")

    def animate_subscribe_txt(self, dt):
        self.subs_ref = self.ref


if __name__ == "__main__":
    LabelBase.register("merienda", fn_regular="Font/Merienda-Light.ttf")
    Calculator().run()
