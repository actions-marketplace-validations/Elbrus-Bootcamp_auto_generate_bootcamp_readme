import os
import re
from googleapiclient.discovery import build

# === Настройки ===
PLAYLIST_ID = os.getenv("PLAYLIST_ID")
API_KEY = os.getenv("API_KEY")
README_PATH = "README.md"

# === Вспомогательные функции ===

def get_youtube_videos():
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=PLAYLIST_ID,
        maxResults=50
    )
    response = request.execute()

    print("Ответ от YouTube API:", response)

    videos = {}
    for item in response["items"]:
        title = item["snippet"]["title"]
        match = re.match(r"[pP](\d+)[wW](\d+)[dD](\d+)\s*-\s*(.+)", title, re.IGNORECASE)
        if match:
            p, w, d, topic = match.groups()
            key = f"p{p}w{w}d{d}"
            videos[key] = f"https://youtu.be/{item['snippet']['resourceId']['videoId']}"
            print(f"✅ Распознано видео: {title} -> {key}")
        else:
            print(f"❌ Видео не совпадает с шаблоном: {title}")

    return videos

def generate_course_structure(videos):
    content = ""
    phases = [p for p in os.listdir() if p.startswith("phase-")]

    for phase in sorted(phases, key=lambda x: int(x.split('-')[1])):
        phase_num = phase.replace("phase-", "")
        content += f"<!-- BEGIN PHASE {phase_num} -->\n"
        content += f"<details>\n  <summary>🔽 <strong>ФАЗА {phase_num}</strong> (развернуть)</summary>\n\n"

        weeks = sorted(
            [w for w in os.listdir(phase) if w.startswith("week-")],
            key=lambda x: int(x.split('-')[1])
        )

        for week in weeks:
            week_num = week.replace("week-", "")
            content += f"## 📅 Неделя {week_num}\n<details>\n  <summary>▶️ Развернуть неделю</summary>\n\n### 📋 Темы\n"

            topics_path = os.path.join(phase, week)
            print(f"Сканирование папки: {topics_path}")
            print(f"Содержимое: {os.listdir(topics_path)}")
            topics = sorted(
                [
                    t for t in os.listdir(topics_path)
                    if os.path.isdir(os.path.join(topics_path, t)) and re.match(r"^\d+", t)
                ],
                key=lambda x: int(re.match(r"^\d+", x).group())
            )
            print(f"Отфильтрованные темы: {topics}")

            for topic in topics:
                topic_path = os.path.join(phase, week, topic)
                match = re.match(r"^(\d+)", topic)
                topic_day = match.group(1) if match else "0"
                topic_title = re.sub(r"^\d+[-_]", "", topic).replace("-", " ").title()

                topic_key = f"p{phase_num}w{week_num}d{topic_day}"
                code_link = f"[code]({topic_path}/code)"
                slides = [f for f in os.listdir(topic_path) if f.endswith((".pptx", ".pdf")) and os.path.isfile(os.path.join(topic_path, f))]
                slide_link = f"[Скачать]({os.path.join(topic_path, slides[0])})" if slides else "—"

                yt_link = videos.get(topic_key, "—")
                yt_cell = f"<a href='{yt_link}' target='_blank'>Ссылка на YouTube</a>" if yt_link != "—" else "—"

                content += f"#### 🔹 {topic_title}\n"
                content += "| <span style=\"color:#4CAF50\">📁 Код</span> | <span style=\"color:#FFA726\">📄 Презентация</span> | <span style=\"color:#2196F3\">🎥 Запись</span> |\n"
                content += "|------------------------------------------|--------------------------------------------------|---------------------------------------------|\n"
                content += f"| {code_link} | {slide_link} | {yt_cell} |\n\n---\n\n"

            content += "</details>\n\n"

        content += f"</details>\n<!-- END PHASE {phase_num} -->\n\n"

    return content

def update_readme():
    videos = get_youtube_videos()
    generated_content = generate_course_structure(videos)

    with open(README_PATH, "r", encoding="utf-8") as f:
        old_content = f.read()

    # Удаляем старые секции фаз
    new_content = re.sub(
        r"<!-- BEGIN PHASE.*?-->.*?<!-- END PHASE.*-->",
        "",
        old_content,
        flags=re.DOTALL
    )

    # Удаляем старое сгенерированное содержимое
    new_content = re.sub(
        r"<!-- BEGIN GENERATED CONTENT -->.*?<!-- END GENERATED CONTENT -->",
        "",
        new_content,
        flags=re.DOTALL
    )

    # Извлекаем только секцию "Дополнительные материалы"
    additional_content = ""
    match = re.search(r"## 📎 Дополнительные материалы.*", new_content, re.DOTALL)
    if match:
        additional_content = match.group(0)

    # Формируем итоговое содержимое
    final_content = (
        "# 📚 Навигация по репозиторию\n\n"
        "<!-- BEGIN GENERATED CONTENT -->\n"
        + generated_content
        + "<!-- END GENERATED CONTENT -->\n\n"
        + additional_content
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(final_content)

if __name__ == "__main__":
    update_readme()