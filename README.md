
# Code2PDF

`Code2PDF` 是一个 Python 脚本，它将一个项目目录中的文件树结构和文件内容转换为 PDF。该工具能够遍历项目目录，生成其树结构，并将每个文件的内容写入 PDF 文档中。

## 功能概述

- **目录树生成**：构建项目目录树并将其写入 PDF。
- **文件内容转换**：将项目中的代码文件逐行读取并写入 PDF。
- **自定义字体支持**：使用 `DejaVuSansMono` 字体来确保一致的代码显示格式。
- **分页处理**：自动处理页面换行和分页。

## 依赖

- Python 3.x
- [ReportLab](https://www.reportlab.com/opensource/) 库用于生成 PDF 文档

可以通过以下命令安装所需依赖：

pip install reportlab


## 使用方法

### 运行脚本

通过命令行运行脚本，指定项目目录和输出 PDF 文件名：


python code2pdf.py <project_directory> <output_pdf>


- `<project_directory>`：要转换的项目目录的路径。
- `<output_pdf>`：输出的 PDF 文件名。

例如：

python code2pdf.py ./my_project output.pdf


### 示例

假设你有一个项目目录结构如下：


my_project/
    ├── main.py
    ├── utils.py
    └── README.md


运行以下命令：

python code2pdf.py ./my_project my_project.pdf


脚本将生成一个 `my_project.pdf` 文件，其中包含项目的目录结构和文件内容。

## 字体设置

脚本使用了 `DejaVuSansMono` 字体格式来确保代码格式的正确显示。你需要确保该字体文件（`DejaVuSansMono.ttf`）存在于与脚本相同的目录下。如果字体文件缺失，脚本将无法运行并提示错误信息。

## 脚本详细功能说明

- `register_custom_font(font_path)`：注册自定义字体（`DejaVuSansMono.ttf`），使得 PDF 文档中的文本使用该字体。
- `filter_directories(dirs)`：过滤掉以 `.` 开头的隐藏目录和 `__pycache__` 目录。
- `build_directory_tree(root_dir)`：遍历指定目录，生成目录树结构，并收集所有文件的相对路径。
- `write_directory_tree_to_pdf(c, dir_tree, font_name, font_size, text_pos)`：将目录树写入 PDF。
- `write_files_to_pdf(c, root_dir, file_paths, font_name, font_size, text_pos)`：将各个文件的内容写入 PDF。
- `main()`：主函数，负责解析命令行参数、生成 PDF 并调用各个功能模块。

## 注意事项

- 该脚本适用于包含文本文件的项目目录，非文本文件可能会导致读取错误。
- 确保 `DejaVuSansMono.ttf` 字体文件与脚本位于同一目录下。
- PDF 生成过程中会自动分页，当页面内容超过当前页时，脚本会自动创建新页。

## 错误处理

如果在读取文件内容时发生错误，例如由于文件编码问题，脚本会在 PDF 中记录错误信息，并继续处理其他文件。

## 许可证

该项目采用 MIT 许可证。详细内容请参阅 [LICENSE](LICENSE) 文件。