# OpenVSP 官方案例索引

本目录随 OpenVSP 简体中文汉化版发布，内容来自 OpenVSP 3.51.2 上游源码中的官方
`examples` 目录。案例本身的版权、作者归属和许可保持上游规定不变；中文索引由
OpenAI Codex AI 生成。

## 推荐入口

- `Complete_Aircraft`：可直接打开的经典官方/社区整机 `.vsp3` 模型；包含固定翼、混合翼身、
  分布式电推进以及 NASA 倾转翼、升力+巡航、Joby S4、Heaviside 等 eVTOL/VTOL 案例，
  并附来源、许可和 SHA-256 说明。
- `scripts`：OpenVSP API、几何建模、文件导入导出和分析脚本案例。
- `vspaero_ex`：VSPAERO 固定翼、旋翼、非定常计算及 API 案例。
- `CustomScripts`：自定义几何体脚本案例。
- `airfoil`：翼型数据文件案例。
- `CCE`：自定义组件扩展案例。
- `matlab`：MATLAB 接口及数据处理案例。
- `textures`：纹理图片和纹理映射素材。

## 使用方式

1. 建议先复制具体案例到用户可写的工作目录，再进行计算或修改。
2. `.vspscript` 文件可通过“文件 → 运行脚本...”执行。
3. `.vsp3` 模型可通过“文件 → 打开...”载入。
4. VSPAERO 案例通常包含自己的 README，请先阅读对应子目录说明。
5. 部分案例会生成网格、结果或日志文件，不建议直接在只读安装目录中运行。

`Complete_Aircraft` 中的社区模型并非 OpenVSP 官方精度基准；请在工程使用前自行核验。
模型的作者、原始下载页面、许可和 SHA-256 记录在该目录的
`SOURCES_AND_LICENSES.md` 中。

为保持官方案例可对照升级，除本中文索引外，不在此目录中改写上游案例内容。
