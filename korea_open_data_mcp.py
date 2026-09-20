"""
korea_open_data_mcp.py
공공데이터포털(data.go.kr) 범용 OpenAPI 호출 MCP 서버 (간소화 버전)

학생이 넣어야 하는 값은 단 2개뿐입니다:
  - baseUrl: 활용가이드 문서(워드파일)에 있는 "서비스 URL" 또는 "Call Back URL"을
             그대로 복사해서 붙여넣기
  - serviceKey: 공공데이터포털에서 발급받은 인증키(Encoding)

API 이름(name)은 baseUrl 마지막 경로에서 자동으로 만들어지므로 따로 입력할 필요가
없습니다. (예: .../gyeongnammarket/gyeongnammarketList -> 이름: gyeongnammarketList)

필요 패키지: mcp, httpx
  pip install "mcp[cli]" httpx

로컬 실행이므로 이 컴퓨터의 일반 네트워크를 그대로 사용합니다 —
Claude 클라우드 컨테이너의 네트워크 허용 목록 제약을 받지 않습니다.
"""

import json
import os
from typing import Any
from urllib.parse import urlparse

import httpx

# mcp 패키지 버전에 따라 클래스 이름이 다릅니다.
#   mcp 1.x: mcp.server.fastmcp.FastMCP
#   mcp 2.x: mcp.server.mcpserver.MCPServer (FastMCP에서 이름 변경됨)
# 둘 다 지원하도록 자동으로 맞춰줍니다.
try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    from mcp.server.mcpserver import MCPServer as FastMCP

mcp = FastMCP("korea-open-data")


# ------------------------------------------------------------------
# 등록된 API 목록 불러오기
#   PUBLIC_APIS 환경변수에 JSON 배열로 등록합니다. 각 항목은 baseUrl과
#   serviceKey 2개만 있으면 됩니다. 예:
#
#   [
#     {
#       "baseUrl": "http://apis.data.go.kr/6480000/gyeongnammarket/gyeongnammarketList",
#       "serviceKey": "발급받은_인증키(Encoding)"
#     },
#     {
#       "baseUrl": "http://apis.data.go.kr/xxxx/yyyy/zzzzList",
#       "serviceKey": "발급받은_인증키(Encoding)"
#     }
#   ]
# ------------------------------------------------------------------

def derive_name(base_url: str) -> str:
    """baseUrl 마지막 경로 조각을 API 이름으로 사용."""
    path = urlparse(base_url).path.rstrip("/")
    return path.split("/")[-1] if path else base_url


def load_registered_apis() -> dict[str, dict[str, str]]:
    raw = os.environ.get("PUBLIC_APIS", "[]")
    try:
        apis = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"PUBLIC_APIS 환경변수 JSON 파싱 실패: {e}")

    registered = {}
    for api in apis:
        name = api.get("name") or derive_name(api["baseUrl"])
        registered[name] = api
    return registered


@mcp.tool()
def list_apis() -> str:
    """현재 이 서버에 등록된 공공데이터 API 목록을 보여줍니다 (이름과 URL)."""
    apis = load_registered_apis()
    if not apis:
        return "등록된 API가 없습니다. PUBLIC_APIS 환경변수를 확인하세요."
    lines = [f"- {name}: {info['baseUrl']}" for name, info in apis.items()]
    return "\n".join(lines)


@mcp.tool()
def call_public_api(
    api_name: str,
    extra_params: dict[str, Any] | None = None,
    num_of_rows: int = 100,
    page_no: int = 1,
) -> str:
    """
    등록된 공공데이터포털 API를 호출합니다.

    Args:
        api_name: list_apis()로 확인한 API 이름 (baseUrl 마지막 경로 조각)
        extra_params: 해당 API가 추가로 요구하는 파라미터 (없으면 생략 가능)
        num_of_rows: 한 번에 받을 데이터 개수 (기본 100)
        page_no: 페이지 번호 (기본 1)

    Returns:
        API 응답 원문 (JSON 텍스트)
    """
    apis = load_registered_apis()
    if api_name not in apis:
        available = ", ".join(apis.keys()) or "(없음)"
        return f"'{api_name}' 은(는) 등록되지 않은 API입니다. 등록된 API: {available}"

    api = apis[api_name]
    base_url = api["baseUrl"]
    service_key = api["serviceKey"]

    # data.go.kr 인증키는 이미 URL-인코딩된 상태(Encoding 키)이므로,
    # httpx가 다시 인코딩하지 않도록 URL을 직접 조립합니다.
    url = (
        f"{base_url}"
        f"?serviceKey={service_key}"
        f"&numOfRows={num_of_rows}"
        f"&pageNo={page_no}"
        f"&resultType=json"
    )

    if extra_params:
        for k, v in extra_params.items():
            url += f"&{k}={v}"

    try:
        resp = httpx.get(url, timeout=15.0)
        resp.raise_for_status()
        return resp.text
    except httpx.HTTPError as e:
        return f"API 호출 오류: {e}"


if __name__ == "__main__":
    mcp.run()
