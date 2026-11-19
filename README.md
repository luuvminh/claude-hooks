# claude-hooks

Hook chung cho Claude Code của Max, dùng ở mọi dự án, cả cloud lẫn Mac.

| Hook | Khi nào | Làm gì |
|---|---|---|
| superpowers | mở phiên | nạp skill `using-superpowers` |
| ponytail | mở phiên, mỗi tin, mỗi subagent | bật chế độ ponytail |
| ponytail-gate | lúc báo xong | chặn một lần nếu code đổi so với nhánh chính mà chưa `/ponytail-review` |
| impeccable | sửa file, lúc báo xong | quét file giao diện (file khác thì bỏ qua) |
| repo-hooks | mở phiên | kéo lại nhánh chính của từng repo (bản clone mới trên cloud hay bị cũ, cổng chặn nhầm) |
| repo-hooks | mọi sự kiện | phiên mở ở thư mục cha (cloud: `/home/user`) thì chạy hook riêng của từng repo con, ví dụ maypiano |

Repo nào đã có sẵn hook cùng tên trong `.claude/settings.json` thì hook chung tự nhường, không chạy hai lần.
Không có repo, không có code, không có file giao diện: hook im lặng.

## Cài

```bash
git clone https://github.com/luuvminh/claude-hooks ~/.claude/claude-hooks
bash ~/.claude/claude-hooks/install.sh
```

`install.sh` gộp vào `~/.claude/settings.json` (giữ mọi cài đặt khác, sao lưu file cũ thành `settings.json.bak-<giờ>`),
và nối skill vào `~/.claude/skills/` nếu chưa có skill cùng tên. Chạy lại bao nhiêu lần cũng được.

Tự cập nhật: mỗi lần mở phiên (tối đa 6 giờ một lần) hook `self-update.sh` kéo bản mới về và cài lại.

Sau khi duyệt xong: `python3 ~/.claude/claude-hooks/hooks/ponytail-gate.py --stamp` (chạy trong repo, hoặc thư mục cha).

## Kiểm

```bash
python3 tests/test_fetch.py
```

## Gỡ

Xoá các mục có `claude-hooks` trong `~/.claude/settings.json` (hoặc chép lại file `.bak-…`), rồi xoá `~/.claude/claude-hooks`.

## Nguồn

- superpowers: github.com/obra/superpowers (MIT, `hooks/SUPERPOWERS-LICENSE`)
- ponytail: github.com/DietrichGebert/ponytail (MIT, `hooks/PONYTAIL-LICENSE`)
- impeccable: github.com/pbakaus/impeccable (`skills/impeccable`)
