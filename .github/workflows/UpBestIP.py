import os
import requests

# ------------------------- 配置区 -------------------------
# 从环境变量中获取 Cloudflare API Token，可以是单个或多个（逗号分割）
cf_tokens_str = os.getenv("CF_TOKENS", "").strip()
if not cf_tokens_str:
    raise Exception("环境变量 CF_TOKENS 未设置或为空")
api_tokens = [token.strip() for token in cf_tokens_str.split(",") if token.strip()]

# 子域名与对应的 IP 列表 URL 配置
# 仅使用你的 best-ips-domains 仓库
subdomain_configs = {
    "bestcf": {
        "v4": "https://raw.githubusercontent.com/divericks/best-ips-domains/main/BestIPs_v4",
        "v6": "https://raw.githubusercontent.com/divericks/best-ips-domains/main/BestIPs_v6"
    },
    "bestproxy": {
        "v4": "https://raw.githubusercontent.com/divericks/best-ips-domains/main/BestProxyIPs"
    }
}
# -----------------------------------------------------------

# DNS 记录类型映射
dns_record_map = {
    "v4": "A",
    "v6": "AAAA"
}

# 获取指定 URL 的 IP 列表，仅返回前两行
def fetch_ip_list(url: str) -> list:
    response = requests.get(url)
    response.raise_for_status()
    ip_lines = [line.strip() for line in response.text.strip().splitlines() if line.strip()]
    return ip_lines[:2]

# 获取 Cloudflare 第一个域区的信息，返回 (zone_id, domain)
def fetch_zone_info(api_token: str) -> tuple:
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://api.cloudflare.com/client/v4/zones", headers=headers)
    response.raise_for_status()
    zones = response.json().get("result", [])
    if not zones:
        raise Exception("未找到域区信息")
    return zones[0]["id"], zones[0]["name"]

# 更新 DNS 记录
def update_dns_record(api_token: str, zone_id: str, subdomain: str, domain: str, dns_type: str, operation: str, ip_list: list = None):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    full_record_name = domain if subdomain == "@" else f"{subdomain}.{domain}"

    if operation == "delete":
        while True:
            query_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type={dns_type}&name={full_record_name}"
            response = requests.get(query_url, headers=headers)
            response.raise_for_status()
            records = response.json().get("result", [])
            if not records:
                break
            for record in records:
                del_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record['id']}"
                del_resp = requests.delete(del_url, headers=headers)
                del_resp.raise_for_status()
                print(f"删除 {subdomain} {dns_type} 记录: {record['id']}")
    elif operation == "add" and ip_list:
        for ip in ip_list:
            payload = {
                "type": dns_type,
                "name": full_record_name,
                "content": ip,
                "ttl": 1,
                "proxied": False
            }
            response = requests.post(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                                     json=payload, headers=headers)
            if response.status_code == 200:
                print(f"添加 {subdomain} {dns_type} 记录: {ip}")
            else:
                print(f"添加 {dns_type} 记录失败: {subdomain} IP {ip} 错误 {response.status_code} {response.text}")

def main():
    try:
        for idx, token in enumerate(api_tokens, start=1):
            print("=" * 50)
            print(f"开始处理 API Token #{idx}")
            zone_id, domain = fetch_zone_info(token)
            print(f"域区 ID: {zone_id} | 域名: {domain}")

            for subdomain, version_urls in subdomain_configs.items():
                for version_key, url in version_urls.items():
                    dns_type = dns_record_map.get(version_key)
                    if not dns_type:
                        continue
                    ips = fetch_ip_list(url)
                    update_dns_record(token, zone_id, subdomain, domain, dns_type, "delete")
                    if ips:
                        update_dns_record(token, zone_id, subdomain, domain, dns_type, "add", ips)
                    else:
                        print(f"{subdomain} ({dns_type}) 未获取到 IP")
            print(f"结束处理 API Token #{idx}")
            print("=" * 50 + "\n")
    except Exception as err:
        print(f"错误: {err}")

if __name__ == "__main__":
    main()
