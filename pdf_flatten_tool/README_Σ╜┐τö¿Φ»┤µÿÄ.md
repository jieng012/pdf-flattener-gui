# PDF Flatten 工具 - 使用说明

这是一个带图形界面的桌面小工具，可以：
- 导入原有 PDF
- 一键做强力 flatten
- 导出新的 PDF
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

## Linux 打包
```bash
./build_linux.sh
```

## 目前版本限制
- 暂不支持需要密码才能打开的 PDF
- 输出路径不能和原始 PDF 完全相同

## 文件说明
- `app.py`：主程序（GUI + CLI）
- `requirements.txt`：运行依赖
- `build_windows.bat`：Windows 打包脚本
- `build_linux.sh`：Linux 打包脚本
- `app.ico` / `app_icon.png`：程序图标
