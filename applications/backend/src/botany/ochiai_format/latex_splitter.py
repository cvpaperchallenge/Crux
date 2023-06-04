
from typing import Any, List, Optional
from langchain.text_splitter import TextSplitter
import re
from typing import (
    AbstractSet,
    Any,
    Collection,
    List,
    Literal,
    Optional,
    Union,
)


def _split_text(text: str, separator: str, keep_separator: bool) -> List[str]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({separator})", text)
            splits = [_splits[i] + _splits[i + 1] for i in range(1, len(_splits), 2)]
            if len(_splits) % 2 == 0:
                splits += _splits[-1:]
            splits = [_splits[0]] + splits
        else:
            splits = text.split(separator)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]


class LatexSplitter(TextSplitter):
    """
    Split the input text in the same way as RecursiveCharacterTextSplitter, but not based on the text length but on the token length.
    """
    def __init__(
        self,
        encoding_name: str = "gpt2",
        model_name: Optional[str] = None,
        allowed_special: Union[Literal["all"], AbstractSet[str]] = set(),
        disallowed_special: Union[Literal["all"], Collection[str]] = "all",
        **kwargs: Any,
    ):
        """Create a new TextSplitter."""
        super().__init__(**kwargs)
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "Could not import tiktoken python package. "
                "This is needed in order to for TokenTextSplitter. "
                "Please install it with `pip install tiktoken`."
            )

        if model_name is not None:
            enc = tiktoken.encoding_for_model(model_name)
        else:
            enc = tiktoken.get_encoding(encoding_name)
        self._tokenizer = enc
        self._allowed_special = allowed_special
        self._disallowed_special = disallowed_special
        self.separators = [
            # First, try to split along Latex sections
            "\\title{",
            "\n\\author{",
            "\n\\chapter{",
            "\n\\section{",
            "\n\\subsection{",
            "\n\\subsubsection{",
            # Now split by environments
            "\n\\begin{abstract}",
            "\n\\begin{enumerate}",
            "\n\\begin{itemize}",
            "\n\\begin{description}",
            "\n\\begin{list}",
            "\n\\begin{quote}",
            "\n\\begin{quotation}",
            "\n\\begin{verse}",
            "\n\\begin{verbatim}",
            ## Now split by math environments
            "$$",
            # "$",
            # # Now split by the normal type of lines
            # " ",
            "",
        ]

    def _split_latex(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = None
        for i, _s in enumerate(separators):
            if _s == "":
                separator = _s
                break
            if _s in text:
                separator = _s
                new_separators = separators[i + 1 :]
                break

        if separator == "":
            return [text]
        splits = _split_text(text, separator, self._keep_separator)
        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if new_separators is None:
                    final_chunks.append(s)
                else:
                    other_info = self._split_latex(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return final_chunks
    
    def _split_token(self, chunks: str) -> List[str]:
        """Split each incoming latex chunk into multiple chunks based on the token length."""
        splits = []
        for text in chunks:
            input_ids = self._tokenizer.encode(
                text,
                allowed_special=self._allowed_special,
                disallowed_special=self._disallowed_special,
            )
            start_idx = 0
            cur_idx = min(start_idx + self._chunk_size, len(input_ids))
            chunk_ids = input_ids[start_idx:cur_idx]
            while start_idx < len(input_ids):
                splits.append(self._tokenizer.decode(chunk_ids))
                start_idx += self._chunk_size - self._chunk_overlap
                cur_idx = min(start_idx + self._chunk_size, len(input_ids))
                chunk_ids = input_ids[start_idx:cur_idx]
        return splits


    def split_text(self, text: str) -> List[str]:
        latex_chunks = self._split_latex(text, self.separators)
        final_chunks = self._split_token(latex_chunks)
        return final_chunks

    @classmethod
    def from_language(
        cls, **kwargs: Any
    ):
        return cls(**kwargs)