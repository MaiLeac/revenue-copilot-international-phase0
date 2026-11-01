"""Unit tests for the Dưỡng Nhan 7-Constitution Diagnostic & VietQR Funnel Engine (PROD-01)."""

from __future__ import annotations

from pathlib import Path

import pytest

from assets.duong_nhan_engine.constitution_engine import (
    CONSTITUTION_PROFILES,
    build_vietqr_checkout_url,
    diagnose_constitution,
)
from assets.duong_nhan_engine.handbook_generator import (
    EXTENDED_RECIPES,
    render_handbook_html,
    write_handbook_html,
)


def test_diagnose_constitution_identifies_primary_and_secondary_types() -> None:
    assert len(CONSTITUTION_PROFILES) == 7
    result = diagnose_constitution(["khi_uat", "huyet_u", "khi_uat"])
    assert result.primary_code == "khi_uat"
    assert result.secondary_code == "huyet_u"
    assert "Khí Uất" in result.primary_profile.name_vi
    assert len(result.recommended_recipes) >= 1
    assert any(r.recipe_id == "REC-002" for r in result.recommended_recipes)
    assert len(result.plan_28_days_summary) == 4


def test_every_recipe_includes_safety_contraindications() -> None:
    result = diagnose_constitution(["dam_thap"])
    assert result.primary_code == "dam_thap"
    for rec in result.recommended_recipes:
        assert len(rec.contraindications) >= 1


def test_build_vietqr_checkout_url_encodes_order_and_affiliate_ref() -> None:
    url = build_vietqr_checkout_url(
        bank_id="MB",
        account_no="0123456789",
        account_name="MAI LE",
        amount_vnd=299_000,
        order_code="dn105",
        affiliate_ref="koc_lan",
    )
    assert "MB-0123456789-compact2.png" in url
    assert "amount=299000" in url
    assert "DUONGNHAN%20DN105%20REF%20KOC_LAN" in url


def test_build_vietqr_rejects_non_positive_amount() -> None:
    with pytest.raises(ValueError, match="amount_vnd must be positive"):
        build_vietqr_checkout_url("MB", "0123", "MAI", amount_vnd=0)


def test_duong_nhan_mvp_html_exists_and_contains_quiz_and_vietqr() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    html_path = repo_root / "experiments" / "exp03-duong-nhan-ai-mvp" / "index.html"
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")
    assert "Trắc Nghiệm Chẩn Đoán Nhanh 7 Thể Chất Đông Y" in content
    assert "69.000₫" in content
    assert "img.vietqr.io" in content


def test_duong_nhan_handbook_generator_renders_complete_digital_asset(tmp_path: Path) -> None:
    assert len(EXTENDED_RECIPES) >= 20
    out_file = write_handbook_html(tmp_path / "handbook.html")
    assert out_file.exists()
    html = render_handbook_html()
    assert "Cẩm Nang & Thực Đơn Dưỡng Nhan 7 Thể Chất Đông Y" in html
    assert "speechSynthesis" in html
    assert "Lộ Trình 28 Ngày" in html
