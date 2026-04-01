#!/usr/bin/env python3
"""
独立的 GLM API 调用脚本（通过 curl -v）
接收 JSON 参数，输出 JSON 结果。

使用 -v 标志确保 curl 在 uvicorn 线程池环境中正常工作。
"""
import sys
import json
import subprocess

def main():
    try:
        data = json.loads(sys.stdin.read())
    except:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)

    api_key = data.get("api_key")
    api_base = data.get("api_base", "https://open.bigmodel.cn/api/paas/v4")
    model = data.get("model", "glm-4.6v")
    messages = data.get("messages", [])

    if not api_key:
        print(json.dumps({"error": "Missing API key"}))
        sys.exit(1)

    url = f"{api_base}/chat/completions"
    payload = json.dumps({"model": model, "messages": messages}, ensure_ascii=False)

    # -v 确保使用 HTTP/1.1 并在 uvicorn 线程池环境中正常连接
    curl_cmd = [
        "curl", "-v", "-s", "--max-time", "180",
        "-X", "POST", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "--data-raw", payload,
    ]

    result = subprocess.run(
        curl_cmd,
        capture_output=True,
        text=True,
        timeout=200,
    )

    if result.returncode != 0:
        print(json.dumps({"error": f"Curl failed (rc={result.returncode}): {result.stderr[:300]}"}))
        sys.exit(1)

    # 从 stdout 提取 JSON：跳过 verbose 行，从第一个 { 开始
    first_brace = result.stdout.find("{")
    if first_brace == -1:
        print(json.dumps({"error": f"No JSON found in response: {result.stdout[:200]}"}))
        sys.exit(1)

    print(result.stdout[first_brace:])

if __name__ == "__main__":
    main()
