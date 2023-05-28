import json

class Text:
    def __init__(self, text, start_timestamp, duration):
        self.text = text
        self.timestamp = start_timestamp
        self.duration = duration

class Element:
    def __init__(self, subtitles, timestamp):
        index = 0
        # get element by timestamp
        for i in subtitles.texts:
            if i.timestamp+i.duration > timestamp:
                self.text = i.text
                self.dist_from_start = timestamp-i.timestamp
                self.dist_from_end = i.timestamp+i.duration-timestamp
                self.index = index
                break
            index += 1

class Subtitles:
    def __init__(self, subtitle:list):
        self.texts = []
        self.duration = 0

        for i in subtitle:
            self.texts.append(Text(i['text'], self.duration, i['duration']))
            self.duration += i['duration']

    def get_element(self, timestamp):
        if timestamp >= self.duration:
            return None
        else:
            return Element(self, timestamp)

# function to load subtitles from json
def load_from_json(path):
    with open(path, encoding='utf-8') as f:
        return Subtitles(json.load(f))