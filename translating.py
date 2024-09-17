import deepl

auth_key = "..."
translator = deepl.Translator(auth_key)

with open("words.txt", "r") as f:
    words = [word.strip() for word in f.readlines()]

with open("translated.txt", "w+", encoding="utf-8") as f:
    for i, word in enumerate(words):
        try:
            print(f"{i}. {word} - ", end="")
            translated = translator.translate_text(word, source_lang="EN", target_lang="PL").text
            print(translated)
            f.write(f"{word}-{translated}\n")
        except Exception as e:
            print(f"Exception: {e}")