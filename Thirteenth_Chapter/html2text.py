#!/usr/bin/python3


import re
import html.entities


def html2text(html_text):
    def char_from_entity(match):
        code = html.entities.codepoint2name.get(match.group(1), 0xFFFD)
        return chr(code)

    text = re.sub(r'<!--.*?-->', '', html_text, flags=re.DOTALL)
    text = re.sub(r'<[Pp][^>]*?>', '\n\n', text)
    text = re.sub(r'<[^>]*?>', '', text)
    text = re.sub(r'&#(\d+);', lambda x: chr(int(x.group(1))), text)
    text = re.sub(r'&([A-Za-z]+);', char_from_entity, text)
    text = re.sub(r'\n(?:[ \xA0\t]+\n)+', '\n', text)
    return re.sub(r'\n\n+', '\n\n', text.strip())
