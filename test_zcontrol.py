import serial
import time

# 替换为你的串口号
ser = serial.Serial('/dev/tty.usbmodem123456', baudrate=9600, timeout=1)

# 发送指令函数
def send_cmd(cmd):
    ser.write((cmd + '\r\n').encode())
    time.sleep(0.1)
    reply = ser.read_all().decode()
    print(">>", cmd)
    print("<<", reply.strip())
    return reply

# 查询设备信息
send_cmd("*IDN?")

# 设置 z 轴模块编号为 1（示例）
# 如果你将 ANPz101/LT 插在 slot1，那就是 channel 1
z_channel = 1

# 移动 Z 轴到目标位置（单位可能是 um 或 steps，需查说明书）
# 示例命令（假设开环）：
send_cmd(f"mov {z_channel} 20")   # 移动到20单位位置
send_cmd(f"pos? {z_channel}")     # 查询当前位置

# 关闭串口
ser.close()
