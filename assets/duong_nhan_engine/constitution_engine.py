"""Deterministic 7-Body-Type Diagnostic, Recipe Lookup & VietQR Funnel Engine (PROD-01).

Implements the improved business mechanism over biquyetduongnhan.vn:
1. Interactive constitution scoring across the 7 traditional body types (0 VND LLM cost).
2. Symptom-based instant recipe & contraindication lookup (fixes static 664-page ebook UX).
3. VietQR / SePay payment link & KOC affiliate tracking payload generator.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True)
class BodyConstitutionProfile:
    code: str
    name_vi: str
    tagline: str
    facial_signs: list[str]
    body_signs: list[str]
    core_principle: str
    foods_to_prioritize: list[str]
    foods_to_avoid: list[str]


@dataclass(frozen=True)
class WellnessRecipe:
    recipe_id: str
    title: str
    category: str  # Tra duong nhan, Canh duong sinh, Chao che
    target_constitutions: list[str]
    target_concerns: list[str]
    ingredients: list[str]
    prep_steps: list[str]
    best_time_to_use: str
    contraindications: list[str]  # Safety first: who must avoid


@dataclass(frozen=True)
class QuizDiagnosisResult:
    primary_code: str
    primary_profile: BodyConstitutionProfile
    secondary_code: str | None
    scores: dict[str, int]
    recommended_recipes: list[WellnessRecipe]
    plan_28_days_summary: list[str]


CONSTITUTION_PROFILES: dict[str, BodyConstitutionProfile] = {
    "huyet_hu": BodyConstitutionProfile(
        code="huyet_hu",
        name_vi="Huyết Hư (Thiếu hụt khí huyết nuôi dưỡng)",
        tagline="Da vàng xỉn thiếu sức sống, môi nhạt, tóc khô rụng, hay hoa mắt khó vào giấc.",
        facial_signs=["Sắc mặt vàng sạm hoặc trắng nhợt thiếu hồng hào", "Môi nhạt màu, quầng mắt thâm nhẹ", "Da khô, dễ xuất hiện nếp nhăn mảnh"],
        body_signs=["Tóc khô xơ, dễ gãy rụng", "Hay hoa mắt khi đứng lên ngồi xuống, ngủ nông", "Lượng kinh nguyệt ít, màu nhạt, dễ mệt sau kỳ kinh"],
        core_principle="Dưỡng huyết – Kiện tỳ – An thần nhẹ nhàng (Không dùng đồ đại bổ gây nóng trong).",
        foods_to_prioritize=["Táo đỏ (Hồng táo)", "Kỷ tử", "Long nhãn", "Đương quy", "Đậu đen xanh lòng", "Mè đen"],
        foods_to_avoid=["Trà đặc, cà phê lúc bụng rỗng", "Đồ ăn sống lạnh, nước đá", "Thức khuya sau 23h (giờ Can Đởm tàng huyết)"],
    ),
    "khi_hu": BodyConstitutionProfile(
        code="khi_hu",
        name_vi="Khí Hư (Năng lượng Tỳ Phế suy giảm)",
        tagline="Người nhanh hụt hơi, giọng nhỏ, da kém săn chắc, dễ đổ mồ hôi vặt.",
        facial_signs=["Gương mặt thiếu độ căng bóng, cơ mặt dễ chảy xệ", "Sắc mặt trắng bệch hoặc vàng nhạt", "Mí mắt dễ sưng nhẹ buổi sáng"],
        body_signs=["Hay mệt mỏi dù không làm việc nặng", "Ăn nhanh no, đầy bụng sau ăn", "Dễ cảm lạnh khi đổi thời tiết"],
        core_principle="Bổ khí – Kiện tỳ – Nâng đỡ cơ biểu.",
        foods_to_prioritize=["Hoàng kỳ", "Đảng sâm", "Hoài sơn (Củ mài)", "Hạt sen", "Gạo lứt, táo đỏ"],
        foods_to_avoid=["Đồ chiên rán nhiều dầu mỡ gây trệ Tỳ", "Nước ngọt có ga, đồ lạnh", "Nhịn ăn sáng"],
    ),
    "am_hu": BodyConstitutionProfile(
        code="am_hu",
        name_vi="Âm Hư (Thiếu tân dịch, nóng trong âm ỉ)",
        tagline="Hai gò má dễ ửng đỏ chiều tối, da khô thiếu nước, lòng bàn tay chân ấm nóng.",
        facial_signs=["Da khô căng từ bên trong, dễ bong tróc vùng mũi má", "Môi khô, dễ nứt nẻ, sắc mặt hơi đỏ về chiều", "Dễ nổi mụn nhỏ li ti do nhiệt độc tích tụ"],
        body_signs=["Lòng bàn tay, bàn chân ấm nóng (ngũ tâm phiền nhiệt)", "Miệng họng khô, thích uống nước mát", "Khó ngủ sâu, hay mơ, dễ bốc hỏa ở tuổi 35+"],
        core_principle="Tư âm – Nhuận táo – Thanh nhiệt dịu nhẹ.",
        foods_to_prioritize=["Mạch môn", "Ngọc trúc", "Bách hợp", "Nấm tuyết (Ngân nhĩ)", "Lê hấp, kỷ tử, hạt chia"],
        foods_to_avoid=["Đồ cay nóng (ớt, tiêu, gừng khô lượng nhiều)", "Đồ nướng, rượu bia", "Xông hơi quá lâu làm mất tân dịch"],
    ),
    "duong_hu": BodyConstitutionProfile(
        code="duong_hu",
        name_vi="Dương Hư (Thiếu hơi ấm ôn煦 cơ thể)",
        tagline="Tay chân lạnh quanh năm, sợ gió lạnh, sắc mặt trắng, dễ phù nhẹ và đau bụng kỳ kinh.",
        facial_signs=["Sắc mặt trắng sáng nhưng thiếu huyết sắc hồng", "Quầng mắt hơi sẫm, mặt dễ tích nước buổi sáng", "Môi nhạt hoặc hơi tím nhẹ khi trời lạnh"],
        body_signs=["Bàn tay bàn chân lạnh, mùa hè ngồi điều hòa dễ lạnh sống lưng", "Ăn đồ mát/sống lạnh dễ đau bụng, đi ngoài", "Đau bụng kinh âm ỉ, chườm ấm thì dễ chịu"],
        core_principle="Ôn dương – Tán hàn – Thông kinh hoạt lạc.",
        foods_to_prioritize=["Gừng già (Sinh khương/Can khương)", "Quế chi / Nhục quế", "Đường nâu nguyên chất", "Long nhãn, táo đỏ, kỷ tử"],
        foods_to_avoid=["Trà xanh đặc, khổ qua, rau má sống lượng nhiều", "Nước đá, kem lạnh, trái cây lấy trực tiếp từ tủ lạnh", "Ngâm chân nước lạnh hoặc tắm đêm"],
    ),
    "huyet_u": BodyConstitutionProfile(
        code="huyet_u",
        name_vi="Huyết Ứ (Tuần hoàn khí huyết kém lưu thông)",
        tagline="Da dễ sạm nám, quầng mắt đậm, môi thâm, đau bụng kinh kèm cục máu đông.",
        facial_signs=["Đốm nâu, nám mảng hoặc vết thâm mụn rất lâu mờ", "Môi hơi sẫm màu, quầng thâm mắt rõ", "Sắc da tối màu, kém tươi nhuận"],
        body_signs=["Đau bụng dữ dội ngày đầu kỳ kinh, máu kinh sẫm màu", "Vai gáy dễ căng cứng, tê mỏi tay chân khi ngồi lâu", "Dễ bầm tím dưới da"],
        core_principle="Hoạt huyết – Hóa ứ – Làm sáng sắc diện.",
        foods_to_prioritize=["Nụ hoa hồng (Mai khôi hoa)", "Đan sâm / Đương quy", "Sơn tra (Táo mèo)", "Nghệ vàng, đường đỏ, kỷ tử"],
        foods_to_avoid=["Đồ ăn quá lạnh làm ngưng trệ huyết mạch", "Ngồi bất động liên tục > 2 giờ không vận động", "Đồ ăn nhiều đường tinh luyện và mỡ bão hòa"],
    ),
    "dam_thap": BodyConstitutionProfile(
        code="dam_thap",
        name_vi="Đàm Thấp / Thấp Nhiệt (Tích nước, dầu mụn, nặng nề)",
        tagline="Da đổ dầu nhiều, dễ lên mụn bọc/mụn ẩn, người nặng nề, dễ tích mỡ bụng dưới.",
        facial_signs=["Vùng chữ T bóng dầu, lỗ chân lông to", "Dễ nổi mụn viêm, mụn ẩn vùng cằm và quai hàm", "Mặt và mí mắt dễ phù nhẹ, cảm giác nặng mặt"],
        body_signs=["Người nặng nề, uể oải sau bữa trưa", "Dễ tích mỡ bụng dưới dù ăn không nhiều", "Rêu lưỡi dày, miệng hơi dính hoặc đắng nhẹ"],
        core_principle="Kiện tỳ – Trừ thấp – Thanh lọc dầu thừa.",
        foods_to_prioritize=["Ý dĩ (Bo bo)", "Đậu đỏ nhỏ hạt (Xích tiểu đậu)", "Vỏ quýt lâu năm (Trần bì)", "Phục linh, trà lá sen, bí đao"],
        foods_to_avoid=["Trà sữa, bánh ngọt, phô mai, đồ nếp", "Các bài thuốc đại bổ nhiều đường/mật ong đặc", "Ăn tối quá muộn sau 20h30"],
    ),
    "khi_uat": BodyConstitutionProfile(
        code="khi_uat",
        name_vi="Khí Uất (Căng thẳng làm Can khí uất kết)",
        tagline="Hay thở dài, căng tức ngực sườn trước kỳ kinh, nám hai bên gò má, khó ngủ do suy nghĩ.",
        facial_signs=["Sắc mặt lúc sáng lúc xỉn theo tâm trạng và giấc ngủ", "Dễ xuất hiện nám cánh bướm hai bên gò má", "Nếp nhăn vùng ấn đường (giữa hai chân mày)"],
        body_signs=["Hay thở dài vô thức, cảm giác nghẹn nhẹ ở cổ họng", "Căng tức ngực và dễ cáu gắt 5–7 ngày trước kỳ kinh", "Đầu óc khó tắt suy nghĩ khi nằm xuống giường"],
        core_principle="Sơ can – Giải uất – Điều hòa khí huyết.",
        foods_to_prioritize=["Nụ hoa hồng", "Hoa cúc chi", "Trần bì (Vỏ quýt)", "Hoa nhài, kỷ tử, táo đỏ"],
        foods_to_avoid=["Cà phê đậm khi đang căng thẳng", "Bỏ bữa hoặc ăn uống thất thường khi làm việc", "Kìm nén cảm xúc và thức khuya xem màn hình"],
    ),
}


SAMPLE_RECIPES: list[WellnessRecipe] = [
    WellnessRecipe(
        recipe_id="REC-001",
        title="Trà Tam Bảo Hồng Nhuận (Táo Đỏ – Kỷ Tử – Long Nhãn)",
        category="Trà dưỡng nhan",
        target_constitutions=["huyet_hu", "khi_hu", "duong_hu"],
        target_concerns=["Da xỉn, sắc mặt vàng sạm", "Tóc rụng, tóc khô", "Ngủ ngon, bớt căng thẳng"],
        ingredients=["Táo đỏ Tân Cương: 3 quả (cắt lát bỏ hạt)", "Kỷ tử ninh hạ: 10 hạt", "Long nhãn nhục: 4–5 múi", "Nước sôi 90°C: 350ml"],
        prep_steps=[
            "Tráng nhanh táo đỏ và long nhãn bằng nước ấm 5 giây để sạch bụi.",
            "Cho táo đỏ và long nhãn vào bình giữ nhiệt, rót 350ml nước sôi 90°C ủ 10 phút.",
            "Thêm kỷ tử vào sau cùng, chờ 3 phút để giữ trọn hoạt chất rồi thưởng thức khi còn ấm.",
        ],
        best_time_to_use="Buổi sáng sau ăn sáng 30 phút hoặc buổi chiều 14h–16h.",
        contraindications=["Người đang sốt cao, viêm họng cấp", "Người thể Đàm thấp nặng đang nổi mụn mủ sưng viêm hoặc tiểu đường chưa kiểm soát"],
    ),
    WellnessRecipe(
        recipe_id="REC-002",
        title="Trà Mai Khôi Trần Bì Sơ Can (Hoa Hồng – Vỏ Quýt – Kỷ Tử)",
        category="Trà dưỡng nhan",
        target_constitutions=["khi_uat", "huyet_u"],
        target_concerns=["Nám, tàn nhang, sắc tố", "Kinh nguyệt và nhan sắc", "Ngủ ngon, bớt căng thẳng"],
        ingredients=["Nụ hoa hồng khô (Mai khôi): 5–6 nụ", "Trần bì (vỏ quýt lâu năm): 3g", "Kỷ tử: 8 hạt", "Nước ấm 85°C: 300ml"],
        prep_steps=[
            "Cho trần bì vào tách, rót nước sôi ủ trước 5 phút cho ra tinh dầu thơm.",
            "Thả nụ hoa hồng và kỷ tử vào, đậy nắp ủ thêm 5 phút.",
            "Uống ấm từng ngụm nhỏ, kết hợp hít thở sâu hương hoa hồng để thư giãn Can khí.",
        ],
        best_time_to_use="Chiều 15h–17h hoặc 5 ngày trước kỳ kinh nguyệt.",
        contraindications=["Phụ nữ đang mang thai 3 tháng đầu", "Người đang rong kinh hoặc lượng kinh quá nhiều"],
    ),
    WellnessRecipe(
        recipe_id="REC-003",
        title="Nước Ý Dĩ Xích Tiểu Đậu Thanh Lọc (Đậu Đỏ Nhỏ – Ý Dĩ – Trần Bì)",
        category="Trà & Nước dưỡng sinh",
        target_constitutions=["dam_thap"],
        target_concerns=["Mụn, da dầu", "Thon dáng, tiêu mỡ bụng, giảm phù"],
        ingredients=["Ý dĩ (rang vàng nhẹ để khử tính hàn): 20g", "Đậu đỏ hạt nhỏ (Xích tiểu đậu): 20g", "Trần bì: 2g", "Nước lọc: 800ml"],
        prep_steps=[
            "Sao vàng nhẹ hạt ý dĩ trên chảo khô 5 phút cho dậy mùi thơm (bước quan trọng để không làm lạnh bụng).",
            "Ninh ý dĩ, đậu đỏ nhỏ và trần bì với 800ml nước trong 25 phút (hoặc ủ bình giữ nhiệt 2 tiếng).",
            "Chắt lấy nước uống thay nước lọc trong ngày; phần hạt có thể ăn kèm bữa phụ.",
        ],
        best_time_to_use="Uống trong khung giờ 9h–16h (giờ Tỳ Vị và Bàng Quang vận hóa nước).",
        contraindications=["Phụ nữ mang thai (do Ý dĩ)", "Người thể Âm hư khô táo nặng hoặc đang táo bón"],
    ),
    WellnessRecipe(
        recipe_id="REC-004",
        title="Chè Ngân Nhĩ Bách Hợp Tuyết Lê (Dưỡng Âm Cấp Ẩm Sâu)",
        category="Cháo chè dưỡng nhan",
        target_constitutions=["am_hu"],
        target_concerns=["Da khô, nếp nhăn, lão hóa sớm", "Ngủ ngon, bớt căng thẳng", "Tuổi 40+ và tiền mãn kinh"],
        ingredients=["Nấm tuyết khô (Ngân nhĩ): 1/4 bông", "Bách hợp khô: 8g", "Lê tươi: 1/2 quả (cắt hạt lựu)", "Kỷ tử: 10 hạt, Đường phèn: 5g"],
        prep_steps=[
            "Ngâm nấm tuyết và bách hợp trong nước mát 30 phút cho nở mềm, xé nhỏ nấm tuyết.",
            "Hầm nấm tuyết và bách hợp với 500ml nước lửa nhỏ trong 30 phút cho ra胶 (collagen thực vật tự nhiên).",
            "Cho lê cắt hạt lựu, kỷ tử và chút đường phèn vào đun thêm 7 phút rồi tắt bếp.",
        ],
        best_time_to_use="Bữa phụ chiều 16h hoặc buổi tối trước khi ngủ 2 tiếng.",
        contraindications=["Người thể Dương hư đang lạnh bụng, đi ngoài phân lỏng", "Người đang ho nhiều đờm trắng loãng"],
    ),
]


def diagnose_constitution(selected_codes: list[str]) -> QuizDiagnosisResult:
    """Score user quiz selections deterministically and return personalized diagnosis + recipes."""
    scores: dict[str, int] = {code: 0 for code in CONSTITUTION_PROFILES}
    for code in selected_codes:
        clean = code.strip().lower()
        if clean in scores:
            scores[clean] += 1

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    primary_code = ranked[0][0] if ranked[0][1] > 0 else "huyet_hu"
    secondary_code = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0 else None

    primary_profile = CONSTITUTION_PROFILES[primary_code]

    matched_recipes: list[WellnessRecipe] = []
    for rec in SAMPLE_RECIPES:
        if primary_code in rec.target_constitutions or (
            secondary_code and secondary_code in rec.target_constitutions
        ):
            matched_recipes.append(rec)
    if not matched_recipes:
        matched_recipes.append(SAMPLE_RECIPES[0])

    plan_28_days = [
        f"Tuần 1 (Khơi thông): Ngưng nước đá sau 18h, ngủ trước 23h, dùng 3 buổi/tuần bài '{matched_recipes[0].title}'.",
        f"Tuần 2 (Bồi bổ gốc '{primary_profile.name_vi}'): Ưu tiên nhóm thực phẩm {', '.join(primary_profile.foods_to_prioritize[:3])}.",
        "Tuần 3 (Điều khí & Sáng da): Kết hợp 10 phút ngâm chân ấm hoặc massage vùng mắt – ấn đường trước khi ngủ.",
        "Tuần 4 (Cố định nếp dưỡng): Đánh giá lại sắc môi, giấc ngủ và độ ẩm da; giảm dần tần suất về mức duy trì 2–3 lần/tuần.",
    ]

    return QuizDiagnosisResult(
        primary_code=primary_code,
        primary_profile=primary_profile,
        secondary_code=secondary_code,
        scores=scores,
        recommended_recipes=matched_recipes,
        plan_28_days_summary=plan_28_days,
    )


def build_vietqr_checkout_url(
    bank_id: str,
    account_no: str,
    account_name: str,
    amount_vnd: int = 299_000,
    order_code: str = "DN001",
    affiliate_ref: str = "",
) -> str:
    """Build a deterministic VietQR quicklink URL with order & affiliate tracking memo."""
    if amount_vnd <= 0:
        raise ValueError("amount_vnd must be positive.")
    memo = f"DUONGNHAN {order_code.strip().upper()}"
    if affiliate_ref.strip():
        memo += f" REF {affiliate_ref.strip().upper()}"
    encoded_memo = quote(memo)
    encoded_name = quote(account_name.strip())
    return (
        f"https://img.vietqr.io/image/{bank_id.strip()}-{account_no.strip()}-compact2.png"
        f"?amount={int(amount_vnd)}&addInfo={encoded_memo}&accountName={encoded_name}"
    )
