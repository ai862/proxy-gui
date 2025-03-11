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
        self.proxy_addr.insert(0, '127.0.0.1')
        self.proxy_addr.grid(row=0, column=1)

        tk.Label(self.proxy_frame, text="端口:").grid(row=1, column=0)
        self.proxy_port = tk.Entry(self.proxy_frame)
        self.proxy_port.insert(0, '8080')
        self.proxy_port.grid(row=1, column=1)

        tk.Label(self.proxy_frame, text="排除地址:").grid(row=2, column=0)
        self.proxy_exclude = tk.Entry(self.proxy_frame)
        self.proxy_exclude.grid(row=2, column=1)

        # 新增：网络测试地址输入框
        tk.Label(self.proxy_frame, text="网络测试地址:").grid(row=3, column=0)
        self.test_url = tk.Entry(self.proxy_frame)
        self.test_url.insert(0, 'https://www.google.com')
        self.test_url.grid(row=3, column=1)

        # 新增：是否忽略 SSL 验证的复选框
        self.ignore_ssl_var = tk.IntVar()
        tk.Checkbutton(self.proxy_frame, text="忽略 SSL 验证", variable=self.ignore_ssl_var).grid(row=4, column=0, columnspan=2)
        # 新增：自定义 CA 证书路径输入框
        tk.Label(self.proxy_frame, text="自定义 CA 证书路径:").grid(row=5, column=0)
        self.ca_cert_path = tk.Entry(self.proxy_frame)
        self.ca_cert_path.grid(row=5, column=1)

        # 代理状态标签
        self.status_label = tk.Label(self.proxy_frame, text="代理状态: 未知")
        self.status_label.grid(row=6, column=0, columnspan=2)
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
            test_url = self.test_url.get()
            ignore_ssl = self.ignore_ssl_var.get()
            ca_cert = self.ca_cert_path.get().strip()  # 增加strip处理
            
            # 新增代理配置获取
            proxy_host = self.proxy_addr.get()
            proxy_port = self.proxy_port.get()
            proxies = {
                "http": f"http://{proxy_host}:{proxy_port}",
                "https": f"http://{proxy_host}:{proxy_port}"
            } if proxy_host and proxy_port else None

            # 增加证书路径验证
            if ca_cert and not os.path.exists(ca_cert):
                raise FileNotFoundError(f"CA证书路径不存在: {ca_cert}")

            if ignore_ssl:
                verify = False
            elif ca_cert:
                verify = ca_cert
            else:
                verify = True

            response = requests.get(test_url, 
                                   timeout=5, 
                                   verify=verify,
                                   proxies=proxies)  # 添加proxies参数
            if response.status_code == 200:
                messagebox.showinfo("成功", "网络连接正常！")
            else:
                messagebox.showwarning("警告", "网络连接存在问题")
        except FileNotFoundError as e:
            messagebox.showerror("证书错误", f"证书路径错误: {str(e)}")
        except requests.exceptions.ProxyError as e:
            messagebox.showerror("代理错误", f"无法连接到代理服务器: {proxy_host}:{proxy_port}\n{str(e)}, 请检查代理设置是否正确")
        except requests.exceptions.Timeout as e:
            messagebox.showerror("超时错误", f"连接超时: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            messagebox.showerror("连接错误", f"无法连接到服务器: {str(e)}")
        except requests.exceptions.SSLError as e:
            messagebox.showerror("SSL 错误", f"SSL 验证失败: {str(e)}")
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