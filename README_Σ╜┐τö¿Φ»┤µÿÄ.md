# PDF Flatten 工具 - 使用说明

这是一个带图形界面的桌面小工具，现在支持：
- 导入单个 PDF
- 一次过多选多个 PDF 批量处理
- 一键做强力 flatten
- 单个文件导出为新的 PDF
- 多个文件导出到另外一个文件夹
- 切换中文 / English / Bahasa Melayu 界面

## 这个工具的做法
本工具采用 **图像化强力 flatten**：
1. 打开原始 PDF
2. 把每一页渲染成高分辨率图像
3. 再按原页面大小重建成新的 PDF
4. 导出 flatten 后的文件

这种方式的优点是：
- 输出 PDF 更难再被直接编辑
- 原来的表单、可编辑图层、部分可修改对象会被“压平”

需要注意：
- 通常会失去文字搜索、复制文字、表单填写、链接等功能
- DPI 越高越清晰，但文件也会更大

## 推荐设置
- 150 DPI：文件较小
- 200 DPI：推荐，清晰度和体积较平衡
- 300 DPI：更清晰，但文件通常更大

## 图形界面用法
### 单个 PDF
1. 点击“浏览 / 多选”选择 1 个 PDF
2. 点击“选择保存位置”
3. 选择新的输出 PDF 文件名
4. 点击“开始 Flatten”

### 批量 PDF
1. 点击“浏览 / 多选”
2. 一次过选中多个 PDF
3. 点击“选择保存位置”
4. 选择一个 **新的输出文件夹**
5. 点击“开始 Flatten”

批量模式下，输出文件会自动命名为：
- `原文件名_flattened.pdf`

例如：
- `A.pdf` -> `A_flattened.pdf`
- `Report.pdf` -> `Report_flattened.pdf`

## 运行方法
先安装依赖：
```bash
pip install -r requirements.txt
```

然后启动图形界面：
```bash
python app.py
```

## 命令行模式
```bash
python app.py --cli --input input.pdf --output output.pdf --dpi 200 --lang zh
```

`--lang` 可选：
- `zh`
- `en`
- `ms`

## Windows 打包 EXE
在 Windows 电脑里运行：
```bat
build_windows.bat
```

打包后输出位置：
```text
dist\PDF-Flatten-Tool.exe
```
