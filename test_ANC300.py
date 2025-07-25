

import serial
import time

def send_command(ser, cmd, wait=0.1):
    """发送命令并读取响应"""
    cmd_line = cmd + '\r\n'  # ANC300命令结尾是CR+LF
    ser.write(cmd_line.encode())
    time.sleep(wait)  # 等待设备响应
    response = ser.read_all().decode(errors='ignore')
    return response.strip()

def main():
    # 修改为你的串口号和波特率
    port = '/dev/tty.usbmodem01'  # Windows示例，Mac/Linux可能是'/dev/ttyUSB0'或'/dev/tty.usbserial'
    baudrate = 38400

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
    except Exception as e:
        print(f'打开串口失败: {e}')
        return

    # 测试流程示例
    commands = [
        'setm 1 stp',      # 轴1设置为步进模式
        'setf 1 1000',     # 设置轴1步进频率为1000 Hz
        'setv 1 20',       # 设置轴1步进幅度为20 V
        'stepu 1 1000',    # 轴1向上移动1000步
        'setm 2 off',      # 轴2设置为偏置模式
        'seta 2 2.345678', # 设置轴2偏置电压
        'geta 2',          # 读取轴2偏置电压
        'geto 1',          # 读取轴1输出电压
        'stepu 1 10000',   # 轴1向上移动10000步
        'geto 1'           # 读取轴1输出电压
    ]

    for cmd in commands:
        print(f"> {cmd}")
        resp = send_command(ser, cmd)
        print(resp)

    ser.close()

if __name__ == '__main__':
    main()

