# OpenVSP 3.54.0 rc.2 交互式桌面验收

完成时间：2026-10-20T05:58:30Z。

[实际证据 ZIP](desktop-acceptance.zip)，598222 字节，SHA-256：`9e6841b9b6f98cc065e0311670864b93313ee5d21b5be60208d0d57b70334af6`。

包内含 11 张 OpenVSP 应用窗口 PNG、原始合成模型和 GUI 保存后的模型 XML，以及 [审阅记录](gui-review.json)。测试模型来自固定 [生成脚本](../gui-fixture.as)，没有用户模型或其他应用截图。

原始 Linux ZIP SHA-256：`a0534b9c5ad5767d787d7d509abc4c988588bbc8c7841e932c7ac6387f746d01`。主界面、几何体树、机翼常规/平面形、关于版本与仓库、实际另存为及打开均通过有限检查。保存文件名为 `GUI Roundtrip 100% 中文.vsp3`，持久化名称和 ID 与原模型一致。

环境为 Debian 13 Linux x86_64 云桌面运行 Ubuntu 24.04 构建的原包；Windows、macOS 和 Linux ARM64 GUI 未作同范围验收，不是全部页面或工程数值准确性证明。
