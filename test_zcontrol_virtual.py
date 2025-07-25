import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit
)

class ANC300Controller(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.ser = None  # 串口初始化为空

    def initUI(self):
        self.setWindowTitle("ANC300 控制器图形界面（测试模式）")
        self.setGeometry(100, 100, 500, 350)

        layout = QVBoxLayout()

        # 串口设置
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("串口号:"))
        self.port_input = QLineEdit("/dev/tty.usbmodemXXXXX")
        port_layout.addWidget(self.port_input)
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.connect_serial)
        port_layout.addWidget(self.connect_btn)
        layout.addLayout(port_layout)

        # 指令输入
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("发送指令:"))
        self.cmd_input = QLineEdit()
        cmd_layout.addWidget(self.cmd_input)
        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self.send_command)
        cmd_layout.addWidget(self.send_btn)
        layout.addLayout(cmd_layout)

        # 预设按钮
        move_layout = QHBoxLayout()
        self.move_btn = QPushButton("Z轴移动到 20")
        self.move_btn.clicked.connect(self.move_z)
        move_layout.addWidget(self.move_btn)
        self.query_btn = QPushButton("查询Z轴位置")
        self.query_btn.clicked.connect(self.query_z)
        move_layout.addWidget(self.query_btn)
        layout.addLayout(move_layout)

        # 自定义Z轴位置输入
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("目标Z轴位置:"))
        self.custom_pos_input = QLineEdit("50")
        custom_layout.addWidget(self.custom_pos_input)
        self.custom_move_btn = QPushButton("移动到该位置")
        self.custom_move_btn.clicked.connect(self.custom_move_z)
        custom_layout.addWidget(self.custom_move_btn)
        layout.addLayout(custom_layout)

        # 输出显示
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def connect_serial(self):
        self.ser = True
        self.output_area.append("（测试模式）已连接到虚拟串口")

    def send_command(self):
        if self.ser:
            cmd = self.cmd_input.text()
            time.sleep(0.1)

            # 初始化 current_z 属性（模拟当前位置）
            if not hasattr(self, 'current_z'):
                self.current_z = 20

            if cmd == "*IDN?":
                reply = "ANC300 模拟器 v1.0"
            elif cmd.startswith("mov"):
                try:
                    parts = cmd.strip().split()
                    if len(parts) == 3:
                        self.current_z = int(parts[2])  # 更新模拟的位置
                        reply = "OK"
                    else:
                        reply = "错误的移动命令格式"
                except:
                    reply = "无法解析位置"
            elif cmd.startswith("pos?"):
                reply = str(self.current_z)
            else:
                reply = "未知指令"

            self.output_area.append(f">> {cmd}\n<< {reply}")
        else:
            self.output_area.append("未连接串口")

    def move_z(self):
        self.cmd_input.setText("mov 1 20")
        self.send_command()

    def query_z(self):
        self.cmd_input.setText("pos? 1")
        self.send_command()

    def custom_move_z(self):
        pos = self.custom_pos_input.text()
        self.cmd_input.setText(f"mov 1 {pos}")
        self.send_command()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ANC300Controller()
    window.show()
    sys.exit(app.exec_())