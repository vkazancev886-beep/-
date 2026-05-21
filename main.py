from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import platform
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Обязательно для Android
import matplotlib.pyplot as plt
import os
from datetime import datetime

Window.clearcolor = (0.95, 0.95, 0.98, 1)

class ReportApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.times = [
            "с 6:00 до 8:00", "с 8:00 до 10:00", "с 10:00 до 12:00", "с 12:00 до 14:00",
            "с 14:00 до 16:00", "с 16:00 до 18:00", "с 18:00 до 20:00", "с 20:00 до 22:00",
            "с 22:00 до 00:00", "с 00:00 до 02:00", "с 02:00 до 04:00", "с 04:00 до 06:00"
        ]
        self.locations = ["Красноармейск", "Родинское - Красный Лиман", "Димитров", "Новоэкономическое"]
        self.freq_bands = ["910-1360 МГц", "1361-2999 МГц", "3000-4938 МГц",
                           "4939-6100 МГц", "6100-7210 МГц", "7211-12000 МГц"]

        # Данные
        self.loc_data = {loc: {t: {'Обнаружение': 0, 'Воздействие': 0, 'Подавление': 0} for t in self.times} for loc in self.locations}
        self.freq_data = {t: {band: 0 for band in self.freq_bands} for t in self.times}

        self.sm = None

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(self.create_locations_screen())
        self.sm.add_widget(self.create_frequencies_screen())
        self.sm.add_widget(self.create_summary_screen())
        return self.sm

    # ====================== ВКЛАДКА 1: НАСЕЛЁННЫЕ ПУНКТЫ ======================
    def create_locations_screen(self):
        screen = Screen(name='locations')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Выбор
        top = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.spin_time_loc = Spinner(text=self.times[0], values=self.times, size_hint_x=0.5)
        self.spin_loc = Spinner(text=self.locations[0], values=self.locations, size_hint_x=0.5)
        top.add_widget(self.spin_time_loc)
        top.add_widget(self.spin_loc)
        layout.add_widget(top)

        # Ввод
        inputs = GridLayout(cols=3, size_hint_y=None, height=140, spacing=10)
        self.entry_det = TextInput(text='0', multiline=False, input_filter='int', font_size=18)
        self.entry_imp = TextInput(text='0', multiline=False, input_filter='int', font_size=18)
        self.entry_sup = TextInput(text='0', multiline=False, input_filter='int', font_size=18)

        inputs.add_widget(Label(text='Обнаружение:', size_hint_x=0.4))
        inputs.add_widget(self.entry_det)
        inputs.add_widget(Label(text='Воздействие:', size_hint_x=0.4))
        inputs.add_widget(self.entry_imp)
        inputs.add_widget(Label(text='Подавление:', size_hint_x=0.4))
        inputs.add_widget(self.entry_sup)
        layout.add_widget(inputs)

        btn_save = Button(text='Сохранить данные', size_hint_y=None, height=55, background_color=(0.2, 0.6, 1, 1), font_size=18)
        btn_save.bind(on_press=self.save_loc_data)
        layout.add_widget(btn_save)

        # Таблица
        scroll = ScrollView()
        self.loc_table = GridLayout(cols=5, spacing=5, size_hint_y=None, padding=5)
        self.loc_table.bind(minimum_height=self.loc_table.setter('height'))
        scroll.add_widget(self.loc_table)
        layout.add_widget(scroll)

        screen.add_widget(layout)
        self.update_loc_table()
        return screen

    def save_loc_data(self, instance):
        t = self.spin_time_loc.text
        loc = self.spin_loc.text
        try:
            self.loc_data[loc][t]['Обнаружение'] = int(self.entry_det.text or 0)
            self.loc_data[loc][t]['Воздействие'] = int(self.entry_imp.text or 0)
            self.loc_data[loc][t]['Подавление'] = int(self.entry_sup.text or 0)
            self.update_loc_table()
            self.show_popup('✅ Готово', f'Данные для {loc}\n({t}) сохранены')
        except:
            self.show_popup('❌ Ошибка', 'Введите целые числа')

    def update_loc_table(self):
        self.loc_table.clear_widgets()
        headers = ['Время', 'Локация', 'Обн.', 'Возд.', 'Под.']
        for h in headers:
            self.loc_table.add_widget(Label(text=h, bold=True, color=(0,0,0,1), size_hint_y=None, height=30))
        for loc in self.locations:
            for t in self.times:
                d = self.loc_data[loc][t]
                self.loc_table.add_widget(Label(text=t[2:7], size_hint_y=None, height=28))  # короткое время
                self.loc_table.add_widget(Label(text=loc[:10], size_hint_y=None, height=28))
                self.loc_table.add_widget(Label(text=str(d['Обнаружение']), size_hint_y=None, height=28))
                self.loc_table.add_widget(Label(text=str(d['Воздействие']), size_hint_y=None, height=28))
                self.loc_table.add_widget(Label(text=str(d['Подавление']), size_hint_y=None, height=28))

    # ====================== ВКЛАДКА 2: ЧАСТОТЫ ======================
    def create_frequencies_screen(self):
        screen = Screen(name='frequencies')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        top = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.spin_time_freq = Spinner(text=self.times[0], values=self.times, size_hint_x=1)
        top.add_widget(self.spin_time_freq)
        layout.add_widget(top)

        scroll = ScrollView()
        self.freq_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.freq_grid.bind(minimum_height=self.freq_grid.setter('height'))
        scroll.add_widget(self.freq_grid)
        layout.add_widget(scroll)

        self.freq_entries = {}
        for band in self.freq_bands:
            row = BoxLayout(size_hint_y=None, height=40, spacing=10)
            lbl = Label(text=band, size_hint_x=0.6, halign='left')
            entry = TextInput(text='0', multiline=False, input_filter='int', font_size=16)
            row.add_widget(lbl)
            row.add_widget(entry)
            self.freq_grid.add_widget(row)
            self.freq_entries[band] = entry

        btn_save = Button(text='Сохранить частоты', size_hint_y=None, height=55, background_color=(0.2, 0.6, 1, 1), font_size=18)
        btn_save.bind(on_press=self.save_freq_data)
        layout.add_widget(btn_save)

        screen.add_widget(layout)
        return screen

    def save_freq_data(self, instance):
        t = self.spin_time_freq.text
        try:
            for band, entry in self.freq_entries.items():
                self.freq_data[t][band] = int(entry.text or 0)
            self.show_popup('✅ Готово', f'Частоты для {t} сохранены')
        except:
            self.show_popup('❌ Ошибка', 'Введите целые числа')

    # ====================== ВКЛАДКА 3: ИТОГИ ======================
    def create_summary_screen(self):
        screen = Screen(name='summary')
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)

        btn_pie = Button(text='Построить круговые диаграммы', size_hint_y=None, height=60, font_size=18)
        btn_pie.bind(on_press=self.make_pies)
        layout.add_widget(btn_pie)

        btn_excel = Button(text='Сохранить в Excel', size_hint_y=None, height=60, font_size=18)
        btn_excel.bind(on_press=self.save_excel)
        layout.add_widget(btn_excel)

        # Место для диаграмм
        self.img_actions = Image(size_hint_y=None, height=280, allow_stretch=True)
        self.img_freq = Image(size_hint_y=None, height=280, allow_stretch=True)
        layout.add_widget(self.img_actions)
        layout.add_widget(self.img_freq)

        screen.add_widget(layout)
        return screen

    def calculate_totals(self):
        action = {'Обнаружение': 0, 'Воздействие': 0, 'Подавление': 0}
        for loc_vals in self.loc_data.values():
            for t_vals in loc_vals.values():
                for k, v in t_vals.items():
                    action[k] += v

        freq_tot = {b: 0 for b in self.freq_bands}
        for t_vals in self.freq_data.values():
            for b, v in t_vals.items():
                freq_tot[b] += v
        return action, freq_tot

    def make_pies(self, instance):
        action_totals, freq_totals = self.calculate_totals()

        # Диаграмма действий
        plt.figure(figsize=(6, 5))
        plt.pie(action_totals.values(), labels=action_totals.keys(), autopct='%1.1f%%',
                startangle=90, colors=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        plt.title('По типам действий')
        plt.savefig('pie_actions.png', bbox_inches='tight')
        plt.close()
        self.img_actions.source = 'pie_actions.png'

        # Диаграмма частот
        if sum(freq_totals.values()) > 0:
            plt.figure(figsize=(7, 5))
            plt.pie(freq_totals.values(), labels=list(freq_totals.keys()), autopct='%1.1f%%', startangle=90)
            plt.title('По диапазонам частот')
            plt.savefig('pie_frequencies.png', bbox_inches='tight')
            plt.close()
            self.img_freq.source = 'pie_frequencies.png'
        else:
            self.img_freq.source = ''

        self.show_popup('✅ Диаграммы', 'Круговые диаграммы построены')

    def save_excel(self, instance):
        try:
            filename = f"report_{datetime.now().strftime('%d.%m.%Y_%H%M')}.xlsx"
            save_path = os.path.join(self.user_data_dir, filename)

            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                # Общее по НП
                rows = []
                for loc in self.locations:
                    for t in self.times:
                        d = self.loc_data[loc][t]
                        rows.append({'Время': t, 'Локация': loc,
                                     'Обнаружение': d['Обнаружение'],
                                     'Воздействие': d['Воздействие'],
                                     'Подавление': d['Подавление']})
                pd.DataFrame(rows).to_excel(writer, sheet_name='Общее по НП', index=False)

                # Частоты
                freq_df = pd.DataFrame.from_dict(self.freq_data, orient='index')
                freq_df.index.name = 'Время'
                freq_df.to_excel(writer, sheet_name='Частоты')

                # Итоги
                action_totals, freq_totals = self.calculate_totals()
                pd.DataFrame([action_totals]).to_excel(writer, sheet_name='Итоги_действия', index=False)
                pd.DataFrame([freq_totals]).to_excel(writer, sheet_name='Итоги_частоты', index=False)

            self.show_popup('✅ Сохранено!', f'Файл сохранён:\n{filename}\n\nПапка: {self.user_data_dir}')
        except Exception as e:
            self.show_popup('❌ Ошибка', str(e))

    def show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(text=text, halign='center'))
        btn = Button(text='OK', size_hint_y=None, height=50)
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.5))
        btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    ReportApp().run()
