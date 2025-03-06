import tkinter as tk
from tkinter import messagebox
import winreg
import requests

class ProxySetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("系统代理设置")
        # 窗口居中
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = int((screen_width - 400) / 2)
        y = int((screen_height - 300) / 2)
        root.geometry(f'400x300+{x}+{y}')

        # 代理设置框架
        self.proxy_frame = tk.LabelFrame(root, text="代理设置")
        self.proxy_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(self.proxy_frame, text="代理地址:").grid(row=0, column=0)
        self.proxy_addr = tk.Entry(self.proxy_frame)
        self.proxy_addr.insert(0, '10.211.55.2')
        self.proxy_addr.grid(row=0, column=1)

        tk.Label(self.proxy_frame, text="端口:").grid(row=1, column=0)
        self.proxy_port = tk.Entry(self.proxy_frame)
        self.proxy_port.insert(0, '8080')
        self.proxy_port.grid(row=1, column=1)

        tk.Label(self.proxy_frame, text="排除地址:").grid(row=2, column=0)
        self.proxy_exclude = tk.Entry(self.proxy_frame)
        self.proxy_exclude.grid(row=2, column=1)

        # 代理状态标签
        self.status_label = tk.Label(self.proxy_frame, text="代理状态: 未知")
        self.status_label.grid(row=3, column=0, columnspan=2)
        self.update_proxy_status()

        # 控制按钮
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(padx=10, pady=10)

        tk.Button(self.btn_frame, text="设置代理", command=self.set_proxy).pack(side="left", padx=5)
        tk.Button(self.btn_frame, text="测试连接", command=self.test_connection).pack(side="left", padx=5)
        tk.Button(self.btn_frame, text="关闭代理", command=self.disable_proxy).pack(side="left", padx=5)

    def set_proxy(self):
        try:
            proxy = f"{self.proxy_addr.get()}:{self.proxy_port.get()}"
            # 修改注册表设置代理
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            if self.proxy_exclude.get():
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, self.proxy_exclude.get())
            winreg.CloseKey(key)
            messagebox.showinfo("成功", "代理设置成功！")
            self.update_proxy_status()
        except Exception as e:
            messagebox.showerror("错误", f"代理设置失败: {str(e)}")

    def disable_proxy(self):
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            messagebox.showinfo("成功", "代理已关闭！")
            self.update_proxy_status()
        except Exception as e:
            messagebox.showerror("错误", f"关闭代理失败: {str(e)}")

    def test_connection(self):
        try:
            response = requests.get("http://www.google.com", timeout=5)
            if response.status_code == 200:
                messagebox.showinfo("成功", "网络连接正常！")
            else:
                messagebox.showwarning("警告", "网络连接存在问题")
        except Exception as e:
            messagebox.showerror("错误", f"网络连接失败: {str(e)}")

    def update_proxy_status(self):
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 0, winreg.KEY_READ)
            status = winreg.QueryValueEx(key, "ProxyEnable")[0]
            winreg.CloseKey(key)
            if status == 1:
                self.status_label.config(text="代理状态: 已开启")
            else:
                self.status_label.config(text="代理状态: 已关闭")
        except Exception as e:
            self.status_label.config(text="代理状态: 未知")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProxySetupApp(root)
    root.mainloop()