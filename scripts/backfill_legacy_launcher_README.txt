历史 Linux 中文界面兼容启动器 / Historical Linux Chinese GUI launcher

OpenVSP 3.51.2 / 3.51.3 Ubuntu ARM 包请使用 ./vsp-zh-CN 启动中文界面。
例如：./vsp-zh-CN "my model.vsp3"
运行依赖：fontconfig、fonts-noto-cjk，以及包原有的图形/系统运行库。

历史 vsp 原二进制保持不变。直接执行 ./vsp 仍可能将中文显示为方框；
其 -help 在无 X11 显示环境下也可能失败。这些是历史版本的已知限制。
启动器仅为自身进程及 vsp 设置 FONTCONFIG_FILE，不修改系统或用户字体配置。
应用专用配置仍读取 /etc/fonts/fonts.conf，保留系统字体目录/缓存；
仅将 Helvetica/Courier 与 FLTK 实际 sans/mono 家族映射至 Noto CJK。
模型、帮助、CLI 与 Python API 的原有验证要求不变。

Launch the Chinese GUI using ./vsp-zh-CN, not the unchanged ./vsp binary.
Install fontconfig and fonts-noto-cjk. The launcher forwards arguments unchanged
and applies package-local Fontconfig aliases only to its process. It does not
modify system or user configuration. Direct vsp execution may still show tofu.
