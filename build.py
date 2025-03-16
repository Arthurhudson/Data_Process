import os
import sys
import shutil
from PyInstaller.__main__ import run

def build_app():
    # 清理之前的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # PyInstaller参数
    args = [
        'excel_processor.py',  # 主程序文件
        '--name=ExcelProcessor',  # 应用名称
        '--windowed',  # 使用GUI模式
        '--debug=all',  # 添加调试信息
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不确认覆盖
        '--codesign-identity=-',  # 使用 ad-hoc 签名
        '--osx-entitlements-file=entitlements.plist',  # 权限文件
    ]
    
    # 运行PyInstaller
    run(args)
    
    # 对生成的应用进行 ad-hoc 签名
    app_path = os.path.join('dist', 'ExcelProcessor.app')
    if os.path.exists(app_path):
        os.system(f'codesign --force --deep --sign - {app_path}')
        print("应用已完成签名！")
    
    print("应用打包完成！")

if __name__ == '__main__':
    build_app() 