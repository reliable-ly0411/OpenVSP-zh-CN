# OpenVSP 3.51.3 rc.2 交互式桌面验收

完成时间：2026-10-20T06:47:40Z。

[实际证据 ZIP](desktop-acceptance.zip)，595774 字节，SHA-256：`2100cd1a7e3db7b7d1c7120c96e61397639016830397291d171a7325337e5a02`。

包内含 11 张 OpenVSP 应用窗口 PNG、原始合成模型和 GUI 保存后的模型 XML，以及 [审阅记录](gui-review.json)。测试模型来自固定 [生成脚本](../gui-fixture.as)，没有用户模型或其他应用截图。

原始 Linux ZIP SHA-256：`bc68f35be5849f19598490c169d0d6e52f80a8dd076078d2a3e698c537870cd8`。主界面、几何体树、机翼常规/平面形、关于版本与仓库、实际另存为及打开均通过有限检查。保存文件名为 `GUI Roundtrip 100% 中文.vsp3`，持久化名称和 ID 与原模型一致。

环境为 Debian 13 Linux x86_64 云桌面运行 Ubuntu 24.04 构建的原包；Windows、macOS 和 Linux ARM64 GUI 未作同范围验收，不是全部页面或工程数值准确性证明。
