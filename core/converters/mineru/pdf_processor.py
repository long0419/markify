from pathlib import Path
from typing import Dict

from magic_pdf.config.enums import SupportedPdfParseMethod
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze

from core.converters.mineru.title_corrector import MarkdownTitleProcessor


class PDFProcessor:
    """PDF文档处理管道"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.image_dir = self.output_dir / "images"
        self._prepare_directories()

    def _prepare_directories(self):
        """创建输出目录结构"""
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def process(self, pdf_path: str) -> Dict[str, str]:
        """处理PDF主流程"""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        name_stem = pdf_path.stem
        writers = {
            'image': FileBasedDataWriter(str(self.image_dir)),
            'markdown': FileBasedDataWriter(str(self.output_dir))
        }

        # 读取并解析PDF
        pdf_content = FileBasedDataReader("").read(str(pdf_path))
        dataset = PymuDocDataset(pdf_content)

        # 执行解析流程
        if dataset.classify() == SupportedPdfParseMethod.OCR:
            result = dataset.apply(doc_analyze, ocr=True).pipe_ocr_mode(writers['image'])
        else:
            result = dataset.apply(doc_analyze, ocr=False).pipe_txt_mode(writers['image'])

        # 生成输出文件
        output_files = self._generate_outputs(result, writers, name_stem)

        # 自动修正标题层级
        self._adjust_title_levels(output_files['markdown'])

        return output_files

    def _generate_outputs(self, result, writers, name_stem: str) -> Dict[str, str]:
        """生成所有输出文件"""
        # 生成原始Markdown
        md_file = f"{name_stem}.md"
        result.dump_md(writers['markdown'], md_file, self.image_dir.name)

        # 生成中间文件
        # result.dump_content_list(writers['markdown'], f"{name_stem}_content.json")
        # result.dump_middle_json(writers['markdown'], f"{name_stem}_middle.json")

        return {
            'markdown': str(self.output_dir / md_file),
            'images': str(self.image_dir),
            # 'middle_json': str(self.output_dir / f"{name_stem}_middle.json")
        }

    def _adjust_title_levels(self, md_path: str):
        """执行Markdown标题修正"""
        processor = MarkdownTitleProcessor()
        processor.process_file(md_path)


if __name__ == "__main__":
    # 示例用法
    processor = PDFProcessor()
    result = processor.process("/path/to/your.pdf")
    print(f"处理完成，输出文件：{result}")
