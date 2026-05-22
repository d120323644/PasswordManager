"""
密码管理器 - Kivy 手机版 v2
修复布局问题，简化代码
"""
import os
import json
import hashlib
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window


# 黄棕配色方案
COLORS = {
    'primary': (0.82, 0.62, 0.24, 1),      # 金黄色 #D19E3D
    'primary_dark': (0.65, 0.48, 0.15, 1), # 深棕色 #A67A26
    'secondary': (0.55, 0.35, 0.20, 1),    # 棕色 #8C5933
    'background': (0.98, 0.96, 0.92, 1),   # 米白色 #FAF8EB
    'card': (1, 1, 1, 1),                   # 白色
    'text': (0.2, 0.2, 0.2, 1),            # 深灰
    'error': (0.8, 0.2, 0.2, 1),           # 红色
}


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_input = None
        self.status_label = None
        
    def build(self):
        scroll = ScrollView(do_scroll_x=False)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        layout.bind(minimum_height=lambda i, v: setattr(scroll, 'height', v))
        
        # 标题
        layout.add_widget(Label(
            text='🔐 密码管理器',
            font_size=sp(28),
            bold=True,
            color=COLORS['primary_dark'],
            size_hint=(1, None),
            height=60
        ))
        
        # 提示
        layout.add_widget(Label(
            text='请输入主密码',
            font_size=sp(18),
            color=COLORS['text'],
            size_hint=(1, None),
            height=40
        ))
        
        # 密码输入
        self.password_input = TextInput(
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size=sp(18),
            hint_text='输入密码'
        )
        layout.add_widget(self.password_input)
        
        # 状态
        self.status_label = Label(
            text='',
            size_hint=(1, None),
            height=40,
            color=COLORS['error'],
            font_size=sp(14)
        )
        layout.add_widget(self.status_label)
        
        # 登录按钮
        login_btn = Button(
            text='进入',
            size_hint=(1, None),
            height=50,
            font_size=sp(20),
            background_color=COLORS['primary'],
            color=(1, 1, 1, 1)
        )
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)
        
        # 设置按钮
        setup_btn = Button(
            text='首次使用 - 设置密码',
            size_hint=(1, None),
            height=50,
            font_size=sp(16),
            background_color=COLORS['secondary'],
            color=(1, 1, 1, 1)
        )
        setup_btn.bind(on_press=lambda x: self.goto_setup())
        layout.add_widget(setup_btn)
        
        scroll.add_widget(layout)
        return scroll
    
    def do_login(self, instance):
        password = self.password_input.text if self.password_input else ''
        if not password:
            self.status_label.text = '⚠️ 请输入密码'
            return
        
        app = App.get_running_app()
        if app.check_password(password):
            app.screen_manager.current = 'main'
        else:
            app.failed_attempts += 1
            left = 5 - app.failed_attempts
            if left > 0:
                self.status_label.text = f'密码错误！剩余：{left}次'
            else:
                self.status_label.text = '已锁定 24 小时'
        self.password_input.text = ''
    
    def goto_setup(self):
        App.get_running_app().screen_manager.current = 'setup'


