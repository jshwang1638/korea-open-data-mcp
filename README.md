# korea-open-data-mcp

공공데이터포털(data.go.kr)의 여러 OpenAPI를 **하나의 MCP 서버**로 호출할 수 있게 해주는 범용 도구입니다.

data.go.kr에 등록된 대부분의 API는 `serviceKey` / `numOfRows` / `pageNo` / `resultType`
같은 표준 파라미터 규격을 공통으로 씁니다. 그래서 API마다 새 MCP 서버를 만들 필요 없이,
**서비스 URL과 인증키 2개만 등록하면** 바로 호출할 수 있습니다.

## 특징

- API마다 별도 코드 작성 불필요 — 등록만 하면 끝
- Claude Desktop, Claude Code 등 MCP를 지원하는 모든 클라이언트에서 사용 가능
- 로컬에서 실행되므로 별도의 서버 호스팅이 필요 없음
- `mcp` 패키지 1.x / 2.x(`FastMCP` → `MCPServer` 개명) 모두 자동 호환

## 설치

### 1. 저장소 클론
```bash
git clone https://github.com/jshwang1638/korea-open-data-mcp.git
cd korea-open-data-mcp
```

### 2. 패키지 설치
**Windows (PowerShell)** — PC 설치:
```bash
pip install "mcp[cli]" httpx
```

**Windows (PowerShell)** — PC에 설치된 모든 파이썬 버전에 한 번에 설치:
```powershell
Get-ChildItem "$env:LOCALAPPDATA\Programs\Python" -Directory -Filter "Python3*" | ForEach-Object { & "$($_.FullName)\python.exe" -m pip install "mcp[cli]" httpx }
```powershell

여러 파이썬 버전이 설치되어 있다면, MCP 클라이언트(Claude Desktop 등)가 실제로 실행하는 파이썬에 패키지가 설치되어 있어야 합니다. 위 Windows 명령은 이 문제를 자동으로 해결해줍니다.

## Claude Desktop 설정

`claude_desktop_config.json`에 아래처럼 등록하세요.

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "korea-open-data": {
      "command": "python",
      "args": ["/절대경로/korea_open_data_mcp.py"],
      "env": {
        "PUBLIC_APIS": "[{\"baseUrl\":\"http://apis.data.go.kr/6480000/gyeongnammarket/gyeongnammarketList\",\"serviceKey\":\"발급받은_인증키(Encoding)\"}]"
      }
    }
  }
}
```

설정 후 클라이언트를 완전히 재시작하세요.

## API 등록 방법

`PUBLIC_APIS` 환경변수에 JSON 배열로 등록합니다. 각 항목에 필요한 값은 단 2개입니다.

| 필드 | 설명 | 어디서 얻나 |
|---|---|---|
| `baseUrl` | 호출할 API의 엔드포인트 URL | 공공데이터포털 "활용가이드" 문서의 **Call Back URL** (또는 서비스 URL) |
| `serviceKey` | 인증키 (Encoding 버전) | 공공데이터포털 마이페이지 → 개발계정 |

```json
[
  {
    "baseUrl": "http://apis.data.go.kr/6480000/gyeongnammarket/gyeongnammarketList",
    "serviceKey": "발급받은_인증키"
  },
  {
    "baseUrl": "http://apis.data.go.kr/xxxx/yyyy/zzzzList",
    "serviceKey": "다른_인증키"
  }
]
```

API 이름은 `baseUrl`의 마지막 경로 조각에서 자동으로 만들어집니다.
(예: `.../gyeongnammarket/gyeongnammarketList` → 이름 `gyeongnammarketList`)

## 제공 도구

- **`list_apis()`** — 등록된 API 목록과 URL을 보여줍니다.
- **`call_public_api(api_name, extra_params, num_of_rows, page_no)`** — 등록된 API를 호출하고 JSON 응답을 반환합니다.

## 사용 예시

Claude에서 이렇게 요청하면 됩니다.

> "경남 전통시장 API 조회해줘"
> "gyeongnammarketList 데이터 10개만 가져와줘"

## 보안 주의사항

- `serviceKey`는 개인 인증키입니다. **공개 저장소에 실제 키를 커밋하지 마세요.**
- 이 저장소를 fork/clone해서 쓸 때는 본인의 `claude_desktop_config.json`(로컬 설정 파일, git에 포함되지 않음)에만 키를 넣으세요.
- `PUBLIC_APIS` 예시에 있는 값은 데모용이며 실제 키가 아닙니다.

## 라이선스

MIT
