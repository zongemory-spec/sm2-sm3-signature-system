# 验证证据与复现

本地验证日期：2026-10-31。

- 17 项 unittest 通过，0 跳过、0 失败；强制要求 OpenSSL 可用。
- SM3 的 abc 与 abcd 重复 16 次两个已知向量匹配。
- SM3 与 Python hashlib 所用 OpenSSL 实现交叉比较，包含空输入、UTF-8 和 0..255 二进制字节。
- gmssl 签名 → OpenSSL 验证通过；OpenSSL 签名 → gmssl 验证通过。
- OpenSSL 验证时改动消息或使用不同身份 ID，均拒绝原签名。
- 覆盖空格/换行绑定、文件字节变化、另一个有效公钥、非法公钥点、私钥范围、签名标量、旧版显式验证和密钥成对校验。
- 测试只生成一次性演示密钥，不导出私钥；报告不含私钥、随机 nonce 或用户原文件。

[JSON 报告](../reports/verification.json) · [测试日志](../reports/tests.txt)

## 运行

```sh
python -m pip install gmssl==3.2.2
python -m unittest discover -s tests -v
python demo_evidence.py --require-openssl --out reports/my-verification.json
```

OpenSSL 交叉验证通过系统/Python 的 libcrypto 库执行。找不到兼容库时，普通测试会跳过对应检查；设置 REQUIRE_OPENSSL=1 或使用 --require-openssl 会将缺少库视为失败，不把“未测试”写成通过。CI 在 Ubuntu 强制开启此项。

本次独立库版本为 OpenSSL 3.0.16。这是特定参数组合的互操作检查，不是密码产品认证、实现审计或完备标准符合性测试。

## 桌面验收

桌面程序已启动且未报告启动异常，但当前桌面自动化连接超时；未完成自动按钮验收或截图，不将其记录为已通过。

请在本地使用演示密钥验收：

1. 签名页输入“合成签名演示”，生成 V2 签名，导出 .sig。
2. 验签页导入对应公钥与签名，输入完全相同的文字，点击文本验签。
3. 使用篡改测试和错误公钥测试，查看拒绝日志。
4. 用临时 TXT/PDF/DOCX 文件重复文件签名与验签；改变任意字节应不匹配。
5. 用以前保存的旧版签名确认默认拒绝，勾选兼容模式后再按旧语义验证。

截图只展示演示公钥、摘要、签名及结果，不放真实原文件或私钥。当前界面不直接显示私钥。

## 核对来源

- [SM3 公开算法说明附录 A](https://datatracker.ietf.org/doc/html/draft-sca-cfrg-sm3-00#appendix-A)：本项目使用其中的已知向量。该文档是历史 Internet-Draft，不是 IETF 对本项目的认证。
- [py-gmssl 接口说明](https://github.com/py-gmssl/py-gmssl)：sign / verify 与 sign_with_sm3 / verify_with_sm3 的区别。
- [OpenSSL SM2 EVP 文档](https://docs.openssl.org/3.0/man7/EVP_PKEY-SM2/)：消息摘要和身份 ID 参与 SM2 签名的方式。
