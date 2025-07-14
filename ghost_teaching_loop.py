import os
from dotenv import load_dotenv
import openai
from odds_reverse_engineering.utils.teacher_student_memory import TeacherStudentMemory
from datetime import datetime

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env!")

client = openai.OpenAI(api_key=api_key)
memory = TeacherStudentMemory()

def ghost_openai_wrapper(prompt, tags=None, model='gpt-3.5-turbo', max_tokens=512, temperature=0.2):
    """
    Central teacher-student wrapper for all OpenAI calls.
    Checks memory first, calls OpenAI if needed, archives with tags.
    Tags can include: sport, type, context, file, etc.
    """
    # 1. Check memory first
    answer = memory.get_answer(prompt)
    if answer:
        print("[GhostAI] Answer from memory.")
        return answer
    # 2. Call OpenAI if not found
    try:
        print("[GhostAI] Calling OpenAI API...")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        content = response.choices[0].message.content or ""
        # 3. Save to memory with tags
        full_tags = tags.copy() if tags else {}
        full_tags['model'] = model
        full_tags['date'] = datetime.now().strftime('%Y-%m-%d')
        memory.save_answer(prompt, content, tags=full_tags)
        print("[GhostAI] Answer saved to memory.")
        return content
    except Exception as e:
        print(f"[GhostAI] OpenAI API call failed: {e}")
        return ""

def rate_ghost_answer(prompt, rating):
    """Rate a memory answer as 'good', 'bad', or 'uncertain'."""
    memory.rate_answer(prompt, rating)
    print(f"[GhostAI] Rated answer for prompt as {rating}.") 