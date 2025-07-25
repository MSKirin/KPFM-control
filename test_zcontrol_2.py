import sys
import serial
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
        self.setWindowTitle("ANC300 控制器图形界面")
        self.setGeometry(100, 100, 500, 300)

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

        # 输出显示
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def connect_serial(self):
        try:
            port = self.port_input.text()
            self.ser = serial.Serial(port, baudrate=9600, timeout=1)
            self.output_area.append(f"已连接到 {port}")
        except Exception as e:
            self.output_area.append(f"连接失败: {str(e)}")

    def send_command(self):
        if self.ser:
            cmd = self.cmd_input.text()
            self.ser.write((cmd + '\r\n').encode())
            time.sleep(0.1)
            reply = self.ser.read_all().decode().strip()
            self.output_area.append(f">> {cmd}\n<< {reply}")
        else:
            self.output_area.append("未连接串口")

    def move_z(self):
        self.cmd_input.setText("mov 1 20")
        self.send_command()

    def query_z(self):
        self.cmd_input.setText("pos? 1")
        self.send_command()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ANC300Controller()
    window.show()
    sys.exit(app.exec_())
