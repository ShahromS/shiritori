import random
from flask import Flask, request, jsonify

app = Flask(__name__)

# Список уже использованных слов (глобально для текущей сессии приложения)
used_words = set()

# Базовый список слов для しりとり
word_list = ["りんご", "ごま", "まめ", "めがね", "ねこ", "こま", "まり", "りす"]


def get_next_word(last_char):
    """
    Выбирает слово, начинающееся на указанную букву, 
    которое ещё не было использовано.
    """
    candidates = [
        word for word in word_list
        if word.startswith(last_char) and word not in used_words
    ]
    return random.choice(candidates) if candidates else None


@app.route("/", methods=["POST"])
def webhook():
    global used_words

    data = request.get_json(silent=True, force=True)
    if not data:
        return jsonify({"fulfillmentText": "Нет данных от DialogFlow."})

    # Извлекаем название Intenta, чтобы понять, какой сценарий запускать
    intent_name = data.get("queryResult", {}).get("intent", {}).get("displayName", "")

    # Обработка разных Intents в зависимости от intent_name
    if intent_name == "Default Welcome Intent":
        # Простой ответ на приветствие
        return jsonify(
            {"fulfillmentText": "Привет! Я готов сыграть в しりとり. Скажи 'Начать игру', чтобы стартовать!"})

    elif intent_name == "StartShiritoriIntent":
        # Начинаем игру, сбрасывая использованные слова и даём начальное сообщение
        used_words.clear()
        return jsonify({"fulfillmentText": "Игра начинается! Скажи любое слово на японском, чтобы начать しりとり."})

    else:
        # Предположим, что остальные фразы — часть игрового процесса しりとり
        user_word = data.get("queryResult", {}).get("queryText", "").strip()

        if not user_word:
            return jsonify({"fulfillmentText": "Я не услышал от тебя слова. Попробуй снова."})

        # Проверяем, не было ли это слово уже использовано
        if user_word in used_words:
            return jsonify({"fulfillmentText": "Это слово уже использовано! Попробуй другое."})

        # Добавляем слово пользователя в использованные
        used_words.add(user_word)

        # Определяем последнюю букву
        last_char = user_word[-1]
        # Находим следующее слово
        next_word = get_next_word(last_char)

        # Если есть подходящее слово
        if next_word:
            used_words.add(next_word)
            return jsonify({"fulfillmentText": f"{next_word}！Теперь твой ход!"})
        else:
            # Если нет подходящего слова
            return jsonify({"fulfillmentText": "Я не могу придумать слово... Ты победил! 🎉"})


if __name__ == "__main__":
    # Запускаем приложение на 0.0.0.0:8080
    # Контейнер или хост с ngrok будет слушать этот порт
    app.run(host="0.0.0.0", port=8080)