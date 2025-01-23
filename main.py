# SPDX-FileCopyrightText: 2024-present Adam Fourney <adamfo@microsoft.com>
#
# SPDX-License-Identifier: MIT
import argparse
import sys
from textwrap import dedent
from __about__ import __version__
from _markitdown import MarkItDown, DocumentConverterResult
from model_manager import ModelConfigurator


def create_parser():
    """创建无冲突参数解析器"""
    parser = argparse.ArgumentParser(
        description="Markdown转换工具（集成模型管理）",
        prog="markitdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage=dedent("""
            语法:
              markitdown [选项] [输入文件]

            示例:
              # 基本使用
              markitdown input.pdf -o output.md

              # 使用GPU加速
              markitdown input.pdf --device cuda:0

              # 自定义模型路径
              markitdown input.pdf --models-dir ~/my_models

              # 使用ModelScope源
              markitdown input.pdf --use-modelscope
            """).strip(),
        add_help=False  # 关键点：禁用默认help
    )

    # 核心参数
    parser.add_argument(
        '-h', '--help',
        action='help',  # 使用内置help action
        default=argparse.SUPPRESS,
        help='显示帮助信息'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}',
        help='显示版本信息'
    )
    parser.add_argument(
        'filename',
        nargs='?',
        help='输入文件路径（可选，可从stdin读取）'
    )
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='输出文件路径（默认输出到stdout）'
    )

    # 模型配置参数组
    model_group = parser.add_argument_group('模型配置')
    model_group.add_argument(
        '--device',
        default='cpu',
        choices=['cpu', 'mps', 'cuda', 'cuda:0', 'cuda:1'],
        help='计算设备选择（默认：%(default)s）'
    )
    model_group.add_argument(
        '--models-dir',
        metavar='PATH',
        help='自定义模型存储路径（默认：~/.markitdown_models）'
    )
    model_group.add_argument(
        '--use-modelscope',
        action='store_true',
        help='使用ModelScope下载模型（默认使用HuggingFace Hub）'
    )

    # PDF处理参数组
    pdf_group = parser.add_argument_group('PDF处理')
    pdf_group.add_argument(
        '--pdf-mode',
        default='simple',
        choices=['simple', 'advanced', 'cloud'],
        help='PDF处理模式（默认：%(default)s）'
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        # 初始化模型配置
        configurator = ModelConfigurator(
            device=args.device,
            models_dir=args.models_dir,
            use_modelscope=args.use_modelscope
        )
        configurator.setup_environment()

        # 执行主逻辑
        if args.filename is None:
            markitdown = MarkItDown(pdf_mode=args.pdf_mode)
            result = markitdown.convert_stream(sys.stdin.buffer)
        else:
            markitdown = MarkItDown(pdf_mode=args.pdf_mode)
            result = markitdown.convert(args.filename)

        _handle_output(args, result)

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


def _handle_output(args, result: DocumentConverterResult):
    """处理输出"""
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result.text_content)
    else:
        print(result.text_content)


if __name__ == "__main__":
    main()
