# OpenVSP 3.53.0 rc.2 交互式桌面验收

完成时间：2026-10-20T06:44:35Z。

[实际证据 ZIP](desktop-acceptance.zip)，472630 字节，SHA-256：`e4cbfce5ff33279fb233530501af594608ca15d89b4444ba0a23ab59fac47527`。

包内含 10 张 OpenVSP 应用窗口 PNG、原始合成模型和 GUI 保存后的模型 XML，以及 [审阅记录](gui-review.json)。测试模型来自固定 [生成脚本](../gui-fixture.as)，没有用户模型或其他应用截图。

原始 Linux ZIP SHA-256：`8414b3751fe10976c1766483e97c6904899553463cd3b73c476e7378a8099e2a`。主界面、几何体树、机翼常规/平面形、关于版本与仓库、实际另存为及打开均通过有限检查。保存文件名为 `GUI Roundtrip 100% 中文.vsp3`，持久化名称和 ID 与原模型一致。

环境为 Debian 13 Linux x86_64 云桌面运行 Ubuntu 24.04 构建的原包；Windows、macOS 和 Linux ARM64 GUI 未作同范围验收，不是全部页面或工程数值准确性证明。
