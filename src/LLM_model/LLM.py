from yandex_cloud_ml_sdk import YCloudML
import json
import os
import re

# Параметры авторизации
folder_id = 'b1gst3c7cskk2big5fqn'
api_key = os.getenv("YCLOUD_TOKEN")

# Инициализация клиента
sdk = YCloudML(folder_id=folder_id, auth=api_key)
model = sdk.models.completions(f'gpt://{folder_id}/llama')

input_JSON = '/prompts/'

# Пример входных данных — список ходов
#moves_input = [
#    {"move": "e4", "start_time": "00:01.115", "end_time": "00:02.679"},
#    {"move": "c5", "start_time": "00:02.700", "end_time": "00:03.120"},
#    {"move": "Nf3", "start_time": "00:03.150", "end_time": "00:04.000"},
#    {"move": "d6", "start_time": "00:04.050", "end_time": "00:05.000"},
#]

#def time_to_seconds(timestr):
#    """Преобразует время в формате mm:ss.mmm в секунды (float)"""
#    match = re.match(r"(\d+):(\d+)\.(\d+)", timestr)
#    if not match:
#        return 0.0
#    minutes, seconds, millis = match.groups()
#    return int(minutes) * 60 + int(seconds) + int(millis) / 1000

#def extract_time_bounds(moves):
#    """Извлекает минимальное и максимальное время из списка ходов"""
#    start_times = [time_to_seconds(m["start_time"]) for m in moves]
#    end_times = [time_to_seconds(m["end_time"]) for m in moves]
#    return min(start_times), max(end_times)

# Промт, который будет отправлен в модель
with open(input_JSON) as f:
    chess = json.load(f)

prompt = f"""
You are a chess analyst. I will provide you with a chess game in JSON format. Each element in the array represents a move and contains:
- "move" — the move in standard algebraic notation,
- "start_time" and "end_time" — the timestamp of that move in the video.

Your task is to identify and return only a few key or interesting moments from the game. Each moment should be surrounded by 3 moves before and 3 moves after, and those surrounding moves must not contain any comments.

Return the moments in the following JSON format:
- The key is the full move number where the moment begins (e.g., "7"). Only one moment per key.
- The value is an array of moves, where each move includes:
  - "move"
  - "start_time"
  - "end_time"
  - "comment" — leave this field empty for context moves.
    - The main move (the highlight) should have a brief but meaningful comment in Russian (2–3 sentences) including:
      - Which piece made the move (in English notation),
      - Which square it moved to,
      - Why this move is interesting (e.g., sacrifice, check, mate, blunder, opening idea, tactic, etc.). Mention the name of the opening or motif if relevant.

Types of interesting moments (in priority order):
1. Quick checkmate
2. Recognizable opening sequence (4–6 moves) — with opening name
3. Prepared sacrifices
4. Winning an important piece (especially the queen)
5. Series of checks
6. Unusual opening moves
7. Time trouble or sharp acceleration in tempo
8. Tactical shots in middlegame or endgame
9. Pawn delivering mate
10. Final decisive attack (mate, resignation, time loss)

Mandatory inclusions:
- A complete opening sequence with its name, if recognizable
- A final segment, if it ends the game and contains a key idea

Number of moments:
- If the game has ≥ 20 full moves — select 3–6 such moments
- If < 20 — select 1–4 moments

Do not include:
- Isolated moves without tactical context
- Standard development moves (e.g., a3, h6, d6) unless part of a key idea
- Castling unless it's part of a combination
- Comments for non-highlight moves

Output format:
"7": [
  
    "move": "Nf3",
    "start_time": "00:10",
    "end_time": "00:12",
    "comment": ""
  ,
  ...
  
    "move": "Qh5",
    "start_time": "00:28",
    "end_time": "00:30",
    "comment": "The queen goes to h5, threatening to mate on f7 — a classic move in the bishop's opening."
  ,
  ...
  
    "move": "Nc6",
    "start_time": "00:35",
    "end_time": "00:37",
    "comment": ""
  
]

One key = one moment. Comments should only be inside the JSON and written in English, meaningful and chess-relevant. No explanations outside the JSON.
{chess}
"""
print(f"Promt:\n{prompt}\n\n")
def main():
    # Извлекаем временные границы
#   min_time, max_time = extract_time_bounds(moves_input)
#    print(f"🕐 Партия начинается в {min_time:.3f} сек, заканчивается в {max_time:.3f} сек")

    # Запрос к модели
    response = model.run(prompt)

    try:
        result_json = json.loads(response.text)
        print(json.dumps(result_json, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print("❌ Не удалось распарсить JSON. Ответ модели:")
        print(response.text)

if __name__ == "__main__":
    main()
