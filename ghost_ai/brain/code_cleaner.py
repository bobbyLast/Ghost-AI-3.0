import os
from pathlib import Path
from datetime import datetime
from ghost_teaching_loop import ghost_openai_wrapper, rate_ghost_answer
from odds_reverse_engineering.utils.teacher_student_memory import TeacherStudentMemory

memory = TeacherStudentMemory()

def clean_code_file(filepath, reason, suggest_only=True):
    """
    Cleans and optimizes a code file using OpenAI and the teacher-student memory system.
    Archives before/after code, fix reason, and OpenAI explanation in memory.
    If suggest_only is True, only prints the cleaned code and does not overwrite the file.
    """
    path = Path(filepath)
    if not path.exists():
        print(f"[CodeCleaner] File not found: {filepath}")
        return
    with open(path, 'r', encoding='utf-8') as f:
        original_code = f.read()
    prompt = (
        f"Clean up this code. Remove unused functions/imports, refactor bloated parts, and optimize logic for clarity and speed. "
        f"Reason: {reason}\n\n" + original_code
    )
    tags = {
        'type': 'code_clean',
        'file': str(filepath),
        'reason': reason,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    cleaned_code = ghost_openai_wrapper(prompt, tags=tags, model='gpt-3.5-turbo', max_tokens=2048)
    # Archive before/after and OpenAI explanation
    memory.save_answer(
        prompt=f"CLEAN_CODE::{filepath}::{reason}",
        response=cleaned_code,
        tags=tags
    )
    if suggest_only:
        print("[CodeCleaner] --- Cleaned code suggestion ---")
        print(cleaned_code)
        print("[CodeCleaner] --- End suggestion ---")
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)
        print(f"[CodeCleaner] File {filepath} cleaned and overwritten.") 