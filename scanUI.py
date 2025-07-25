import sys
import time
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal


class ScanThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, port, a, d, delay):
        super().__init__()
        self.port = port
        self.a = a
        self.d = d
        self.delay = delay
        self._is_running = True

    def run(self):
        try:
            ser = serial.Serial(self.port, 9600, timeout=1)
        except Exception as e:
            self.log_signal.emit(f"打开串口失败: {e}")
            self.finished_signal.emit()
            return

        axes = {1: 'X', 2: 'Y'}

        # 设置offset模式
        for axis in axes:
            cmd = f"setm {axis} off"
            ser.write((cmd + '\r\n').encode())
            time.sleep(0.05)
            _ = ser.read_all()

        positions = self.generate_scan_positions(self.a, self.d)

        for x_pos, y_pos in positions:
            if not self._is_running:
                break
            x_volt = self.position_to_voltage(x_pos)
            y_volt = self.position_to_voltage(y_pos)
            cmd_x = f"seta 1 {x_volt:.3f}"
            cmd_y = f"seta 2 {y_volt:.3f}"
            ser.write((cmd_x + '\r\n').encode())
            time.sleep(0.05)
            ser.write((cmd_y + '\r\n').encode())
            time.sleep(0.05)
            self.log_signal.emit(f"移动到 X: {x_pos:.2f}μm (电压{ x_volt:.2f}V), Y: {y_pos:.2f}μm (电压{ y_volt:.2f}V)")
            time.sleep(self.delay)

        # 扫描结束后接地
        for axis in axes:
            cmd = f"setm {axis} gnd"
            ser.write((cmd + '\r\n').encode())
            time.sleep(0.05)
            _ = ser.read_all()

        ser.close()
        self.log_signal.emit("扫描完成！")
        self.finished_signal.emit()

    def stop(self):
        self._is_running = False

    def generate_scan_positions(self, a, d):
        num_steps = int(a / d) + 1
        positions = []
        for i in range(num_steps):
            for j in range(num_steps):
                x = i * d
                y = j * d if i % 2 == 0 else (num_steps - 1 - j) * d  # 折返扫描
                positions.append((x, y))
        return positions

    def position_to_voltage(self, pos):
        # 60V 对应 50μm 固定映射
        return min(60.0, max(0.0, 60.0 * pos / 50.0))


class ANC300ScanGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANC300 XY 扫描控制器")
        self.setGeometry(300, 300, 600, 450)

        self.scan_thread = None

        main_layout = QVBoxLayout()

        # 参数输入区
        param_layout = QHBoxLayout()

        param_layout.addWidget(QLabel("扫描范围 a (μm):"))
        self.entry_range = QLineEdit("50")
        param_layout.addWidget(self.entry_range)

        param_layout.addWidget(QLabel("步长 d (μm):"))
        self.entry_step = QLineEdit("5")
        param_layout.addWidget(self.entry_step)

        param_layout.addWidget(QLabel("停留时间 (秒):"))
        self.entry_delay = QLineEdit("0.5")
        param_layout.addWidget(self.entry_delay)

        main_layout.addLayout(param_layout)

        # 串口号输入
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("串口号:"))
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("/dev/tty.usbmodemXXXXX")
        port_layout.addWidget(self.port_input)

        # 自动检测串口按钮
        self.btn_find_port = QPushButton("自动检测串口")
        self.btn_find_port.clicked.connect(self.find_port)
        port_layout.addWidget(self.btn_find_port)

        main_layout.addLayout(port_layout)

        # 开始和停止扫描按钮
        btn_layout = QHBoxLayout()

        self.btn_start_scan = QPushButton("开始扫描")
        self.btn_start_scan.clicked.connect(self.start_scan)
        btn_layout.addWidget(self.btn_start_scan)

        self.btn_stop_scan = QPushButton("停止扫描")
        self.btn_stop_scan.clicked.connect(self.stop_scan)
        self.btn_stop_scan.setEnabled(False)  # 默认禁用
        btn_layout.addWidget(self.btn_stop_scan)

        main_layout.addLayout(btn_layout)

        # 日志显示区
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        self.setLayout(main_layout)

    def log(self, msg):
        self.log_area.append(msg)

    def find_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                ser.write(b"ver\r\n")
                time.sleep(0.1)
                response = ser.read_all().decode(errors='ignore')
                ser.close()
                if "ANC300" in response:
                    self.port_input.setText(port.device)
                    self.log(f"发现ANC300串口: {port.device}")
                    return
            except:
                continue
        self.log("未找到ANC300串口，请检查连接。")

    def start_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            QMessageBox.warning(self, "警告", "扫描正在进行中，请稍后。")
            return

        try:
            a = float(self.entry_range.text())
            d = float(self.entry_step.text())
            delay = float(self.entry_delay.text())
            if a <= 0 or d <= 0 or delay < 0:
                raise ValueError
            if d > a:
                QMessageBox.warning(self, "参数错误", "步长不能大于扫描范围。")
                return
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的正数参数。")
            return

        port = self.port_input.text().strip()
        if not port:
            QMessageBox.warning(self, "错误", "请填写串口号或使用自动检测。")
            return

        self.scan_thread = ScanThread(port, a, d, delay)
        self.scan_thread.log_signal.connect(self.log)
        self.scan_thread.finished_signal.connect(self.scan_finished)
        self.scan_thread.start()

        self.btn_start_scan.setEnabled(False)
        self.btn_stop_scan.setEnabled(True)
        self.log("开始扫描...")

    def stop_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.log("停止扫描请求已发送，等待线程结束...")

    def scan_finished(self):
        self.log("扫描线程结束。")
        self.btn_start_scan.setEnabled(True)
        self.btn_stop_scan.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ANC300ScanGUI()
    win.show()
    sys.exit(app.exec_())
