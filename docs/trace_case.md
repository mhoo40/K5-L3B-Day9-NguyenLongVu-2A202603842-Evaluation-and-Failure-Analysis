# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi bạn 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (Run ID: `E-seeded_regression-20261118-8d8b`) |
| Triệu chứng | `pass_rate` (`lab8` grader: `FAIL (status resolved != denied)`), `db_fact_kept` (`False`), và `refund_amount_correct` (`False`) đều fail. **Ledger** ghi `refund_vnd=20000`, `refund_count=1`, `status=resolved` (trong khi nhãn chuẩn yêu cầu `refund_vnd=0`, `refund_count=0`, `status=denied`); **reply** ở bước 6 nói trôi chảy `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` — khớp với con số sai trên ledger nhưng sai hoàn toàn so với chính sách. |
| Bước sai đầu tiên | **Event #3** · `model_override` · `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | **Event #1** (`handoff`) giao đúng công cụ (`lookup_order`, `lookup_policy`, `compute_compensation`) với phạm vi `owner_order_only` và nhiệm vụ `check_applicable_policy`; **Event #2** (`investigator`) truy vấn DB thành công (`visible: true, reason: "ok"`) và trả về dữ liệu gốc của đơn `O-202` (`status: "delivered"`, số ngày trễ thực tế không thỏa điều kiện hoàn). Mọi dữ liệu đầu vào trước bước 3 đều chính xác; sai lệch chỉ bắt đầu khi Event #3 tự ý ghi đè `delay_days = 5`, kéo theo Event #4 (`quote`) tính sai `amount_vnd: 20000` (`SHIP-LATE-03`) và ghi nhầm 20.000đ vào ledger. |
| Failure mode | `FM-03` — Bịa / ghi đè dữ liệu từ DB (`model_override` làm sai lệch sự thật hệ thống trước khi tính bồi thường) |
| Đối chứng | Trên `fixed C-002@11`: **không có event `model_override`** nào chen vào sau bước 2; từ dữ liệu gốc ở Event #2, Event #3 (`quote`) trả về `{"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}`, Event #4 (`reply`) từ chối đúng chính sách (`"Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành."`), và ledger giữ `refund_vnd=0`, `refund_count=0`, `status=denied` khớp nhãn. |
| Regression test | Grader `DbFactKept` (`db_fact_kept` trong `src/lab9/graders.py` — phát hiện event `kind == "model_override"`) kết hợp `RefundAmountCorrect` (`ledger=20000 != label=0`) và test hồi quy trong `tests/test_lab9.py` (kiểm tra `C-002@11` / item tương ứng trong eval set): đã chạy xác nhận **fail** trên `seeded_regression` (`db_fact_kept = 0.9286 < 0.95`, `refund_amount_correct = 0.7857 < 0.95`) và **pass** trên `fixed` (`db_fact_kept = 1.0`, `refund_amount_correct = 1.0`). |
| Chưa chắc chắn | Trace chỉ ghi lại sự kiện `model_override {"delay_days": 5}` đã xảy ra, nhưng **không chứng minh được nguyên nhân gốc ở tầng prompt/model** (do LLM tự suy diễn số ngày giao hàng từ văn bản khiếu nại, do lỗi parse ngày tháng, hay do injection trong prompt) và chưa kiểm chứng trên LLM thật ngoài `MockLLM`. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
