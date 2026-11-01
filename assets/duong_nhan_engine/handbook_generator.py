"""Deterministic generator for the complete Digital Asset:
Cam Nang & Tro Ly Duong Nhan 7 The Chat Dong Y (Full Interactive Reader + Printable PDF + Audio Companion).
Zero LLM runtime cost, zero marginal cost per sale, automated fulfillment ready.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .constitution_engine import CONSTITUTION_PROFILES


EXTENDED_RECIPES: List[Dict[str, str]] = [
    # Khi Hu (Qi Deficiency)
    {
        "code": "KH-01",
        "title": "Trà Hoàng Kỳ Táo Đỏ Kỷ Tử (Bổ Khí Nâng Cơ)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "khi_hu",
        "constitution_name": "Khí Hư",
        "ingredients": "Hoàng kỳ 8g, Táo đỏ Tân Cương 4 quả (bỏ hạt), Kỷ tử 6g, Gừng tươi 1 lát mỏng, 400ml nước sôi.",
        "steps": "Tráng nhanh dược liệu bằng nước ấm. Hãm trong bình giữ nhiệt 20 phút, uống ấm vào buổi sáng sau ăn 30 phút.",
        "benefit": "Bổ trung ích khí, giảm mệt mỏi hụt hơi, cải thiện sắc mặt nhợt nhạt và chảy xệ cơ mặt.",
        "avoid": "Không uống khi đang sốt cao, viêm họng cấp hoặc huyết áp đang tăng cao.",
    },
    {
        "code": "KH-02",
        "title": "Cháo Sơn Dược Hạt Sen Long Nhãn (Kiện Tỳ Dưỡng Khí)",
        "category": "Cháo Dưỡng Sinh",
        "constitution": "khi_hu",
        "constitution_name": "Khí Hư",
        "ingredients": "Hoài sơn (Sơn dược) khô 15g, Hạt sen 15g, Long nhãn 8g, Gạo tẻ 40g.",
        "steps": "Ngâm hoài sơn và hạt sen 30 phút. Ninh cùng gạo tẻ 45 phút đến khi nhừ, thêm long nhãn 5 phút cuối.",
        "benefit": "Kiện tỳ ích vị, giúp hấp thu dinh dưỡng tốt, giảm chướng bụng sau ăn, da dẻ hồng hào săn chắc.",
        "avoid": "Người tiểu đường hoặc đang táo bón nhiệt cần giảm lượng long nhãn.",
    },
    {
        "code": "KH-03",
        "title": "Canh Gà Ác Hầm Đảng Sâm Kỷ Tử",
        "category": "Canh Thực Dưỡng",
        "constitution": "khi_hu",
        "constitution_name": "Khí Hư",
        "ingredients": "Nửa con gà ác (hoặc 150g ức gà ta), Đảng sâm 10g, Kỷ tử 8g, Táo đỏ 4 quả, 2 lát gừng.",
        "steps": "Chần sơ gà với gừng, sau đó tiềm cách thủy cùng đảng sâm, táo đỏ 60 phút, rắc kỷ tử trước khi tắt bếp.",
        "benefit": "Đại bổ nguyên khí, phục hồi thể lực sau ốm hoặc sau kỳ kinh nguyệt, chống lão hóa sớm.",
        "avoid": "Không dùng khi đang cảm cúm phong nhiệt hoặc đầy bụng khó tiêu cấp.",
    },
    {
        "code": "KH-04",
        "title": "Sữa Hạt Kê Đậu Đỏ Táo Đỏ Ấm",
        "category": "Ngũ Cốc & Sữa Hạt",
        "constitution": "khi_hu",
        "constitution_name": "Khí Hư",
        "ingredients": "Hạt kê vàng 25g, Đậu đỏ 20g, Táo đỏ bỏ hạt 4 quả, 500ml nước lọc.",
        "steps": "Ngâm đậu đỏ 4 tiếng, nấu bằng máy làm sữa hạt chế độ sữa thảo mộc 25 phút, uống ấm buổi sáng.",
        "benefit": "Bổ khí kiện tỳ, êm dạ dày, thay thế trà sữa lạnh gây hại tỳ vị.",
        "avoid": "Tránh thêm đường tinh luyện; người đầy hơi nặng chỉ uống 150ml/lần.",
    },
    # Huyet Hu (Blood Deficiency)
    {
        "code": "HH-01",
        "title": "Chè Ngũ Hồng Bổ Huyết Nhuận Sắc (5 Vị Đỏ)",
        "category": "Chè Cổ Truyền",
        "constitution": "huyet_hu",
        "constitution_name": "Huyết Hư",
        "ingredients": "Đậu đỏ 25g, Lạc đỏ (đậu phộng vỏ đỏ) 15g, Táo đỏ 5 quả, Kỷ tử 8g, Đường đỏ nguyên chất 8g.",
        "steps": "Ngâm đậu đỏ 2 giờ. Ninh đậu đỏ, lạc đỏ và táo đỏ 40 phút cho mềm, thêm kỷ tử và đường đỏ đun thêm 5 phút.",
        "benefit": "Dưỡng huyết điều kinh, làm hồng môi và má, giảm rụng tóc và khô da sau kỳ kinh.",
        "avoid": "Người đang có đờm thấp nặng, mụn bọc sưng đỏ hoặc đường huyết cao không thêm đường đỏ.",
    },
    {
        "code": "HH-02",
        "title": "Trà Long Nhãn Kỷ Tử Hoa Hồng Đỏ",
        "category": "Trà Dưỡng Nhan",
        "constitution": "huyet_hu",
        "constitution_name": "Huyết Hư",
        "ingredients": "Long nhãn 8g, Kỷ tử 8g, Nụ hoa hồng đỏ sấy lạnh 4 nụ, Táo đỏ thái lát 3 quả.",
        "steps": "Hãm với 350ml nước sôi 90°C trong 10-15 phút. Uống ấm buổi chiều giúp an thần dưỡng huyết.",
        "benefit": "Bổ tâm tỳ huyết, cải thiện mất ngủ hay quên, giảm quầng thâm mắt do thiếu máu.",
        "avoid": "Phụ nữ mang thai và người đang nhiệt miệng, chảy máu cam không dùng.",
    },
    {
        "code": "HH-03",
        "title": "Cháo Đương Quy Trứng Gà Táo Đỏ",
        "category": "Cháo Dưỡng Sinh",
        "constitution": "huyet_hu",
        "constitution_name": "Huyết Hư",
        "ingredients": "Đương quy lát 4g, Táo đỏ 5 quả, Kỷ tử 6g, Trứng gà ta 1 quả, Gạo tẻ 40g.",
        "steps": "Sắc đương quy lấy nước nấu cháo cùng táo đỏ, khi cháo chín đập trứng gà khuấy đều và thêm kỷ tử.",
        "benefit": "Hoạt huyết bổ huyết kinh điển, giảm đau đầu chóng mặt và da khô bong tróc mùa hanh.",
        "avoid": "Không dùng trong những ngày kinh nguyệt đang ra nhiều hoặc người tiêu chảy phân lỏng.",
    },
    {
        "code": "HH-04",
        "title": "Sữa Đen Tam Hắc (Đậu Đen - Mè Đen - Dâu Tằm)",
        "category": "Ngũ Cốc & Sữa Hạt",
        "constitution": "huyet_hu",
        "constitution_name": "Huyết Hư",
        "ingredients": "Đậu đen xanh lòng rang thơm 20g, Mè đen rang 10g, Dâu tằm khô (Tang thầm) 8g, Gạo lứt đen 15g.",
        "steps": "Xay nấu bằng máy sữa hạt 25 phút với 500ml nước, uống ấm vào buổi sáng hoặc xế chiều.",
        "benefit": "Bổ can thận tinh huyết, dưỡng tóc đen bóng, giảm gãy rụng và khô móng tay.",
        "avoid": "Người tỳ vị quá yếu hay đi ngoài phân lỏng chỉ uống lượng nhỏ ấm.",
    },
    # Duong Hu (Yang Deficiency)
    {
        "code": "DH-01",
        "title": "Trà Gừng Táo Đỏ Quế Chi Đường Đỏ (Ôn Dương Tán Hàn)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "duong_hu",
        "constitution_name": "Dương Hư",
        "ingredients": "Gừng già thái sợi 5g, Táo đỏ 4 quả, Quế thanh nhỏ 1g, Đường đỏ 6g.",
        "steps": "Đun sôi nhỏ lửa gừng, táo đỏ và quế trong 10 phút, hòa đường đỏ. Uống trước 11h trưa.",
        "benefit": "Làm ấm tử cung và tứ chi, giảm đau bụng kinh do lạnh, tiêu phù nề mặt buổi sáng.",
        "avoid": "Tuyệt đối không uống sau 17h chiều; người âm hư bốc hỏa, nhiệt miệng không dùng.",
    },
    {
        "code": "DH-02",
        "title": "Canh Sườn Non Củ Sen Hạt Dẻ Óc Chó",
        "category": "Canh Thực Dưỡng",
        "constitution": "duong_hu",
        "constitution_name": "Dương Hư",
        "ingredients": "Sườn non 150g, Củ sen 100g, Hạt dẻ tươi 6 hạt, Nhân óc chó 3 quả, Gừng 3 lát.",
        "steps": "Hầm sườn non với gừng 25 phút, cho củ sen, hạt dẻ và óc chó vào ninh thêm 25 phút, nêm nhạt.",
        "benefit": "Ôn bổ thận dương, mạnh lưng gối, giảm tiểu đêm và lạnh bàn chân mùa mưa lạnh.",
        "avoid": "Người đang sốt, táo bón nhiệt hoặc mỡ máu cao cần hớt sạch váng mỡ.",
    },
    {
        "code": "DH-03",
        "title": "Cháo Gạo Nếp Cẩm Long Nhãn Gừng Tươi",
        "category": "Cháo Dưỡng Sinh",
        "constitution": "duong_hu",
        "constitution_name": "Dương Hư",
        "ingredients": "Gạo nếp cẩm 35g, Long nhãn 8g, Táo đỏ 4 quả, Gừng tươi 3 lát.",
        "steps": "Ngâm nếp cẩm 3 giờ, ninh nhừ với gừng và táo đỏ, thêm long nhãn 5 phút trước khi tắt bếp.",
        "benefit": "Ấm bụng kiện tỳ, cải thiện tuần hoàn ngoại vi giúp gò má hồng tự nhiên.",
        "avoid": "Người đang viêm dạ dày cấp hoặc trào ngược axit nặng ăn lượng nhỏ.",
    },
    # Am Hu (Yin Deficiency)
    {
        "code": "AH-01",
        "title": "Chè Tuyết Nhĩ Hạt Sen Bách Hợp (Tư Âm Cấp Ẩm Sâu)",
        "category": "Chè Cổ Truyền",
        "constitution": "am_hu",
        "constitution_name": "Âm Hư",
        "ingredients": "Nấm tuyết (Tuyết nhĩ) khô 8g, Bách hợp khô 10g, Hạt sen 15g, Kỷ tử 6g, Lê tươi 1/2 quả, Đường phèn 6g.",
        "steps": "Ngâm nở nấm tuyết, cắt nhỏ. Ninh cùng hạt sen, bách hợp 35 phút cho sánh collagen thực vật, thêm lê và kỷ tử đun 10 phút.",
        "benefit": "Tư âm nhuận phế, cấp ẩm nội sinh cho làn da khô căng, giảm bốc hỏa gò má và mất ngủ.",
        "avoid": "Người dương hư sợ lạnh, đang cảm lạnh ho đờm loãng trắng hoặc tiêu chảy không dùng.",
    },
    {
        "code": "AH-02",
        "title": "Trà Mạch Môn Ngọc Trúc Kỷ Tử (Dưỡng Âm Sinh Tân)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "am_hu",
        "constitution_name": "Âm Hư",
        "ingredients": "Mạch môn 6g, Ngọc trúc 6g, Kỷ tử 6g, Hoa cúc vàng 4 bông.",
        "steps": "Hãm với 400ml nước sôi trong 15 phút. Uống ấm rải rác trong ngày.",
        "benefit": "Làm dịu họng khô khát nước, giảm nóng trong người, làm sáng da và mờ nếp nhăn li ti do thiếu nước.",
        "avoid": "Người tỳ vị hư hàn, đầy bụng lạnh bụng tránh dùng.",
    },
    {
        "code": "AH-03",
        "title": "Canh Sườn Hầm Củ Mài Ngọc Trúc Kỷ Tử",
        "category": "Canh Thực Dưỡng",
        "constitution": "am_hu",
        "constitution_name": "Âm Hư",
        "ingredients": "Sườn thăn 150g, Củ mài (Hoài sơn tươi) 120g, Ngọc trúc 8g, Kỷ tử 6g.",
        "steps": "Hầm sườn và ngọc trúc 30 phút, thêm củ mài cắt khúc đun 15 phút, cho kỷ tử vào cuối cùng.",
        "benefit": "Bổ phế tỳ thận âm mà không gây béo trệ, phục hồi độ đàn hồi da sau thức khuya.",
        "avoid": "Không cho các gia vị cay nóng như ớt, tiêu nhiều.",
    },
    # Dam Thap (Phlegm-Dampness)
    {
        "code": "DT-01",
        "title": "Nước Đậu Đỏ Ý Dĩ Sao Trần Bì (Trừ Thấp Tiêu Phù)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "dam_thap",
        "constitution_name": "Đàm Thấp",
        "ingredients": "Xích tiểu đậu (đậu đỏ hạt nhỏ dài) 20g, Ý dĩ đã sao vàng 20g, Trần bì (vỏ quýt lâu năm) 3g, Phục linh 8g.",
        "steps": "Đun sôi nhỏ lửa với 800ml nước trong 30 phút, chắt lấy nước uống ấm thay trà trong ngày (không cần ăn xác nếu đầy bụng).",
        "benefit": "Kiện tỳ thẩm thấp, giảm tích nước mặt và bắp chân, giảm dầu nhờn vùng chữ T và mụn ẩn.",
        "avoid": "Tuyệt đối không dùng cho phụ nữ mang thai (do có Ý dĩ) và người âm hư津 khô táo bón.",
    },
    {
        "code": "DT-02",
        "title": "Trà Lá Sen Sơn Tra Trần Bì (Thanh Nhẹ Giảm Mỡ Nội Tạng)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "dam_thap",
        "constitution_name": "Đàm Thấp",
        "ingredients": "Lá sen khô (Hà diệp) 5g, Sơn tra khô 5g, Trần bì 3g.",
        "steps": "Hãm với 400ml nước sôi 15 phút, uống sau bữa trưa nhiều dầu mỡ 30 phút.",
        "benefit": "Tiêu thực hóa đàm, giảm cảm giác nặng đầu buồn ngủ sau ăn trưa, hỗ trợ vòng eo thon gọn.",
        "avoid": "Không uống lúc đói cồn cào hoặc người đau dạ dày dư axit nặng.",
    },
    {
        "code": "DT-03",
        "title": "Canh Bí Đao Ý Dĩ Nấm Hương",
        "category": "Canh Thực Dưỡng",
        "constitution": "dam_thap",
        "constitution_name": "Đàm Thấp",
        "ingredients": "Bí đao xanh (cả vỏ rửa sạch) 200g, Ý dĩ sao 15g, Nấm hương 4 tai, Gừng 2 lát.",
        "steps": "Ninh ý dĩ và nấm hương 25 phút, cho bí đao và gừng vào nấu thêm 10 phút, nêm thanh đạm.",
        "benefit": "Lợi thủy tiêu thũng, thanh lọc da dầu và giảm sưng mặt buổi sáng.",
        "avoid": "Phụ nữ mang thai bỏ ý dĩ; người huyết áp thấp nặng không ăn quá nhiều bí đao.",
    },
    # Thap Nhiet (Damp-Heat)
    {
        "code": "TN-01",
        "title": "Trà Hoa Cúc Kim Ngân Bồ Công Anh (Thanh Nhiệt Giảm Mụn Viêm)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "thap_nhiet",
        "constitution_name": "Thấp Nhiệt",
        "ingredients": "Hoa cúc chi 5g, Kim ngân hoa 4g, Bồ công anh khô 4g, Cam thảo 2 lát.",
        "steps": "Hãm với 400ml nước sôi 10 phút. Chỉ uống liên tục 5-7 ngày trong đợt bùng mụn đỏ hoặc nóng nhiệt, sau đó nghỉ.",
        "benefit": "Thanh nhiệt giải độc, làm dịu mụn sưng viêm, giảm miệng đắng và mùi cơ thể.",
        "avoid": "Không uống dài ngày quá 2 tuần liên tục vì tính hàn dễ làm yếu tỳ vị; người bụng lạnh đi lỏng không dùng.",
    },
    {
        "code": "TN-02",
        "title": "Chè Đậu Xanh Nha Đam Củ Mã Thầy (Thanh Thấp Hạ Hỏa)",
        "category": "Chè Cổ Truyền",
        "constitution": "thap_nhiet",
        "constitution_name": "Thấp Nhiệt",
        "ingredients": "Đậu xanh nguyên vỏ 30g, Củ mã thầy (năng) 4 củ cắt hạt lựu, Nha đam sơ chế sạch nhớt 30g, Đường phèn 5g.",
        "steps": "Đun đậu xanh và mã thầy 25 phút vừa chín tới (nước còn trong xanh), thêm nha đam và đường phèn đun sôi lại 2 phút.",
        "benefit": "Giải nhiệt độc mùa hè, giảm dầu bóng nhờn và mẩn đỏ trên da.",
        "avoid": "Người dương hư lạnh bụng, phụ nữ đang hành kinh không dùng.",
    },
    # Khi Uat / Huyet U (Qi Stagnation & Blood Stasis)
    {
        "code": "KU-01",
        "title": "Trà Tam Hoa Giải Uất (Hoa Hồng - Hoa Nhài - Phật Thủ)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "khi_uat_huyet_u",
        "constitution_name": "Khí Uất / Huyết Ứ",
        "ingredients": "Nụ hoa hồng 5 nụ, Hoa nhài khô 3g, Phật thủ khô (hoặc Trần bì) 3g, Sơn tra 3 lát.",
        "steps": "Hãm với 350ml nước 85-90°C trong 10 phút. Thưởng trà chậm rãi vào buổi chiều khi căng thẳng công việc.",
        "benefit": "Sơ can giải uất, hành khí hoạt huyết, giảm tức ngực thở dài, làm mờ vết nám sạm do stress và đau tức ngực trước kỳ kinh.",
        "avoid": "Phụ nữ mang thai và người rong kinh lượng nhiều không dùng.",
    },
    {
        "code": "KU-02",
        "title": "Trà Sơn Tra Đan Sâm Hoa Hồng (Hoạt Huyết Sáng Nám)",
        "category": "Trà Dưỡng Nhan",
        "constitution": "khi_uat_huyet_u",
        "constitution_name": "Khí Uất / Huyết Ứ",
        "ingredients": "Sơn tra khô 6g, Hoa hồng đỏ 5 nụ, Táo đỏ 3 quả, Đường đỏ 4g (uống 5 ngày trước kỳ kinh).",
        "steps": "Đun sôi nhẹ 10 phút hoặc hãm bình giữ nhiệt 15 phút, uống ấm.",
        "benefit": "Hóa ứ thông kinh, giảm máu cục sẫm màu và đau bụng kinh, cải thiện sắc da xỉn màu đốm nâu.",
        "avoid": "Ngưng uống ngay khi kinh nguyệt đã ra nhiều; phụ nữ có thai tuyệt đối không dùng.",
    },
    {
        "code": "KU-03",
        "title": "Canh Cá Chép Đậu Phụ Nấm Đông Cô Trần Bì",
        "category": "Canh Thực Dưỡng",
        "constitution": "khi_uat_huyet_u",
        "constitution_name": "Khí Uất / Huyết Ứ",
        "ingredients": "Đậu phụ non 150g, Nấm đông cô 5 tai, Trần bì 3g, Hành hoa, Gừng 3 lát.",
        "steps": "Nấu nước dùng nấm đông cô, trần bì và gừng 15 phút, thêm đậu phụ non đun 5 phút, rắc hành hoa.",
        "benefit": "Lý khí khoan trung, nhẹ bụng, hỗ trợ giấc ngủ sâu cho người hay suy nghĩ căng thẳng.",
        "avoid": "Dùng ấm vào bữa tối, tránh ăn quá muộn sau 20h.",
    },
]


def render_handbook_html() -> str:
    """Render the complete self-fulfilling Digital Handbook + Printable Guide + Audio Companion."""
    constitution_cards = []
    for code, c in CONSTITUTION_PROFILES.items():
        AvoidList = "".join(f"<li>{item}</li>" for item in c.foods_to_avoid)
        RecList = "".join(f"<li>{item}</li>" for item in c.foods_to_prioritize)
        SymList = "".join(f"<li>{item}</li>" for item in (c.facial_signs + c.body_signs))
        constitution_cards.append(
            f"""
            <article class="const-card" id="const-{c.code}">
              <div class="const-header">
                <span class="const-badge">{c.code.upper()}</span>
                <h3>{c.name_vi}</h3>
              </div>
              <p class="const-summary"><strong>Cơ chế cốt lõi:</strong> {c.tagline}</p>
              <div class="const-grid">
                <div>
                  <h4>Dấu hiệu nhận diện</h4>
                  <ul>{SymList}</ul>
                </div>
                <div>
                  <h4>Nguyên tắc & Dược thiện khuyên dùng</h4>
                  <p><em>{c.core_principle}</em></p>
                  <ul>{RecList}</ul>
                </div>
                <div class="avoid-col">
                  <h4>⚠️ Cấm kỵ / Cần tránh</h4>
                  <ul>{AvoidList}</ul>
                </div>
              </div>
            </article>
            """
        )

    recipe_cards = []
    for r in EXTENDED_RECIPES:
        audio_text = (
            f"Công thức {r['title']}, dành cho thể chất {r['constitution_name']}. "
            f"Nguyên liệu gồm: {r['ingredients']} "
            f"Cách chế biến: {r['steps']} "
            f"Công dụng: {r['benefit']} "
            f"Lưu ý chống chỉ định: {r['avoid']}"
        ).replace('"', "&quot;")
        recipe_cards.append(
            f"""
            <div class="recipe-item" data-constitution="{r['constitution']}" data-category="{r['category']}">
              <div class="recipe-top">
                <span class="tag-const">{r['constitution_name']}</span>
                <span class="tag-cat">{r['category']}</span>
                <span class="tag-code">#{r['code']}</span>
              </div>
              <h4>{r['title']}</h4>
              <p><strong>Nguyên liệu định lượng:</strong> {r['ingredients']}</p>
              <p><strong>Cách chế biến:</strong> {r['steps']}</p>
              <p class="benefit-line"><strong>Công dụng dưỡng nhan:</strong> {r['benefit']}</p>
              <div class="contra-alert"><strong>⚠️ Chống chỉ định:</strong> {r['avoid']}</div>
              <button class="audio-btn" onclick="speakRecipe(this)" data-speech="{audio_text}">🔊 Nghe hướng dẫn Audio (Miễn phí)</button>
            </div>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cẩm Nang & Trợ Lý Dưỡng Nhan 7 Thể Chất Đông Y (Bản Đầy Đủ + Audio + In PDF)</title>
