# 三个社区模型的许可版本核查

核查日期：2026-10-20 UTC。关联 [#16](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/16)。
结论：**当前可读来源确认 CC BY-SA 类别，但仍不能确认具体许可版本。** 不据此认定违法，
也不以本地补充文字替作者授予或选择版本。

## 原站可核实的内容

| 仓库模型文件 | 作者/上传者 | 原详情页 | 当前公开记录 `license` |
|---|---|---|---|
| `Community_F-A-18C_Hornet.vsp3` | Elias GH | [F/A-18C Hornet](https://www.airshow.openvsp.org/vsp/UhhSt017Farl1R7v4Km3) | `3` |
| `Community_Joby_S4_eVTOL.vsp3` | Vipul Gadekar | [JOBY S4 EVTOL](https://www.airshow.openvsp.org/vsp/LtyRrSrYXRhQlDkYwPDX) | `3` |
| `Community_Kitty_Hawk_Heaviside_eVTOL.vsp3` | Vipul Gadekar | [Kitty Hawk Heaviside](https://www.airshow.openvsp.org/vsp/V5S83k61gbka8UqusT5E) | `3` |

原站为客户端渲染应用。公开详情页的
[渲染模块](https://www.airshow.openvsp.org/_nuxt/KyeboZow.js)从公开 `models` 记录读取
`license`，再查找[许可选择表](https://www.airshow.openvsp.org/_nuxt/CMn6fkRq.js)。
该选择表把 `3` 映射为 `Attribution Share Alike (CC BY-SA)`；没有版本或许可 URL 字段。
[许可帮助组件](https://www.airshow.openvsp.org/_nuxt/5btKxp_0.js)说明署名和衍生作品相同方式
共享的一般含义，但也未注明具体版本或指向某版本条款。

当日公开记录的精简摘录、数据端点、来源响应 SHA-256、前端文件摘要，以及本地模型
文件 SHA-256 保存为[机器可读证据](community-model-license-evidence-20261020.json)。摘录
不包含站点配置、账户 ID、下载令牌或与许可核查无关的信息。响应摘要可用于识别本次
读取的响应，不能保证未来查询仍返回相同字节，也不是独立时间戳或公证存档。

## 尚未取得的证据

- 原文只记录下载日期 2026-08-10，没有该日期的完整详情页快照或作者许可确认。
- 对上述三个精确模型 ID，以 `*airshow.openvsp.org/vsp/<ID>` 查询 Wayback CDX，
  HTTP 200 但结果均为空数组。这里只能说本次查询未返回记录，不能断言全网不存在存档。
- 原站记录中的更新时间早于本次查询，不足以证明下载当日适用的具体许可版本。
- 没有把当前 CC 官网推荐版本、站点其他资源的许可、类似模型的许可或公开的下载按钮
  当作三模型的版本授权证据。

[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)与
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)是不同文本。
两个官方链接可供阅读，不能从类别名倒推出作者给某个文件选择了其中哪一个。

## 分发边界与下一步

根目录 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)及
[逐文件来源](../examples/Complete_Aircraft/SOURCES_AND_LICENSES.md)明确区分 NOSA 软件、
CC0 社区模型和三份许可版本待核实模型，保留作者、原链接和字节哈希。

许可版本未补齐之前，不能把该信息缺口标为“已获得明确授权”。后续包可以采用隔离这三份
额外样例的方式消除继续随包分发的范围；恢复收录应先获得对应文件的明确许可版本、
许可链接与来源证据，并保留实际修改说明。该方案不需要改变任何建模或分析功能，也不
影响全部上游示例及其余五份 CC0 整机样例。

历史标签、仓库文件及已公开包保持原样；没有静默换包或改写历史附件。当前文档修订本身
不是移除旧内容的动作，也不是原作者的许可确认。新的包策略必须在对应源码、打包检查和
实际新产物中一致体现后，才能宣称该新包已完成隔离。
