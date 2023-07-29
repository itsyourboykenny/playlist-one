from track import Track
from typing import List
import re
import Levenshtein

class Match():
    def __init__(self) -> None:
        pass

    @staticmethod
    def match(query, list) -> Track:
        for item in list:
            print(f"{query.title} vs {item.title}")
            print(f"{Levenshtein.distance(query.title, item.title)}")
            print(f"{query.artist} vs {item.artist}")
            print(f"{Levenshtein.distance(query.artist, item.artist)}")

    @staticmethod
    def format_search(text: str, mode: int = 0) -> str:
        if mode > 2:
            mode = 2
        text = text.lower()

        if mode == 0:
            text = re.sub(r'[\(\)\[\].]', "", text)
        if mode >= 1:
            text = re.sub(r'\([^()]*\)', "", text)
            text = re.sub(r'\[[^\[\]]*\]', "", text)
        if mode == 2:
            text = text.split("feat.")[0]
        return text.strip()

    @staticmethod
    def choose(query: Track, results: List[Track]) -> Track:
        if results is None:
            return None
        if len(results) < 2:
            return results[0]
        
        is_acapella = False
        is_instrumental = False
        if 'acapella' in query.title.lower():
            is_acapella = True
        elif 'instrumental' in query.title.lower():
            is_instrumental = True
        
        promising: Track = None
        best_score: int = None
        
        for curr in results:
            if not is_acapella and 'acapella' in curr.title.lower():
                continue
            if not is_instrumental and 'instrumental' in curr.title.lower():
                continue

            title = Levenshtein.distance(Match.format_search(query.title.lower(), 0), Match.format_search(curr.title.lower(), 0))
            album = Levenshtein.distance(Match.format_search(query.album.lower(), 0), Match.format_search(curr.album.lower(), 0))
            album_type = 100 if (query.album_type == 0 or query.album_type == 1) and curr.album_type == 2 else 0
            explicit = 100 if curr.explicit != query.explicit else 0
            duration = 0 if curr.duration <= query.duration + 1 and curr.duration >= query.duration - 1 else 100
            score = explicit + album + duration + title + album_type

            if promising == None or score < best_score:
                promising = curr
                best_score = score

        return promising
    