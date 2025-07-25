"""
ANC300 读取电容值示例
--------------------
1. 先用 USB 线把 ANC300 (USB slave 口) 接到电脑。
2. 确认设备管理器/ls /dev/tty* 里出现一个新的串口；把下面的 COM_PORT 改成它。
3. 安装 pyserial:  pip install pyserial
4. 运行脚本，脚本会:
   - 关闭回显
   - 切换到电容测量模式 (cap)
   - 等待测量完成 (capw)
   - 读取并打印 getc 结果
"""

import serial
import time

# === 根据实际情况修改 ===
COM_PORT = "/dev/tty.usbmodem01"        # Windows 示例；macOS/Linux 示例: "/dev/tty.usbserial-FTxxxx"
BAUDRATE = 38400
AXIS_ID  = 3             # 你要测哪一根 ANS/ANP，就写对应轴号 1~7

def send(ser, cmd, delay=0.1):
    """发送命令并返回回显"""
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    return ser.read_all().decode(errors="ignore").strip()

def main():
    try:
        ser = serial.Serial(COM_PORT, BAUDRATE, timeout=1)
    except Exception as e:
        print(f"串口打开失败: {e}")
        return

    # 关闭回显，界面更清爽
    print(send(ser, "echo off"))

    # 步骤 1: 切到 cap 模式
    print(send(ser, f"setm {AXIS_ID} cap"))

    # 步骤 2: 等待测量完成
    print(send(ser, f"capw {AXIS_ID}", delay=0.3))

    # 步骤 3: 读取电容值
    response = send(ser, f"getc {AXIS_ID}")
    print("\n========== 测量结果 ==========")
    print(response)
    print("================================\n")

    ser.close()

if __name__ == "__main__":
    main()
