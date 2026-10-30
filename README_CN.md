# 全球城市持续高热效应研究代码与数据

本仓库提供论文 *High urban heat is harder to escape the longer it lasts* 对应的城市年度数据、统计分析程序、2030年条件延伸程序，以及正文Fig. 1–5的图表数据和绘图代码。

研究覆盖2001—2024年全球9,713座城市。年度高热效应采用2001—2005年城市年度UAH合并分布的第90百分位数作为阈值（1.426 °C）。连续至少三年达到该阈值的城市被归类为持续高热效应城市。

## 运行方法

使用Python 3.10或更新版本，在仓库根目录执行：

```bash
python -m pip install -r requirements.txt
python run_all.py --mode verify
python run_all.py --mode plot
```

其他运行模式：

| 命令 | 功能 |
| --- | --- |
| `python run_all.py --mode recompute-core` | 重算状态转移、人口分解和区域统计 |
| `python run_all.py --mode refit-gee` | 拟合持续时间与下一年退出概率的GEE模型 |
| `python run_all.py --mode scenarios` | 重算2024—2030年条件延伸及1,500次城市分层bootstrap |
| `python run_all.py --mode reproduce` | 依次执行分析、数值检查和正文五张图的绘制 |

程序输出保存于`outputs/`，正文五张图的PDF与PNG文件位于`figures/main/`。

## 目录内容

| 目录 | 内容 |
| --- | --- |
| `data/input/` | 2001—2024年城市年度UAH、人口、面积及区域属性 |
| `figure_packages/fig1/` | 全球年度高热效应状态、持续时间、人口变化和2030年条件延伸 |
| `figure_packages/fig2/` | 城市历史状态组成、进入退出、持续时间及GEE模型 |
| `figure_packages/fig3/` | 持续城市人口变化的对称分解 |
| `figure_packages/fig4/` | IPCC AR6区域高热效应进入率、退出率与分类 |
| `figure_packages/fig5/` | 区域持续城市变化及人口分解 |
| `analysis/` | 状态概率传播与分层bootstrap计算 |
| `basemap/` | 地理图件底图文件 |
| `scripts/` | 数据及结果核验程序 |
| `figures/main/` | 正文五张图的PDF与PNG文件 |
| `docs/` | 数据字典、图表索引和网页上传指南 |

Fig. 4统计年度高热效应状态的进入与退出，Fig. 5统计持续状态的进入与退出，并展示对应的区域人口变化。区域归属使用城市年度表中的`IPCC_Acronym`字段。

## 主要结果

城市年度数据共233,112条。持续城市数量从2003年的706座增加至2024年的1,509座，占2024年2,127座高热效应城市的70.9%。其中，537座在整个24年观测期内保持高值，830座的当前高值持续时间至少为11年。

2003—2024年，持续城市所包含的人口增加613.4百万人。年度对称分解显示，城市持续状态成员变化贡献488.5百万人（79.6%），城市内部人口变化贡献124.9百万人（20.4%）。三个历史进入条件下，2030年持续城市数量的条件期望分别为1,764、1,813和1,857座。

## 研究方法与数据来源

年度城市增量热效应（UAH）由城市像元UTCI与匹配的自然参考像元UTCI之差计算，并在固定的2020年城市边界内聚合。人口数据采用LandScan Mosaic年度环境人口序列，区域划分依据IPCC AR6参考区域。

Fig. 1d使用`figure_packages/fig1/Fig1D_scenarios_2030.csv`中的情景数据绘制。`analysis/scenario_2030.py`实现条件状态传播及分层bootstrap计算，并将计算结果输出到`outputs/scenarios/Fig1D_recomputed.csv`。

- GloUTCI-M数据：[doi:10.5281/zenodo.8310513](https://doi.org/10.5281/zenodo.8310513)。
- LandScan Mosaic Annual Global Ambient Population Time Series, Version 1.0：[doi:10.48690/lsm/zew2-1n91](https://doi.org/10.48690/lsm/zew2-1n91)。
- IPCC AR6参考区域：Iturbide, M. et al., *Earth System Science Data* **12**, 2959–2970 (2020)。

更多字段说明与程序对应关系见[数据字典](docs/DATA_DICTIONARY.md)和[图表索引](docs/FIGURE_AND_ANALYSIS_INDEX.md)。
