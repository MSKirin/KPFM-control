import time
import serial

# ==== 参数设置 ====
a = 20.0  # 正方形扫描区域边长（单位：μm）
d = 2.0   # 步长（单位：μm）
pause_time = 0.5  # 每个像素点暂停时间（秒）

# ANC300 串口设置（请根据你电脑上的串口号修改）
serial_port = "/dev/tty.usbmodem01"

# ==== 电压换算 ====
Vmax = 50.0
x_range = 50.0  # X轴最大位移
y_range = 50.0  # Y轴最大位移
volt_per_um_x = Vmax / x_range
volt_per_um_y = Vmax / y_range

# ==== 初始化串口 ====
ser = serial.Serial(serial_port, baudrate=9600, timeout=1)

def send_cmd(cmd):
    """向ANC300发送命令并返回响应"""
    full_cmd = cmd + "\r\n"
    ser.write(full_cmd.encode())
    time.sleep(0.05)
    response = ser.read_all().decode().strip()
    print(f">>> {cmd}\n{response}")
    return response

# ==== 初始化为 offset 模式 ====
send_cmd("setm 1 off")  # X轴
send_cmd("setm 2 off")  # Y轴

# ==== 计算步数 ====
num_steps = int(a / d)

# ==== 开始扫描 ====
for iy in range(num_steps):
    y_pos = iy * d
    y_voltage = y_pos * volt_per_um_y
    send_cmd(f"seta 2 {y_voltage:.3f}")  # 设置Y轴偏压

    for ix in range(num_steps):
        x_pos = ix * d
        x_voltage = x_pos * volt_per_um_x
        send_cmd(f"seta 1 {x_voltage:.3f}")  # 设置X轴偏压

        # 模拟扫描操作
        time.sleep(pause_time)

# ==== 扫描结束，回到原点 ====
send_cmd("seta 1 0.000")
send_cmd("seta 2 0.000")
ser.close()
print("扫描完成！")