<style>
  :root {{
    --bg: #fdfaf6;
    --card: #ffffff;
    --ink: #2b1e1c;
    --muted: #6e5a56;
    --primary: #8c2d4b;
    --primary-dark: #681d35;
    --accent: #c88a4b;
    --border: #eadcd1;
    --ok: #1f6f50;
    --warn: #b45309;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.6;
  }}
  .container {{ max-width: 1080px; margin: 0 auto; padding: 0 20px; }}
  header.topbar {{
    background: #fff;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 50;
    padding: 12px 0;
  }}
  .topbar-inner {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }}
  .brand {{ font-weight: 800; color: var(--primary); font-size: 1.05rem; text-decoration: none; }}
  .btn {{
    display: inline-block;
    background: var(--primary);
    color: #fff;
    border: none;
    padding: 9px 16px;
    border-radius: 8px;
    font-weight: 700;
    cursor: pointer;
    text-decoration: none;
    font-size: 0.9rem;
  }}
  .btn:hover {{ background: var(--primary-dark); }}
  .btn-outline {{
    background: #fff;
    color: var(--primary);
    border: 1.5px solid var(--primary);
  }}
  .btn-outline:hover {{ background: #fdf2f4; }}
  .hero {{
    background: linear-gradient(135deg, #f9efe6 0%, #f3dfce 100%);
    padding: 36px 28px;
    border-radius: 18px;
    margin: 24px 0;
    border: 1px solid var(--border);
  }}
  .hero h1 {{ margin: 0 0 10px; font-size: 1.85rem; color: #3a1a24; }}
  .section-box {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 26px;
    margin-bottom: 26px;
  }}
  .const-card {{
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 16px;
    background: #fffdfb;
  }}
  .const-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
  .const-badge {{
    background: var(--primary);
    color: #fff;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
  }}
  .const-header h3 {{ margin: 0; font-size: 1.15rem; }}
  .const-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 14px;
    margin-top: 10px;
  }}
  .const-grid h4 {{ margin: 0 0 6px; font-size: 0.92rem; color: var(--primary); }}
  .const-grid ul {{ margin: 0; padding-left: 18px; font-size: 0.9rem; }}
  .avoid-col {{ background: #fff5f5; padding: 10px 12px; border-radius: 10px; border: 1px solid #fecaca; }}
  .filter-bar {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }}
  .filter-bar select, .filter-bar input {{
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 10px;
    font-size: 0.95rem;
    flex: 1;
    min-width: 200px;
  }}
  .recipe-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
    gap: 16px;
  }}
  .recipe-item {{
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    background: #fff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .recipe-top {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }}
  .tag-const {{ background: #f4e6eb; color: var(--primary); padding: 2px 9px; border-radius: 999px; font-size: 0.76rem; font-weight: 700; }}
  .tag-cat {{ background: #fef3c7; color: #92400e; padding: 2px 9px; border-radius: 999px; font-size: 0.76rem; font-weight: 700; }}
  .tag-code {{ color: var(--muted); font-size: 0.76rem; margin-left: auto; }}
  .recipe-item h4 {{ margin: 4px 0 10px; font-size: 1.08rem; color: #3a1a24; }}
  .recipe-item p {{ margin: 5px 0; font-size: 0.9rem; }}
  .benefit-line {{ color: var(--ok); }}
  .contra-alert {{
    margin-top: 8px;
    background: #fffbeb;
    border-left: 3px solid var(--warn);
    padding: 8px 10px;
    font-size: 0.84rem;
    color: #92400e;
    border-radius: 4px;
  }}
  .audio-btn {{
    margin-top: 12px;
    background: #f8efe6;
    color: var(--primary-dark);
    border: 1px solid var(--border);
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.85rem;
  }}
  .audio-btn:hover {{ background: #efe0d1; }}
  table.tracker {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 0.9rem; }}
  table.tracker th, table.tracker td {{ border: 1px solid var(--border); padding: 10px; text-align: left; }}
  table.tracker th {{ background: #f6efe8; color: #3a1a24; }}
  footer.page-footer {{
    background: #2b181e;
    color: #f3dce3;
    padding: 40px 0 30px;
    margin-top: 40px;
    font-size: 0.88rem;
  }}
  .footer-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 24px;
    margin-bottom: 24px;
  }}
  .footer-col h4 {{ color: #fff; margin: 0 0 10px; font-size: 1rem; }}
  .footer-col ul {{ list-style: none; padding: 0; margin: 0; }}
  .footer-col li {{ margin-bottom: 6px; }}
  .footer-col a {{ color: #ffd6e3; text-decoration: none; }}
  .footer-bottom {{
    border-top: 1px solid rgba(255,255,255,0.12);
    padding-top: 20px;
    text-align: center;
    color: #c4a9b2;
    font-size: 0.82rem;
  }}
  @media print {{
    header.topbar, .filter-bar, .audio-btn, footer.page-footer, .no-print {{ display: none !important; }}
    body {{ background: #fff; }}
    .section-box, .const-card, .recipe-item {{ break-inside: avoid; box-shadow: none; }}
  }}
</style>
</head>
<body>

<header class="topbar">
  <div class="container topbar-inner">
    <a href="index.html" class="brand">⬅ Quay lại Trang Trắc Nghiệm Dưỡng Nhan</a>
    <div style="display:flex; gap:10px; flex-wrap:wrap;">
      <button class="btn btn-outline" onclick="window.print()">🖨️ In / Lưu PDF Trọn Bộ (A4)</button>
      <a href="#recipes" class="btn">Tra Cứu Thực Đơn & Nghe Audio</a>
    </div>
  </div>
</header>

<div class="container">
  <section class="hero">
    <h1>📖 Cẩm Nang & Thực Đơn Dưỡng Nhan 7 Thể Chất Đông Y (Bản Điện Tử Tự Động)</h1>
    <p>Hệ thống hóa <strong>7 Thể Chất Đông Y</strong>, <strong>Bảng Chống Chỉ Định An Toàn</strong>, <strong>Kho Thực Đơn Trà - Canh - Cháo - Chè - Ngũ Cốc Có Định Lượng</strong> tích hợp <strong>Audio đọc tự động</strong> và <strong>Lộ trình 28 ngày in PDF</strong>.</p>
  </section>

  <section class="section-box" id="constitutions">
    <h2>1. Bản Đồ 7 Thể Chất Đông Y & Quy Tắc Cấm Kỵ</h2>
    <p style="color:var(--muted);">Nguyên tắc vàng của dưỡng sinh Đông Y: <strong>Không có món bổ cho tất cả mọi người — chỉ có món đúng với thể chất của bạn.</strong></p>
    {''.join(constitution_cards)}
  </section>

  <section class="section-box" id="recipes">
    <h2>2. Kho Thực Đơn Dược Thiện Định Lượng (Tích Hợp Audio Nghe Khi Nấu)</h2>
    <div class="filter-bar">
      <select id="constFilter" onchange="filterHandbookRecipes()">
        <option value="all">-- Tất cả 7 Thể Chất --</option>
        <option value="khi_hu">Khí Hư (Mệt mỏi, hụt hơi)</option>
        <option value="huyet_hu">Huyết Hư (Da xanh, rụng tóc, ngủ nông)</option>
        <option value="duong_hu">Dương Hư (Tay chân lạnh, đau bụng kinh)</option>
        <option value="am_hu">Âm Hư (Nóng trong, khô da, bốc hỏa)</option>
        <option value="dam_thap">Đàm Thấp (Tích nước, da dầu, nặng người)</option>
        <option value="thap_nhiet">Thấp Nhiệt (Mụn viêm đỏ, miệng đắng)</option>
        <option value="khi_uat_huyet_u">Khí Uất / Huyết Ứ (Stress, nám sạm)</option>
      </select>
      <select id="catFilter" onchange="filterHandbookRecipes()">
        <option value="all">-- Tất cả Nhóm Món --</option>
        <option value="Trà Dưỡng Nhan">Trà Dưỡng Nhan</option>
        <option value="Cháo Dưỡng Sinh">Cháo Dưỡng Sinh</option>
        <option value="Canh Thực Dưỡng">Canh Thực Dưỡng</option>
        <option value="Chè Cổ Truyền">Chè Cổ Truyền</option>
        <option value="Ngũ Cốc & Sữa Hạt">Ngũ Cốc & Sữa Hạt</option>
      </select>
      <input type="text" id="kwFilter" placeholder="Tìm nguyên liệu, triệu chứng (VD: táo đỏ, rụng tóc, mụn, mất ngủ)..." oninput="filterHandbookRecipes()">
    </div>
    <div class="recipe-grid" id="handbookRecipeGrid">
      {''.join(recipe_cards)}
    </div>
  </section>

  <section class="section-box" id="plan28">
    <h2>3. Bảng Theo Dõi Lộ Trình 28 Ngày Phục Hồi Khí Huyết (Có thể in ra giấy)</h2>
    <table class="tracker">
      <thead>
        <tr>
          <th>Tuần</th>
          <th>Mục tiêu trọng tâm</th>
          <th>Thói quen Sáng (07:00 - 09:00)</th>
          <th>Thói quen Chiều (14:00 - 16:30)</th>
          <th>Thói quen Tối (21:30 - 22:45)</th>
          <th>Đánh dấu hoàn thành</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Tuần 1 (Ngày 1–7)</strong></td>
          <td>Thanh lọc thói quen gây hại Tỳ Vị & ngưng đồ uống đá lạnh</td>
          <td>1 cốc nước ấm 250ml + Cháo/Sữa hạt ấm theo thể chất</td>
          <td>1 bình trà dưỡng nhan đúng thể chất (uống ấm trước 16h30)</td>
          <td>Ngâm chân nước ấm 40°C trong 15 phút, tắt màn hình trước 22h45</td>
          <td>☐ N1 ☐ N2 ☐ N3 ☐ N4 ☐ N5 ☐ N6 ☐ N7</td>
        </tr>
        <tr>
          <td><strong>Tuần 2 (Ngày 8–14)</strong></td>
          <td>Bồi bổ Khí Huyết / Tư Âm / Trừ Thấp chuyên sâu</td>
          <td>Ăn sáng ấm có ngũ cốc/hoài sơn/táo đỏ</td>
          <td>Luân phiên 2 bài trà dưỡng nhan + 5 phút thở bụng sơ can</td>
          <td>2 bữa canh/chè thực dưỡng trong tuần + ngủ sâu trước 23h</td>
          <td>☐ N8 ☐ N9 ☐ N10 ☐ N11 ☐ N12 ☐ N13 ☐ N14</td>
        </tr>
        <tr>
          <td><strong>Tuần 3 (Ngày 15–21)</strong></td>
          <td>Điều hòa chu kỳ sinh học & tăng tuần hoàn sắc diện</td>
          <td>Chải đầu dưỡng sinh 50 cái + bữa sáng ấm</td>
          <td>Trà hoa/dược thiện theo giai đoạn chu kỳ (trước/sau kinh)</td>
          <td>Xoa ấm vùng bụng (Quan Nguyên) hoặc lòng bàn chân (Dũng Tuyền)</td>
          <td>☐ N15 ☐ N16 ☐ N17 ☐ N18 ☐ N19 ☐ N20 ☐ N21</td>
        </tr>
        <tr>
          <td><strong>Tuần 4 (Ngày 22–28)</strong></td>
          <td>Ổn định nền tảng & đánh giá lại thể chất</td>
          <td>Duy trì 80% bữa ấm, hạn chế đường tinh luyện</td>
          <td>Dùng món dưỡng nhan 3-4 lần/tuần theo thời tiết</td>
          <td>Làm lại bài test 7 thể chất để cập nhật thực đơn tháng mới</td>
          <td>☐ N22 ☐ N23 ☐ N24 ☐ N25 ☐ N26 ☐ N27 ☐ N28</td>
        </tr>
      </tbody>
    </table>
  </section>
</div>

<footer class="page-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-col">
        <h4>Về Tủ Sách Dưỡng Sinh AI</h4>
        <p>Hệ thống hỗ trợ cá nhân hóa thực dưỡng Đông Y chuẩn 7 thể chất. Tích hợp audio giọng đọc và tài liệu in ấn PDF tiện lợi cho cả gia đình.</p>
      </div>
      <div class="footer-col">
        <h4>Liên Kết Nhanh</h4>
        <ul>
          <li><a href="index.html">Trắc Nghiệm 7 Thể Chất (60s)</a></li>
          <li><a href="#recipes">Kho Thực Đơn Định Lượng & Audio</a></li>
          <li><a href="#plan28">Lộ Trình 28 Ngày In Ấn (PDF)</a></li>
          <li><a href="index.html#tro-ly-tra-cuu">Trợ Lý Tra Cứu Triệu Chứng</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Hỗ Trợ & Thanh Toán Tự Động</h4>
        <ul>
          <li>Thanh toán tự động: VietQR & Payoneer Quốc Tế</li>
          <li>Hỗ trợ khách hàng: <a href="mailto:lethanhmaicombo@gmail.com">lethanhmaicombo@gmail.com</a></li>
          <li>Giao nhận tài liệu: Mở tức thì trên trình duyệt sau khi quét mã</li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Tuyên Bố Miễn Trừ Y Khoa</h4>
        <p style="font-size:0.8rem; line-height:1.5;">Tài liệu mang tính chất giáo dục dưỡng sinh ẩm thực cổ truyền, nâng cao thói quen sinh hoạt. Không thay thế chẩn đoán, toa thuốc hay điều trị của bác sĩ chuyên khoa.</p>
      </div>
    </div>
    <div class="footer-bottom">
      © 2026 Tủ Sách Dưỡng Sinh AI • Bảo lưu mọi quyền • Vận hành tự động bởi Money HQ.
    </div>
  </div>
</footer>

<script>
function filterHandbookRecipes() {{
  const cVal = document.getElementById('constFilter').value;
  const catVal = document.getElementById('catFilter').value;
  const kw = document.getElementById('kwFilter').value.trim().toLowerCase();
  const items = document.querySelectorAll('.recipe-item');
  items.forEach(el => {{
    const matchConst = (cVal === 'all') || (el.getAttribute('data-constitution') === cVal);
    const matchCat = (catVal === 'all') || (el.getAttribute('data-category') === catVal);
    const matchKw = !kw || el.innerText.toLowerCase().includes(kw);
    el.style.display = (matchConst && matchCat && matchKw) ? 'flex' : 'none';
  }});
}}

function speakRecipe(btn) {{
  if (!('speechSynthesis' in window)) {{
    alert('Trình duyệt của bạn không hỗ trợ đọc giọng nói tự động.');
    return;
  }}
  window.speechSynthesis.cancel();
  const text = btn.getAttribute('data-speech');
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'vi-VN';
  utter.rate = 1.0;
  btn.innerText = '🔊 Đang đọc Audio... (Bấm để nghe lại)';
  utter.onend = () => {{ btn.innerText = '🔊 Nghe hướng dẫn Audio (Miễn phí)'; }};
  window.speechSynthesis.speak(utter);
}}

(function() {{
  const params = new URLSearchParams(window.location.search);
  const c = params.get('constitution');
  if (c && document.getElementById('constFilter')) {{
    document.getElementById('constFilter').value = c;
    filterHandbookRecipes();
  }}
}})();
</script>
</body>
</html>
"""


def write_handbook_html(output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_handbook_html(), encoding="utf-8")
    return path