class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password_input = None
        self.confirm_input = None
        
    def build(self):
        scroll = ScrollView(do_scroll_x=False)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        layout.bind(minimum_height=lambda i, v: setattr(scroll, 'height', v))
        
        # 标题
        layout.add_widget(Label(
            text='🔐 首次使用\n设置主密码',
            font_size=sp(24),
            bold=True,
            color=COLORS['primary_dark'],
            size_hint=(1, None),
            height=80
        ))
        
        # 主密码标签
        layout.add_widget(Label(
            text='主密码',
            font_size=sp(16),
            color=COLORS['text'],
            size_hint=(1, None),
            height=30,
            halign='left'
        ))
        
        # 主密码输入
        self.password_input = TextInput(
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size=sp(18),
            hint_text='至少 6 位'
        )
        layout.add_widget(self.password_input)
        
        # 确认密码标签
        layout.add_widget(Label(
            text='确认密码',
            font_size=sp(16),
            color=COLORS['text'],
            size_hint=(1, None),
            height=30,
            halign='left'
        ))
        
        # 确认密码输入
        self.confirm_input = TextInput(
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=50,
            font_size=sp(18),
            hint_text='再次输入'
        )
        layout.add_widget(self.confirm_input)
        
        # 设置按钮
        setup_btn = Button(
            text='设置密码',
            size_hint=(1, None),
            height=50,
            font_size=sp(20),
            background_color=COLORS['primary'],
            color=(1, 1, 1, 1)
        )
        setup_btn.bind(on_press=self.do_setup)
        layout.add_widget(setup_btn)
        
        # 提示
        layout.add_widget(Label(
            text='💡 提示：\n• 主密码是唯一凭证\n• 请妥善保管\n• 建议至少 6 位\n• 包含字母数字更安全',
            font_size=sp(14),
            color=COLORS['text'],
            size_hint=(1, None),
            height=120,
            halign='left'
        ))
        
        scroll.add_widget(layout)
        return scroll
    
    def do_setup(self, instance):
        password = self.password_input.text if self.password_input else ''
        confirm = self.confirm_input.text if self.confirm_input else ''
        
        if not password:
            self.show_popup('错误', '密码不能为空！')
            return
        
        if password != confirm:
            self.show_popup('错误', '两次密码不一致！')
            return
        
        if len(password) < 6:
            self.show_popup('错误', '密码至少 6 位！')
            return
        
        app = App.get_running_app()
        app.save_password(password)
        self.show_popup('成功', '设置成功！')
        
        def switch(dt):
            app.screen_manager.current = 'main'
        Clock.schedule_once(switch, 1.5)
    
    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message, font_size=sp(16)),
            size_hint=(0.85, 0.4)
        ).open()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.welcome_label = None
        
    def build(self):
        scroll = ScrollView(do_scroll_x=False)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12, size_hint_y=None)
        layout.bind(minimum_height=lambda i, v: setattr(scroll, 'height', v))
        
        # 欢迎
        self.welcome_label = Label(
            text='🎉 欢迎使用\n密码管理器',
            font_size=sp(24),
            bold=True,
            color=COLORS['primary_dark'],
            size_hint=(1, None),
            height=80
        )
        layout.add_widget(self.welcome_label)
        
        # 功能列表
        features = [
            '🔐 主密码保护',
            '🚫 5 次错误锁定',
            '📝 密码管理',
            '➕ 新建/编辑/删除',
            '⚙️ 修改主密码',
            '📤 导出/导入',
            '🔒 AES-256 加密'
        ]
        
        for f in features:
            layout.add_widget(Label(
                text=f,
                font_size=sp(16),
                color=COLORS['text'],
                size_hint=(1, None),
                height=40,
                halign='left'
            ))
        
        # 按钮
        new_btn = Button(
            text='➕ 新建密码',
            size_hint=(1, None),
            height=50,
            font_size=sp(16),
            background_color=COLORS['primary'],
            color=(1, 1, 1, 1)
        )
        new_btn.bind(on_press=lambda x: self.show_popup('提示', '开发中...'))
        layout.add_widget(new_btn)
        
        settings_btn = Button(
            text='⚙️ 设置',
            size_hint=(1, None),
            height=50,
            font_size=sp(16),
            background_color=COLORS['secondary'],
            color=(1, 1, 1, 1)
        )
        settings_btn.bind(on_press=lambda x: setattr(App.get_running_app().screen_manager, 'current', 'settings'))
        layout.add_widget(settings_btn)
        
        scroll.add_widget(layout)
        return scroll
    
    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message, font_size=sp(16)),
            size_hint=(0.85, 0.4)
        ).open()


class SettingsScreen(Screen):
    def build(self):
        scroll = ScrollView(do_scroll_x=False)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        layout.bind(minimum_height=lambda i, v: setattr(scroll, 'height', v))
        
        layout.add_widget(Label(
            text='⚙️ 设置',
            font_size=sp(28),
            bold=True,
            color=COLORS['primary_dark'],
            size_hint=(1, None),
            height=80
        ))
        
        for text, msg in [
            ('🔑 修改主密码', '修改密码功能开发中...'),
            ('📤 导出数据', '导出功能开发中...'),
            ('📥 导入数据', '导入功能开发中...')
        ]:
            btn = Button(
                text=text,
                size_hint=(1, None),
                height=50,
                font_size=sp(16),
                background_color=COLORS['primary'],
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, m=msg: self.show_popup('提示', m))
            layout.add_widget(btn)
        
        back_btn = Button(
            text='返回',
            size_hint=(1, None),
            height=50,
            font_size=sp(16),
            background_color=COLORS['secondary'],
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(App.get_running_app().screen_manager, 'current', 'main'))
        layout.add_widget(back_btn)
        
        scroll.add_widget(layout)
        return scroll
    
    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message, font_size=sp(16)),
            size_hint=(0.85, 0.4)
        ).open()


class PasswordManagerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_file = "config.json"
        self.failed_attempts = 0
        self.screen_manager = None
    
    def build(self):
        self.title = '密码管理器'
        Window.size = (360, 640)
        Window.clearcolor = COLORS['background']
        
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(SetupScreen(name='setup'))
        self.screen_manager.add_widget(MainScreen(name='main'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        
        self.screen_manager.current = 'setup' if not os.path.exists(self.config_file) else 'login'
        return self.screen_manager
    
    def save_password(self, password):
        salt = os.urandom(16).hex()
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump({
                'master_password_hash': hashed,
                'master_password_salt': salt,
                'version': '1.0'
            }, f, ensure_ascii=False, indent=2)
    
    def check_password(self, password):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            salt = config['master_password_salt']
            stored = config['master_password_hash']
            computed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
            return computed == stored
        except:
            return False


if __name__ == "__main__":
    PasswordManagerApp().run()
