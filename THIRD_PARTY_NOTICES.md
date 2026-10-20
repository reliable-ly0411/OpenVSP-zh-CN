# 第三方内容与许可边界

OpenVSP 原软件及其适用的修改遵循根目录 `LICENSE` 所载 NASA Open Source Agreement
1.3。该声明不把独立第三方库、字体或社区示例重新许可为 NOSA。

## 第三方库与字体

上游依赖、随附库和字体保留各自版权与许可证。根目录 `README.md` 的依赖说明、各依赖
目录中的原许可文件，以及原生构建按需要附带的第三方许可说明共同给出归属；本文件不
取代这些原文。仅把文件放入同一个 ZIP，不改变第三方内容原有的许可。

## 额外社区整机模型

源码目录 `examples/Complete_Aircraft`（历史安装包中的
`Official_Examples/Complete_Aircraft`）是另行汇集的模型，不全是 OpenVSP 原作者作品。
模型文件没有因规范化文件名而改变内容。逐文件作者、来源 URL 与 SHA-256 见该目录的
`SOURCES_AND_LICENSES.md`。

| 文件 | 来源记录中的作者 | 来源记录中的许可 |
|---|---|---|
| `NASA_X-57_Maxwell_Simplified_CRM_v4.4.1.vsp3` | Brandon Litherland | No Rights Reserved / CC0 |
| `NASA_N2A_Hybrid_Wing_Body.vsp3` | Farhan Malik | No Rights Reserved / CC0 |
| `Community_Vans_RV-12.vsp3` | Mathieu | No Rights Reserved / CC0 |
| `NASA_Six-Passenger_Tiltwing_UAM.vsp3` | Siena Whiteside | No Rights Reserved / CC0 |
| `Uber_eCRM-002_Lift-Plus-Cruise.vsp3` | Ian Villa | No Rights Reserved / CC0 |
| `Community_F-A-18C_Hornet.vsp3` | Elias GH | Attribution Share Alike / CC BY-SA；具体版本未确认 |
| `Community_Joby_S4_eVTOL.vsp3` | Vipul Gadekar | Attribution Share Alike / CC BY-SA；具体版本未确认 |
| `Community_Kitty_Hawk_Heaviside_eVTOL.vsp3` | Vipul Gadekar | Attribution Share Alike / CC BY-SA；具体版本未确认 |

三份版本未确认的模型不能由本项目替作者选择 CC BY-SA 3.0 或 4.0，也不因放在仓库或
旧包中而转成 NOSA 或 CC0。来源记录与署名不能代替缺失的版本授权证据。

[2026-10-20 许可来源核查](docs/community-model-license-evidence-20261020.md)区分当日可读
原站字段、未取得的历史快照与尚未解决的信息缺口。此记录不认定违法，也不保证适用特定
再分发用途。若需要修改/再分发这些模型，应先取得可对应到具体文件的明确许可版本及
适用条款；本项目不代表模型作者作此授权。

## 参考许可链接

- [CC0 官方说明](https://creativecommons.org/publicdomain/zero/1.0/)
- [CC BY-SA 3.0 Unported](https://creativecommons.org/licenses/by-sa/3.0/)及[完整条款](https://creativecommons.org/licenses/by-sa/3.0/legalcode)
- [CC BY-SA 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/)及[完整条款](https://creativecommons.org/licenses/by-sa/4.0/legalcode)

后两项仅用于说明已知存在的不同版本，不表示三模型适用其中任一版本。明确版本后仍需
遵守该许可对署名、许可链接、修改说明与衍生模型相同方式共享的适用要求。制造商名称、
商标或机型名称仅用于识别，不表示制造商、NASA、OpenVSP 或 VSP Airshow 认可该模型。
