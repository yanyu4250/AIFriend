from langchain_community.document_loaders import TextLoader, CSVLoader, PyPDFLoader, Docx2txtLoader

_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030']


def load_document(file_path: str, file_type: str):
    if file_type == 'pdf':
        return PyPDFLoader(file_path).load()
    elif file_type == 'docx':
        return Docx2txtLoader(file_path).load()
    elif file_type == 'csv':
        return _load_csv(file_path)
    elif file_type == 'txt':
        return _load_text(file_path)
    elif file_type == 'md':
        try:
            from langchain_community.document_loaders import UnstructuredMarkdownLoader
            return UnstructuredMarkdownLoader(file_path).load()
        except ImportError:
            return _load_text(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")


def _load_csv(file_path):
    for enc in _ENCODINGS:
        try:
            return CSVLoader(file_path, encoding=enc).load()
        except (UnicodeDecodeError, UnicodeError, RuntimeError):
            continue
    raise ValueError(f"无法识别CSV文件编码: {file_path}")


def _load_text(file_path):
    for enc in _ENCODINGS:
        try:
            return TextLoader(file_path, encoding=enc).load()
        except (UnicodeDecodeError, UnicodeError, RuntimeError):
            continue
    raise ValueError(f"无法识别文本文件编码: {file_path}")
