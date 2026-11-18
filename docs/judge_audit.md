# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (`tp=24, fp=4, fn=6, tn=66`) | dùng (non-blocking / theo dõi) |
| helpful | 100 | <κ của helpful> | <P của helpful> | <R của helpful> | Không (κ < 0.6) | loại |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | `H-008` ("Em đã hoàn tiền cho anh rồi nha, anh check giúp em.") | PASS | FAIL | Người đúng (FN) | Dùng văn nói thân mật ("nha", "check giúp em"), thiếu chuẩn mực CSKH nhưng judge bỏ sót lỗi giọng điệu. |
| 2 | `H-017` ("Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha.") | PASS | FAIL | Người đúng (FN) | Có "Dạ" ở đầu nên đánh lừa judge, nhưng cụm "bạn ơi ... rồi nha" vẫn quá suồng sã. |
| 3 | `H-029` ("Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm.") | PASS | FAIL | Người đúng (FN) | Câu cộc lốc, thiếu lịch sự/thấu cảm ("không cần nhắn thêm"), judge chỉ bắt từ khóa "Dạ" nên chấm nhầm PASS. |
| 4 | `H-042` ("Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ.") | FAIL | PASS | Người đúng (FP) | Câu trả lời lịch sự, đủ "Dạ ... ạ" và thông tin rõ ràng, judge bắt nhầm lỗi (false positive). |
| 5 | `H-051` ("Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ.") | FAIL | PASS | Người đúng (FP) | Giọng điệu lịch sự ("Dạ ... ạ"), judge nhạy cảm quá mức với từ tiếng Anh "refund" (false positive). |

## Kết luận
- Tiêu chí bị loại và lý do (dẫn ma trận nhầm lẫn): Loại `helpful` vì tiêu chí "hữu ích" mang tính chủ quan cao, độ đồng thuận với nhãn người thấp (`κ < 0.6`, không đạt ngưỡng `FLOORS` — ma trận nhầm lẫn `<tp=..., fp=..., fn=..., tn=...>`, số lượng false positive/false negative cao khi câu trả lời dài hoặc đúng ngữ pháp nhưng sai nghiệp vụ), nên không đủ độ tin cậy để đưa vào gate. Ngược lại, `tone_ok` đạt toàn bộ ngưỡng (`κ = 0.757 ≥ 0.6`, `P = 0.857 ≥ 0.8`, `R = 0.800 ≥ 0.7` với `tp=24, fp=4, fn=6, tn=66`, tỷ lệ lỗi hiệu chỉnh `0.30` so với quan sát `0.28`).
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai (`n=100`), dễ bị overfit vào các mẫu câu cố định (ví dụ quá phụ thuộc vào từ khóa `"Dạ"`/`"ạ"` như ở các ca `H-017`, `H-029`, `H-051`); cần thu thập nhãn người mới trên các mẫu phản hồi thực tế chưa từng công bố để có tập held-out thật.
