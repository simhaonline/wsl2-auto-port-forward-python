# ==================================================================
#       文 件 名: SettingsManage.py
#       概    要: 配置操作类，获取、保存配置
#       作    者: IT小强 
#       创建时间: 2019/12/24 18:14
#       修改时间: 
#       copyright (c) 2016 - 2019 mail@xqitw.cn
# ==================================================================
from os.path import join, isfile
from json import loads, dumps

from ResourcePath import ResourcePath


class SettingsManage:
    """
    配置操作类，获取、保存配置
    """

    # 默认配置数据
    __settings = {
        'auto_start_wsl': False,
        'fire_wall_open': False,
        'fire_wall_close': False,
        'ports': [],
        'wsl_bat_content': r"""@echo off
wsl.exe -u root"""
    }

    def __init__(self):
        """
        初始化
        """
        self.settingsDir = ResourcePath.create_settings_path()
        self.settingsFile = join(self.settingsDir, 'settings.json')
        self.__get_file_content()

    def set(self, name, value):
        """
        设置配置
        @param name: 配置名称
        @param value: 配置值
        """
        self.__settings[name] = value
        self.save_file_content(self.settingsFile, dumps(self.__settings))

    def get(self, name=None, default_value=None):
        """
        获取配置
        @param name: 配置名称 None 会返回全部配置
        @param default_value: 不存在时返回的默认值
        @return: 返回配置值
        """
        if not name:
            return self.__settings
        return self.__settings.get(name, default_value)

    def __get_file_content(self):
        """
        读取json文件的内容并转为字典
        """

        # 如果文件不存在则创建文件
        if not isfile(self.settingsFile):
            f = open(self.settingsFile, 'w', encoding='utf8')
            f.write(dumps(self.__settings))
            f.close()

        # 读取文件内容
        f = open(self.settingsFile, 'r', encoding='utf8')
        content = f.read()
        f.close()

        # 转为json
        self.__settings.update(loads(content))

    @staticmethod
    def save_file_content(file, content):
        """
        保存配置到json文件
        """
        f = open(file, 'w', encoding='utf8')
        f.write(content)
        f.close()
