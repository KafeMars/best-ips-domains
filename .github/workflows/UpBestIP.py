import os
import requests
import base64

# 从环境变量中获取 GitHub Token
cf_token = os.getenv('CF_TOKENS')
if not cf_token:
    raise Exception("环境变量 CF_TOKENS 未设置或为空")

# API 地址
api_url = "https://ipdb.api.030101.xyz/?type=cfv4;cfv6;proxy"

# 获取优选 IP 地址
def get_best_ips():
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        ipv4 = data.get("cfv4", [])
        ipv6 = data.get("cfv6", [])
        proxy_ips = data.get("proxy", [])
        return ipv4, ipv6, proxy_ips
    else:
        raise Exception(f"API 请求失败，状态码：{response.status_code}")

# 更新 GitHub 上的文件
def update_github_file(token, repo, file_path, new_content):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 获取现有文件信息
    response = requests.get(url, headers=headers)
    file_info = response.json()
    sha = file_info['sha']
    content = base64.b64encode(new_content.encode()).decode()

    # 提交更新
    data = {
        "message": f"Update {file_path} with new IPs",
        "committer": {
            "name": "GitHub Actions",
            "email": "actions@github.com"
        },
        "sha": sha,
        "content": content,
        "branch": "main"
    }
    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 200

# 保存 IP 地址到 GitHub
def save_ips_to_github(token, repo, ipv4, ipv6, proxy_ips):
    update_github_file(token, repo, "BestIPs_v4", "\n".join(ipv4))
    update_github_file(token, repo, "BestIPs_v6", "\n".join(ipv6))
    update_github_file(token, repo, "BestProxyIPs", "\n".join(proxy_ips))

# 执行操作
def main():
    ipv4, ipv6, proxy_ips = get_best_ips()
    save_ips_to_github(cf_token, "divericks/best-ips-domains", ipv4, ipv6, proxy_ips)

if __name__ == "__main__":
    main()
