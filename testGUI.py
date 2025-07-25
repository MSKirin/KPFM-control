import tkinter as tk
import tkinter as tk

def dummy():
    print("按钮被点击")

root = tk.Tk()
root.title("测试窗口")
root.geometry("400x200")

# 注意：以下代码中的行和列的索引应该是整数，而不是字符串
tk.Label(root, text="扫描范围 a (m)").grid(row=0, column=0)
entryrange = tk.Entry(root)
entryrange.grid(row=0, column=1)
entryrange.insert(0, "50")

tk.Label(root, text="步长 d (m)").grid(row=1, column=0)
entrystep = tk.Entry(root)
entrystep.grid(row=1, column=1)
entrystep.insert(0, "5")

tk.Label(root, text="停留时间 (s)").grid(row=2, column=0)
entrydelay = tk.Entry(root)
entrydelay.grid(row=2, column=1)
entrydelay.insert(0, "0.5")

# 注意：这里 command 后面应该是一个函数名，而不是函数调用
tk.Button(root, text="开始扫描", command=dummy).grid(row=3, column=0, columnspan=2)

root.mainloop()

