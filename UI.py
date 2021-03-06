# ==================================================================
#       文 件 名: UI.py
#       概    要: WSL2 端口自动转发
#       作    者: IT小强 
#       创建时间: 2019/12/22 9:51
#       修改时间: 
#       copyright (c) 2016 - 2019 mail@xqitw.cn
# ==================================================================
from os.path import isfile
from shutil import copyfile

from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMessageBox, QAction, QSystemTrayIcon, QMenu
from PySide2.QtCore import QProcess

from ResourcePath import ResourcePath
from SettingsManage import SettingsManage
from WinCmd import WinCmd


class UI:
    """
    WSL2 端口自动转发
    """

    def __init__(self, qt_application=None):
        self.qt_application = qt_application
        # 实例化配置管理类
        self.settings_manage = SettingsManage()
        self.__setting = self.settings_manage.get()

        # 实例化windows命令处理类
        self.wsl2 = WinCmd()

        # 初始化启动脚本
        if not isfile(self.wsl2.WSL_VBS_PATH):
            copyfile(self.wsl2.WSL_VBS_PATH_TEMP, self.wsl2.WSL_VBS_PATH)
        if not isfile(self.wsl2.WSL_BAT_PATH):
            self.settings_manage.save_file_content(
                self.wsl2.WSL_BAT_PATH,
                self.__setting.get('wsl_bat_content', '')
            )
        # 加载UI文件
        self.ui = QUiLoader().load(ResourcePath.resource_path('lib/wsl2.ui'))

        # 设置界面图标
        app_icon = QIcon(ResourcePath.resource_path("lib/logo.ico"))
        self.ui.setWindowIcon(app_icon)

        # 设置选中状态
        self.ui.auto_start_wsl.setChecked(self.__setting.get('auto_start_wsl', False))
        self.ui.fire_wall_open.setChecked(self.__setting.get('fire_wall_open', False))
        self.ui.fire_wall_close.setChecked(self.__setting.get('fire_wall_close', False))

        # 设置文本框的值
        self.ui.port_text.appendPlainText('\n'.join(self.__setting.get('ports', [])))
        self.ui.bat_text.appendPlainText(self.wsl2.get_bat_script())

        # 按钮监听
        self.ui.get_wsl2_ip.clicked.connect(self.__get_wsl2_ip)
        self.ui.port_add.clicked.connect(self.__port_add)
        self.ui.port_del.clicked.connect(self.__port_del)
        self.ui.port_info.clicked.connect(self.__port_info)
        self.ui.wsl_l_v.clicked.connect(self.__wsl_l_v)
        self.ui.port_reset.clicked.connect(self.__port_reset)
        self.ui.end_wsl.clicked.connect(self.__end_wsl)
        self.ui.start_wsl.clicked.connect(self.__start_wsl)
        self.ui.start_wsl_all.clicked.connect(self.start_wsl_all)
        self.ui.save_settings.clicked.connect(self.__save_settings)
        self.ui.save_settings_ports.clicked.connect(self.__save_settings)

        # 设置系统托盘图标的菜单
        tp_icon = QIcon(ResourcePath.resource_path("lib/logo.ico"))
        self.tp = QSystemTrayIcon(self.ui)
        self.tp.setIcon(tp_icon)

        self.ui_hide = QAction(icon=tp_icon, text='隐藏(Hide)', triggered=self.ui.hide)
        self.ui_show = QAction(icon=tp_icon, text='显示(Show)', triggered=self.ui.show)
        self.ui_exit = QAction(icon=tp_icon, text='退出(Exit)', triggered=self.__quit_app)
        self.tp_menu = QMenu()
        self.tp_menu.addAction(self.ui_hide)
        self.tp_menu.addAction(self.ui_show)
        self.tp_menu.addAction(self.ui_exit)
        self.tp.setContextMenu(self.tp_menu)
        self.tp.activated.connect(self.__tp_connect_action)
        self.tp.show()
        self.tp.showMessage(
            'WSL2AutoPortForward',
            'WSL2端口自动转发工具已启动',
            QSystemTrayIcon.MessageIcon.Information
        )

    def __tp_connect_action(self, activation_reason):
        """
        监听托盘图标点击
        :param activation_reason: 点击类型
        :return:
        """
        if activation_reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 左单击
            if self.ui.isHidden():
                self.ui.show()
            else:
                self.ui.hide()
        elif activation_reason == QSystemTrayIcon.ActivationReason.Context:
            # 右单击
            self.tp_menu.show()
        elif activation_reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击
            self.ui.show()

    def __quit_app(self):
        """
        退出APP
        :return:
        """
        re = QMessageBox.question(
            self.ui,
            "提示",
            "退出系统",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if re == QMessageBox.Yes:
            # 关闭窗体程序
            self.qt_application.quit()
            # 在应用程序全部关闭后，TrayIcon其实还不会自动消失，
            # 直到你的鼠标移动到上面去后，才会消失，
            # 这是个问题，（如同你terminate一些带TrayIcon的应用程序时出现的状况），
            # 这种问题的解决我是通过在程序退出前将其setVisible(False)来完成的。
            self.tp.setVisible(False)

    def __wsl_l_v(self):
        """
        获取wsl信息
        :return:
        """
        wsl_l_v_txt = '  ' + self.wsl2.wsl_l_v(exec_run=True).replace('\x00', '').strip()
        if not wsl_l_v_txt:
            # 未查询到wsl信息提示
            wsl_l_v_txt = '未查询到wsl信息!'
            QMessageBox.information(self.ui, '系统提示', wsl_l_v_txt)
        self.ui.wsl_l_v_text.setPlainText(wsl_l_v_txt)

    def __get_wsl2_ip(self):
        wsl2_ip_info = self.wsl2.get_wsl2_ip()
        if not wsl2_ip_info:
            # 未查询到端口转发信息提示
            QMessageBox.information(self.ui, '系统提示', '未查询到IP信息!')
        else:
            wsl2_ip_info = 'WSL2当前IP为：' + wsl2_ip_info
            self.ui.wsl_l_v_text.setPlainText(wsl2_ip_info)

    def __port_add(self):
        wsl2_ip_info = self.wsl2.get_wsl2_ip()
        if not wsl2_ip_info:
            # 未查询到端口转发信息提示
            QMessageBox.information(self.ui, '系统提示', '未查询到IP信息!')
        else:
            self.ui.result_text.clear()
            ports = self.ui.port_text.toPlainText()
            port_str = ''
            for port in ports.splitlines():
                if not port.strip():
                    continue
                self.__port_add_one(port, wsl2_ip_info)
                port_str += (',' + port if port_str else port)
            self.__fire_wall_rule_add(port_str)
            self.ui.result_text.appendPlainText('Succeed!')

    def __port_del(self, del_port=True, del_fire=True):
        self.ui.result_text.clear()
        ports = self.ui.port_text.toPlainText()
        if del_port:
            for port in ports.splitlines():
                if not port.strip():
                    continue
                self.__port_del_one(port)
        if del_fire:
            self.__fire_wall_rule_del()
        self.ui.result_text.appendPlainText('Succeed!')

    def __port_reset(self):
        port_info = self.wsl2.port_info()
        self.ui.result_text.clear()
        for port in port_info:
            self.__port_del_one(port['port'])
        self.__fire_wall_rule_del()
        self.ui.result_text.appendPlainText('Succeed!')

    def __port_info(self):
        """
        获取端口转发信息
        :return:
        """
        info_str = self.wsl2.port_info(True).strip()
        if not info_str:
            # 未查询到端口转发信息提示
            info_str = '未查询到端口转发信息!'
            QMessageBox.information(self.ui, '系统提示', info_str)
        self.ui.result_text.setPlainText(info_str)

    def __wsl2_auto_port_forward(self):
        """
        一键自动转发
        @return:
        """

        self.__port_del(del_port=False, del_fire=True)
        self.__port_add()

    def __end_wsl(self):
        """
        停止wsl
        :return:
        """
        self.start_qt_process(self.wsl2.end_wsl(exec_run=False))
        info_str = 'wsl 已全部停止'
        QMessageBox.information(self.ui, '系统提示', info_str)

    def __start_wsl(self):
        """
        启动wsl
        :return:
        """
        self.start_qt_process(self.wsl2.start_wsl(exec_run=False))

    def start_wsl_all(self):
        """
        启动wsl并转发端口
        :return:
        """
        self.__start_wsl()
        self.__wsl2_auto_port_forward()

    def __save_settings(self):
        """
        保存全部配置
        :return:
        """
        # 保存脚本
        self.__save_bat_script()

        # 保存配置信息
        self.settings_manage.set('fire_wall_open', self.ui.fire_wall_open.isChecked())
        self.settings_manage.set('fire_wall_close', self.ui.fire_wall_close.isChecked())
        self.settings_manage.set('auto_start_wsl', self.ui.auto_start_wsl.isChecked())
        self.settings_manage.set('ports', self.ui.port_text.toPlainText().splitlines())

        # 保存成功提示
        QMessageBox.information(self.ui, '系统提示', '配置保存成功!')

    def __save_bat_script(self):
        """
        保存启动脚本
        :return:
        """
        content = self.ui.bat_text.toPlainText()
        self.settings_manage.set('wsl_bat_content', content)
        self.wsl2.save_bat_script(content)

    def __fire_wall_rule_add(self, port):
        """
        添加防火墙
        :param port: 端口号，多个端口逗号隔开
        :return:
        """
        if self.ui.fire_wall_open.isChecked():
            self.start_qt_process(
                self.wsl2.fire_wall_rule_add(
                    wsl_port=port,
                    wall_type=self.wsl2.FireWallRuleIn,
                    exec_run=False
                )
            )
            self.ui.result_text.appendPlainText('>>> 添加防火墙：【' + self.wsl2.FireWallRuleIn + '】...')
            self.start_qt_process(
                self.wsl2.fire_wall_rule_add(
                    wsl_port=port,
                    wall_type=self.wsl2.FireWallRuleOut,
                    exec_run=False
                )
            )
            self.ui.result_text.appendPlainText('>>> 添加防火墙：【' + self.wsl2.FireWallRuleOut + '】...')

    def __fire_wall_rule_del(self):
        """
        删除防火墙
        :return:
        """
        if self.ui.fire_wall_close.isChecked():
            self.start_qt_process(
                self.wsl2.fire_wall_rule_del(
                    wall_type=self.wsl2.FireWallRuleIn,
                    exec_run=False
                )
            )
            self.ui.result_text.appendPlainText('>>> 删除防火墙：【' + self.wsl2.FireWallRuleIn + '】...')
            self.start_qt_process(
                self.wsl2.fire_wall_rule_del(
                    wall_type=self.wsl2.FireWallRuleOut,
                    exec_run=False
                )
            )
            self.ui.result_text.appendPlainText('>>> 删除防火墙：【' + self.wsl2.FireWallRuleOut + '】...')

    def __port_add_one(self, port, wsl2_ip_info):
        """
        添加单个端口
        :param port: 端口号
        :param wsl2_ip_info: 转发的IP
        :return:
        """
        self.start_qt_process(self.wsl2.port_add(wsl_ip=wsl2_ip_info, wsl_port=port, exec_run=False))
        self.ui.result_text.appendPlainText('>>> 添加端口：【' + port + '】...')

    def __port_del_one(self, port):
        """
        删除单个端口
        :param port: 端口号
        :return:
        """
        self.start_qt_process(self.wsl2.port_del(wsl_port=port, exec_run=False))
        self.ui.result_text.appendPlainText('>>> 删除端口：【' + port + '】...')

    def start_qt_process(self, cmd):
        """
        启动子进程执行耗时命令
        :param cmd:
        :return:
        """
        process = QProcess(self.ui)
        process.start(cmd)
        result = process.waitForStarted()
        return result
