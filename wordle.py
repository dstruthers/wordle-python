from dataclasses import dataclass, field
from enum import Enum
import functools
import re

class Hint(Enum):
    YES = 1
    MOVE = 2
    NO = 3


def system_word_list() -> list[str]:
    """
    Return all five-letter words from the system dictionary file, excluding proper nouns and punctuation.
    """
    with open('/usr/share/dict/words', 'r') as f:
        return [w.strip() for w in f.readlines() if re.match(r'^[a-z]{5}$', w)]


def letter_frequencies(words: list[str]) -> dict[str, int]:
    """
    Given a list of words, return a mapping of how frequently each letter of the alphabet occurs
    at least once in a word.
    """
    frequency_map = {}
    for word in words:
        for letter in set(word):
            if letter in frequency_map.keys():
                frequency_map[letter] += 1
            else:
                frequency_map[letter] = 1
    return frequency_map
    
    
@dataclass
class Game:
    """Representation of a Wordle session."""
    solution: str
    responses: list[tuple[Hint, str]] = field(default_factory=list)
    guess_limit: int = 6
    word_bank: list[str] = field(default_factory=system_word_list)
    solved: bool = False

    def next_guess(self) -> str:
        """Return the best next guess based on the current word bank."""
        freqs = letter_frequencies(self.word_bank)
        
        def score(word: str) -> int:
            return functools.reduce(lambda a, b: a + b, [freqs[letter] for letter in set(word)])
        
        score_map = [(word, score(word)) for word in self.word_bank]
        return functools.reduce(lambda a, b: a if a[1] > b[1] else b, score_map)[0]

    
    def respond(self, guess) -> list[tuple[Hint, str]]:
        """Provide a hint based on a guess and the solution."""
        def evaluate(g: str, s: str) -> tuple[Hint, str]:
            if g == s:
                return (Hint.YES, g)
            elif self.solution.find(g) > -1:
                return (Hint.MOVE, g)
            else:
                return (Hint.NO, g)
            
        return [evaluate(g, s) for (g, s) in zip(guess, self.solution)]


    def display_response(self, response: list[tuple[Hint, str]]) -> None:
        """Render a response in color using ANSI terminal codes."""
        for hint, letter in response:
            if hint == Hint.YES:
                print('\033[32m{}\033[0m'.format(letter.upper()), end='')
            elif hint == Hint.MOVE:
                print('\033[33m{}\033[0m'.format(letter.upper()), end='')
            else:
                print(letter.upper(), end='')
        print('')


    def pare_word_bank(self, response: list[tuple[Hint, str]]) -> None:
        """Eliminate invalid words from the word bank based on the latest hint."""
        for i in range(len(response)):
            hint, letter = response[i]
            if hint == Hint.YES:
                self.word_bank = [word for word in self.word_bank if word[i] == letter]
            elif hint == Hint.MOVE:
                self.word_bank = [word for word in self.word_bank if word.find(letter) > -1]
            elif hint == Hint.NO:
                self.word_bank = [word for word in self.word_bank if word.find(letter) == -1]

    
    def play(self) -> None:
        """Attempt to find the provided solution using up to 6 guesses."""
        while not self.solved:
            guess = self.next_guess()
            response = self.respond(guess)
            self.display_response(response)
            self.responses.append(response)
            self.solved = functools.reduce(lambda a, b: a and b, [True if h == Hint.YES else False for (h, _) in response])

            if self.solved:
                print('Success in {}/{}'.format(len(self.responses), self.guess_limit))
                break
            elif len(self.responses) == self.guess_limit:
                print('Failure')
                break

            self.pare_word_bank(response)
            

def main() -> None:
    # Example usage
    Game('abbey').play()

    
if __name__ == '__main__':
    main()
