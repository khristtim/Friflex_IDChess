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
你是一位具有幽默感的国际象棋分析师。我将向你提供一场以 JSON 格式表示的国际象棋对局，其中每步棋包含：
- "move" — 标准代数记法表示的棋步，
- "start_time" 和 "end_time" — 视频中该棋步的时间戳。

你的任务是找出对局中最搞笑、最荒谬或最出乎意料的时刻，并以 JSON 格式返回，这些时刻的格式如下：
- 键是完整的走子编号，
- 值是一个对象，包含以下字段：
  - "move" — 棋步本身，
  - "start_time" 和 "end_time" — 视频中该步的时间戳，
  - "comment" — 简短评论（2–3 行中文），以幽默的语气说明该时刻为何搞笑或离奇。

每条评论应包括：
- 哪个棋子走的（如：皇后、骑士、兵），
- 走到了哪个格子（如：f6、d4），
- 以及为什么这个时刻搞笑或令人惊讶（例如：低级失误、自爆、一步将死、奇怪的牺牲、不合逻辑的决定等）。

示例：“皇后走错进了 d4 的兵口 —— 又悲又搞笑。”

以下情况被认为是搞笑或有趣的（按优先级排序）：
1. 快速将死 —— 尤其是看起来完全像灾难的
2. 明显的失误和错过的将死机会 —— 特别是丢了皇后或被一步将死
3. 奇怪或毫无意义的走子 —— 比如皇后无故走到棋盘边缘
4. 毫无理由的牺牲 —— 直接送出棋子
5. 惊慌失措或时间紧张 —— 走子杂乱无章或重复
6. 连续将军让国王在棋盘上乱跑
7. 兵将死对方 —— 特别是看起来像是羞辱
8. 离奇或荒谬的开局走法 —— 比如一开始就 h4 或 Na3
9. “令人扶额”的瞬间 —— 比如车挂在空位上
10. 任何能让观众发笑的时刻（包括棋子的奇怪互动）

你必须包括：
- 对局的最后一个时刻，如果它很滑稽、尴尬，或为混乱画上一个完美句号 —— 无论是将死、认输，还是超时。
- 给最后一步加一个幽默的评论。

限制：
- 如果对局有 20 步或更多 —— 返回 10 到 15 个最有趣或最奇怪的时刻
- 如果少于 20 步 —— 返回 5 到 10 个时刻
- 如果一个搞笑的时刻需要上下文，你可以加上 2–3 步前奏，但总数必须在限制范围内

不要包括：
- 无聊、常规或纯粹用于发展棋子的走子（如：王车易位、d6、c3、a3），
  除非它们显得非常荒谬或带来奇怪结果。

格式：


  "走子编号": [
    
      "move": "...",
      "start_time": "...",
      "end_time": "...",
      "comment": "..."
    ,
    ...
  ],
  ...


只返回有效的 JSON —— 不要有任何结构外的说明或文本。所有评论必须用中文撰写，并带有幽默或讽刺色彩。
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
