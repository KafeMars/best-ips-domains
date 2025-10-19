#!/usr/bin/env python3
import requests
import json
import os

def fetch_and_save(ip_type, filename):
    """从 API 拉取指定类型的优选 IP 并写入文件"""
    url = f"https://ipdb.api.030101.xyz/?type={ip_type}"
    print(f"Fetching {ip_type} from {url} ...")

    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"[Error] 请求 {ip_type} 失败: {e}")
        return

    text = resp.text.strip()
    # 尝试解析 JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            for key in ("data", "ips", "list", "result"):
                if key in data:
                    data = data[key]
                    break
        if isinstance(data, list):
            output = "\n".join(str(i).strip() for i in data if str(i).strip())
        else:
            output = str(data)
    except Exception:
        # 不是 JSON，直接写原始文本
        output = "\n".join(
            line.strip() for line in text.splitlines() if line.strip()
        )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(output + "\n")
    print(f"[OK] Wrote {filename} ({len(output.splitlines())} lines)")

def main():
    os.makedirs(".", exist_ok=True)
    fetch_and_save("cfv4", "BestIPs_v4")
    fetch_and_save("cfv6", "BestIPs_v6")
    fetch_and_save("proxy", "BestProxyIPs")

if __name__ == "__main__":
    main()
