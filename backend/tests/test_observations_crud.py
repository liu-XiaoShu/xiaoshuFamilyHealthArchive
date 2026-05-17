"""观测记录修改与删除。"""

from __future__ import annotations


def _create_person_and_session(client):
    r = client.post(
        "/api/persons",
        json={"name": "测试成员", "gender": "男"},
    )
    assert r.status_code == 200
    person_id = r.json()["id"]
    r2 = client.post(
        f"/api/persons/{person_id}/sessions",
        json={"report_at": "2024-06-01T08:00:00+00:00", "institution": "测试医院"},
    )
    assert r2.status_code == 200
    return person_id, r2.json()["id"]


def _first_leaf_indicator(client) -> int:
    r = client.get("/api/indicators", params={"leaves_only": True, "limit": 1})
    assert r.status_code == 200
    rows = r.json()
    assert rows, "需要至少一条叶子指标（种子数据）"
    return rows[0]["id"]


def test_observation_patch_and_delete(logged_in_client):
    client = logged_in_client
    person_id, session_id = _create_person_and_session(client)
    indicator_id = _first_leaf_indicator(client)

    r = client.post(
        f"/api/persons/{person_id}/sessions/by-id/{session_id}/observations",
        json=[
            {
                "indicator_id": indicator_id,
                "measured_at": "2024-06-01T09:00:00+00:00",
                "value_text": "5.0",
                "ref_text": "3.5-5.5",
                "abnormal": False,
            }
        ],
    )
    assert r.status_code == 200
    obs_id = r.json()[0]["id"]

    r2 = client.patch(
        f"/api/persons/{person_id}/sessions/by-id/{session_id}/observations/{obs_id}",
        json={"value_text": "6.1", "abnormal": True},
    )
    assert r2.status_code == 200
    assert r2.json()["value_text"] == "6.1"
    assert r2.json()["abnormal"] is True

    r3 = client.delete(
        f"/api/persons/{person_id}/sessions/by-id/{session_id}/observations/{obs_id}",
    )
    assert r3.status_code == 204

    r4 = client.get(
        f"/api/persons/{person_id}/sessions/by-id/{session_id}/observations",
    )
    assert r4.status_code == 200
    assert all(o["id"] != obs_id for o in r4.json())
