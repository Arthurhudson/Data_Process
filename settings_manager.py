import json
import os
import sys

class SettingsManager:
    def __init__(self, settings_file="excel_processor_settings.json"):
        # 获取应用程序所在目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用程序
            app_path = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            app_path = os.path.dirname(os.path.abspath(__file__))
            
        self.settings_file = os.path.join(app_path, settings_file)
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载设置时出错：{str(e)}")
                return {}
        return {}

    def save_settings(self, settings):
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.settings = settings
            return True
        except Exception as e:
            print(f"保存设置时出错：{str(e)}")
            return False

    def get_settings(self):
        return self.settings 