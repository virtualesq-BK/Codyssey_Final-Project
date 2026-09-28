"""E2E API 테스트 (실제 LLM 호출 없음)."""

from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_returns_202_and_analysis_id():
    r = client.post(
        "/api/analyze",
        json={
            "business_idea": "AI 회계 도우미 SaaS",
            "target_customer": "소상공인",
            "target_market": "한국",
            "country": "KR",
            "price": 29000,
        },
    )
    assert r.status_code == 202
    body = r.json()
    assert "analysis_id" in body
    assert body["status"] == "accepted"


def test_analyze_missing_idea_returns_422():
    r = client.post("/api/analyze", json={"business_idea": ""})
    assert r.status_code == 422


def test_get_analysis_unknown_id_returns_404():
    r = client.get("/api/analysis/nonexistent-id-00000")
    assert r.status_code == 404


def test_analyze_and_get_result():
    """analyze → analysis_id → 결과 조회 흐름."""
    post = client.post(
        "/api/analyze",
        json={"business_idea": "드론 배달 스타트업", "country": "KR"},
    )
    assert post.status_code == 202
    analysis_id = post.json()["analysis_id"]

    # TestClient는 동기 실행이므로 BackgroundTask가 완료된 뒤 조회
    get = client.get(f"/api/analysis/{analysis_id}")
    assert get.status_code == 200
    data = get.json()
    assert data["analysis_id"] == analysis_id
    assert data["status"] in ("processing", "completed", "failed")
