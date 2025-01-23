from typing import Union
from pathlib import Path

from base import DocumentConverter, DocumentConverterResult, FileConversionException


class PdfConverter(DocumentConverter):
    """默认PDF解析器（simple模式，基于pdfminer）"""

    def convert(self, local_path: str, **kwargs) -> Union[None, DocumentConverterResult]:
        # Bail if not a pdf
        extension = kwargs.get("file_extension", "")
        if extension.lower() != ".pdf":
            return None
        try:
            import pdfminer.high_level
            return DocumentConverterResult(
                title=None,
                text_content=pdfminer.high_level.extract_text(local_path)
            )
        except Exception as e:
            raise FileConversionException(f"Simple PDF解析失败: {str(e)}")


class AdvancedPdfConverter(DocumentConverter):
    """使用mineru的增强PDF解析器（advanced模式）"""

    def convert(self, local_path: str, **kwargs) -> DocumentConverterResult:
        # Bail if not a pdf
        extension = kwargs.get("file_extension", "")
        if extension.lower() != ".pdf":
            return None

        try:
            from converters.mineru.pdf_processor import PDFProcessor
            processor = PDFProcessor()
            result = processor.process(local_path)
            
            # 读取生成的markdown文件
            with open(result["markdown"], "r", encoding="utf-8") as f:
                md_content = f.read()
                
            return DocumentConverterResult(
                title=Path(local_path).stem,
                text_content=md_content
            )
        except ImportError:
            raise RuntimeError("miner模块未找到，请安装mineru解析器")
        except Exception as e:
            raise FileConversionException(f"Advanced PDF解析失败: {str(e)}")


class CloudPdfConverter(DocumentConverter):
    """云端PDF解析器（预留cloud模式实现）"""

    def convert(self, local_path: str, **kwargs) -> DocumentConverterResult:
        # Bail if not a pdf
        extension = kwargs.get("file_extension", "")
        if extension.lower() != ".pdf":
            return None
        raise NotImplementedError("Cloud模式尚未实现")

