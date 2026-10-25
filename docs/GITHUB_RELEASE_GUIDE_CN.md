# GitHub网页上传指南

本指南以`YZW-D/urban-heat-persistence`为仓库名称示例，采用GitHub网页操作。

## 准备文件

1. 下载并解压发布压缩包，进入`urban_heat_persistence`文件夹。
2. 打开`README.md`，确认正文标题、数据目录及Fig. 1–5信息。
3. 在本机Python环境中执行`python -m pip install -r requirements.txt`和`python run_all.py --mode verify`，核对研究数据与正文统计量。

## 新建仓库

1. 登录[GitHub](https://github.com)，点击页面右上角`+`，选择`New repository`。
2. `Repository name`填写`urban-heat-persistence`，`Description`可填写`Code and data for persistent high urban heat effects in global cities, 2001–2024`。
3. 选择`Private`，保持默认的空仓库设置，点击`Create repository`。
4. 在仓库首页点击`uploading an existing file`，进入文件上传页面。
5. 在电脑上打开解压后的`urban_heat_persistence`目录，将里面的全部文件和文件夹拖入上传区域，包括`.gitignore`。
6. 确认上传后的根目录直接显示`README.md`、`data/`、`analysis/`和`figure_packages/`等内容。
7. 在提交说明中填写`Update code and data for revised manuscript`，点击`Commit changes`。

## 更新现有仓库

1. 打开仓库首页，点击`Add file`，选择`Upload files`。
2. 将新包的目录内容拖入上传区域，使用相同的目录路径更新同名文件。
3. 填写提交说明并点击`Commit changes`。
4. 在仓库文件列表中整理上一版本的旧文件和旧图表，保持当前目录与最新版正文一致。

## 检查与公开

1. 打开`README.md`，查看仓库首页显示内容。
2. 检查`data/input/city_year_2001_2024.csv`、`analysis/scenario_2030.py`、`figure_packages/fig1`至`fig5`以及`figures/main/Fig1.png`至`Fig5.png`。
3. 检查仓库的`Code`页面及主要文件的下载访问。
4. 在仓库的`Settings`中进入`General`，滚动到`Danger Zone`，选择`Change repository visibility`，将`Private`切换为`Public`。
5. 在`Releases`页面选择`Draft a new release`，填写版本标签`v1.0.0`及对应论文标题，发布代码和数据版本。

仓库地址为`https://github.com/YZW-D/urban-heat-persistence`。正文`Code availability`可以引用该地址。
