import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import time

# 自动识别 ANC300 控制器的串口
def find_anc300_port(baudrate=9600, timeout=1):
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        try:
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)
            ser.write(b"ver\r\n")
            response = ser.read(128).decode(errors='ignore')
            if "OK" in response:
                print(f"✅ 发现 ANC300 控制器在串口: {port.device}")
                return port.device
            ser.close()
        except Exception:
            continue
    return None

# 向串口发送命令并等待回应
def send_command(ser, command):
    ser.write((command + '\r\n').encode())
    time.sleep(0.1)
    return ser.read_all().decode(errors='ignore')

# 生成扫描路径
def generate_scan_positions(a, d):
    num_steps = int(a / d) + 1
    positions = []
    for i in range(num_steps):
        for j in range(num_steps):
            x = i * d
            y = j * d if i % 2 == 0 else (num_steps - 1 - j) * d  # 折返扫描
            positions.append((x, y))
    return positions

# 将电压值映射到实际电压范围（0~60V）
def position_to_voltage(pos, max_range=50):
    return min(60.0, max(0.0, 60.0 * pos / max_range))

# 扫描函数
def start_scan():
    try:
        a = float(entry_range.get())
        d = float(entry_step.get())
        delay = float(entry_delay.get())
    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的数字。")
        return

    port = find_anc300_port()
    if not port:
        messagebox.showerror("错误", "未找到 ANC300 控制器，请检查连接。")
        return

    ser = serial.Serial(port, 9600, timeout=1)
    axes = {1: 'X', 2: 'Y'}

    # 设置offset模式
    for axis in axes:
        send_command(ser, f"setm {axis} off")

    positions = generate_scan_positions(a, d)
    for x_pos, y_pos in positions:
        x_volt = position_to_voltage(x_pos, max_range=a)
        y_volt = position_to_voltage(y_pos, max_range=a)
        send_command(ser, f"seta 1 {x_volt:.3f}")
        send_command(ser, f"seta 2 {y_volt:.3f}")
        print(f"已移动到位置 X: {x_volt:.2f} V, Y: {y_volt:.2f} V")
        root.update()
        time.sleep(delay)

    # 扫描完成后接地
    for axis in axes:
        send_command(ser, f"setm {axis} gnd")

    ser.close()
    messagebox.showinfo("完成", "扫描完成！")

# GUI 构建
root = tk.Tk()
root.title("ANC300 XY 扫描控制器")

tk.Label(root, text="扫描范围 a (μm)").grid(row=0, column=0)
entry_range = tk.Entry(root)
entry_range.insert(0, "50")
entry_range.grid(row=0, column=1)

tk.Label(root, text="步长 d (μm)").grid(row=1, column=0)
entry_step = tk.Entry(root)
entry_step.insert(0, "5")
entry_step.grid(row=1, column=1)

tk.Label(root, text="停留时间 (s)").grid(row=2, column=0)
entry_delay = tk.Entry(root)
entry_delay.insert(0, "0.5")
entry_delay.grid(row=2, column=1)

tk.Button(root, text="开始扫描", command=start_scan).grid(row=3, column=0, columnspan=2)

root.mainloop()
