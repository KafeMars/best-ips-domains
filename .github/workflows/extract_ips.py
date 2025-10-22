import requests
from bs4 import BeautifulSoup
import re

# 定义目标网址
url = "https://api.uouin.com/cloudflare.html"

# 获取网页内容
response = requests.get(url)
html = response.text

# 使用 BeautifulSoup 解析网页
soup = BeautifulSoup(html, "html.parser")

# 查找 <tbody> 中的所有文本内容
tbody = soup.find_all('tbody')

ip_addresses = set()  # 使用 set 来避免重复的 IP 地址

# 正则表达式匹配 IPv4 地址
ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

# 遍历每个 <tbody> 项，提取 IP 地址
for item in tbody:
    text = item.get_text()
    ips = re.findall(ip_pattern, text)
    ip_addresses.update(ips)

# 输出调试信息，看看是否提取到 IP 地址
print(f"Found IP addresses: {ip_addresses}")

# 格式化 IP 地址为 ip:8443
formatted_ips = [f"{ip}:8443" for ip in ip_addresses]

# 输出调试信息，查看格式化后的结果
print(f"Formatted IPs: {formatted_ips}")

# 将 IP 地址保存到文件中
with open('CFIPS', 'w') as f:
    f.write("\n".join(formatted_ips))

# 确保文件写入成功
print(f"File written successfully: {formatted_ips}")
