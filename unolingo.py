import random

class UnoLingoManager:
    def __init__(self) -> None:
        self.words_english = []
        self.words_polish = []
        self.dict_english = {}
        self.dict_polish = {}

    def load_words_from_file(self, filename, weight=1):
        print(f"Loading from {filename}...")
        # fetching translated pairs
        words = []
        with open(filename, "r", encoding="utf-8") as f:
            words = [word.strip() for word in f.readlines()]

        # processing pairs
        for pair in words:
            eng, pls = pair.split(' - ')
            pl = pls.split(', ')

            # adding words
            for w in range(weight):
                self.words_english.append(eng)
                for pl_word in pl: self.words_polish.append(pl_word)
            
            # creating translation map
            if eng not in self.dict_english.keys():
                self.dict_english[eng] = pls
            for pl_word in pl:
                if pl_word not in self.dict_polish.keys():
                    self.dict_polish[pl_word] = eng

        print(len(self.words_english), len(self.words_polish))

    def load_words(self):
        self.words_english = []
        self.words_polish = []
        self.dict_english = {}
        self.dict_polish = {}
        
        self.load_words_from_file("hard.txt", 5)
        self.load_words_from_file("translated.txt")

    def shuffle(self):
        self.shuffled = self.words_english + self.words_polish
        random.shuffle(self.shuffled)

    def print_random_pair(self):
        random_eng = self.words_english[random.randint(0, len(self.words_english)-1)]
        print(f"Random pair: {random_eng} - {self.dict_english[random_eng]}")

uno = UnoLingoManager()
uno.load_words()
uno.print_random_pair()
uno.print_random_pair()
uno.print_random_pair()