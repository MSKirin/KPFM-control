# AFM 控制程序框架 v0.1（Python 模拟版）
# 模拟扫描过程、PID控制、成像过程

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -------------------- 扫描参数设置 --------------------
x_range = 5.0  # 扫描范围 (μm)，X方向

y_range = 5.0  # 扫描范围 (μm)，Y方向

step_size = 0.1  # 每步的长度（μm）

# 计算每个方向上的采样点数量
x_points = int(x_range / step_size)
y_points = int(y_range / step_size)

# -------------------- 模拟样品形貌 --------------------
def sample_surface(x, y):
    # 一个虚拟的表面函数，模拟高度变化（单位可看作 μm）
    return 0.5 * np.sin(2 * np.pi * x / 5.0) * np.cos(2 * np.pi * y / 5.0)

# -------------------- PID 控制器类 --------------------
class PIDController:
    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0):
        # 初始化比例、积分、微分增益
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0
        self.prev_error = 0

    def update(self, setpoint, measured, dt):
        # setpoint：目标值；measured：测量值；dt：时间间隔
        error = setpoint - measured  # 当前误差
        self.integral += error * dt  # 积分项累加
        derivative = (error - self.prev_error) / dt if dt > 0 else 0  # 微分项
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative  # PID 输出
        self.prev_error = error  # 保存当前误差供下次使用
        return output

# -------------------- 主扫描函数（非动画） --------------------
def scan_surface():
    height_map = np.zeros((y_points, x_points))  # 初始化形貌图矩阵
    pid = PIDController(Kp=2.0)  # 创建一个 PID 控制器实例
    setpoint = 0.0  # 设定目标偏折信号为 0

    for j in range(y_points):
        y = j * step_size
        for i in range(x_points):
            x = i * step_size
            true_z = sample_surface(x, y)  # 获取真实表面高度
            # 模拟探针测量带有一定噪声
            measured_signal = np.random.normal(loc=true_z, scale=0.02)
            z_adjust = pid.update(setpoint, measured_signal, dt=0.01)  # 调用PID调节高度
            height_map[j, i] = true_z + z_adjust  # 存储调节后的值
    return height_map

# -------------------- 动画显示扫描过程 --------------------
def animate_scan():
    fig, ax = plt.subplots()  # 创建图像窗口和坐标轴
    data = np.zeros((y_points, x_points))  # 初始化图像数据
    im = ax.imshow(data, cmap='viridis', origin='lower', vmin=-1, vmax=1,
                   extent=[0, x_range, 0, y_range])  # 设置显示属性

    pid = PIDController(Kp=2.0)  # 新建一个PID控制器实例
    setpoint = 0.0  # 设置偏折信号目标值

    # 每一帧更新一行图像
    def update(frame):
        y = frame * step_size
        for i in range(x_points):
            x = i * step_size
            true_z = sample_surface(x, y)  # 当前点的真实高度
            measured_signal = np.random.normal(loc=true_z, scale=0.02)  # 模拟测量信号
            z_adjust = pid.update(setpoint, measured_signal, dt=0.01)  # PID 计算反馈
            data[frame, i] = true_z + z_adjust  # 存入图像
        im.set_array(data)  # 更新图像
        return [im]

    # 设置动画：每帧调用 update() 更新一行
    ani = animation.FuncAnimation(fig, update, frames=range(y_points), blit=True, interval=50, repeat=False)
    plt.title("AFM 扫描模拟")
    plt.xlabel("X (μm)")
    plt.ylabel("Y (μm)")
    plt.show()

# -------------------- 执行主程序 --------------------
if __name__ == "__main__":
    animate_scan()  # 运行动画模拟
