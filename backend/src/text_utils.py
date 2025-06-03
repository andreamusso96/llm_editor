import re
from typing import Optional, List, Tuple
from src.utils import logger

def split_text_into_paragraphs(text: str) -> List[Tuple[str, int]]:
    """
    Splits a given text into paragraphs based on blank lines (one or more empty
    or whitespace-only lines) and returns each paragraph with its starting
    character offset in the original text.

    Args:
        text: The input string.

    Returns:
        A list of tuples, where each tuple is (paragraph_text, start_offset).
    """
    paragraphs_with_offsets: List[Tuple[str, int]] = []
    if not text.strip():
        return []
    
    start_offset = 0
    while start_offset < len(text):
        # Find the end of the current paragraph
        # A paragraph ends before two or more newlines, or at the end of the text.
        end_of_paragraph_marker = re.search(r'\n\s*\n', text[start_offset:])
        
        if end_of_paragraph_marker:
            # The paragraph text ends where the marker begins.
            # The marker itself indicates the separation.
            para_end_offset_in_slice = end_of_paragraph_marker.start()
            paragraph_text = text[start_offset : start_offset + para_end_offset_in_slice]
            
            # The next paragraph will start after the marker.
            # The marker is text[start_offset + para_end_offset_in_slice : start_offset + end_of_paragraph_marker.end()]
            next_para_start_offset = start_offset + end_of_paragraph_marker.end()
        else:
            # No more double newlines, so the rest of the text is the last paragraph
            paragraph_text = text[start_offset:]
            next_para_start_offset = len(text) # End of text

        # Add paragraph if it's not just whitespace
        # However, for your use case, you might want to preserve paragraphs that are
        # just whitespace if the LLM could comment on them or if it affects numbering.
        # For now, let's strip and check if non-empty.
        trimmed_paragraph = paragraph_text.strip()
        if trimmed_paragraph: # Only add non-empty paragraphs
            paragraphs_with_offsets.append((paragraph_text, start_offset)) # Store original paragraph text
        elif paragraph_text:
            pass


        start_offset = next_para_start_offset

    return paragraphs_with_offsets


def locate_snippet_in_segment(segment_text: str, segment_global_start_offset: int, snippet: str) -> Tuple[int, int]:
    """
    Locates a snippet within a given text segment and returns its global
    start and end character offsets relative to the original full document.

    Args:
        segment_text: The text segment (e.g., a paragraph or the full document)
                      in which the snippet is expected to be found.
        segment_global_start_offset: The starting character offset of 'segment_text'
                                     within the overall original document. (This is 0
                                     if segment_text is the full original document).
        snippet: The snippet string to locate.

    Returns:
        A tuple (global_start_char, global_end_char). Returns (-1, -1) if not found.
    """
    if not snippet:
        logger.warning("Attempted to locate an empty snippet.")
        return -1, -1

    try:
        local_start_char = segment_text.find(snippet)

        if local_start_char != -1:
            global_start_char = segment_global_start_offset + local_start_char
            global_end_char = global_start_char + len(snippet)
            
            # Optional: A quick sanity check if you have access to the original_full_text here
            # This function's philosophy is that it trusts segment_text and its offset.
            # The caller (task) can do a final sanity check against original_full_text if desired.
            logger.debug(f"Snippet '{snippet[:30]}...' located at local:{local_start_char}, global:[{global_start_char}:{global_end_char}]")
            return global_start_char, global_end_char
        else:
            logger.warning(f"Snippet '{snippet[:100]}...' not found in the provided segment_text (length {len(segment_text)}). Segment starts with: '{segment_text[:100]}...'")
            return -1, -1
    except Exception as e:
        logger.exception(f"Error during snippet location in segment: {e}")
        return -1, -1


if __name__ == "__main__":
    text = """
    This is a test.
    This is a test.

    This is a test.
    This is a test. Beljfheljrh

    This is a test.
    This is a test.

    This is a test.
    This is a test.
    """

    print(split_text_into_paragraphs(text))

    print(locate_snippet_in_segment(text, 0, "Beljfheljrh."))