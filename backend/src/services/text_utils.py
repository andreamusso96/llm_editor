import re
from typing import List, Tuple
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
    

def locate_snippet_in_segment(segment_text: str, segment_global_start_offset: int, snippet: str, sentence_context: str) -> Tuple[int, int]:
    try: 
        # TODO: If there the same sentence has twice an error with the same original snippet, this will not work.
        # We will attribute both errors to the first occurence of the original snippet. This is a minor issue for now. But we should fix it.
        full_sentence_context_start_pos = segment_text.find(sentence_context)
        full_sentence_context_end_pos = full_sentence_context_start_pos + len(sentence_context)

        if full_sentence_context_start_pos == -1:
            snippet_start_pos = segment_text.find(snippet)
            snippet_end_pos = snippet_start_pos + len(snippet)
        else:
            full_sentence_context = segment_text[full_sentence_context_start_pos:full_sentence_context_end_pos]
            snippet_start_pos = full_sentence_context_start_pos + full_sentence_context.find(snippet)
            snippet_end_pos = snippet_start_pos + len(snippet)
        
        if snippet_start_pos == -1:
            logger.warning(f"Original snippet not found in user submission: {sentence_context}")
            return -1, -1
        
        global_snippet_start_pos = segment_global_start_offset + snippet_start_pos
        global_snippet_end_pos = segment_global_start_offset + snippet_end_pos

        return global_snippet_start_pos, global_snippet_end_pos

    except ValueError:
        logger.warning(f"Snippet {snippet} not found in segment: {segment_text}")
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