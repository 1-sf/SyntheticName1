import re

import re

def remove_numbering(entity):
    pattern = r'^\d+\.\s+'
    clean_entity = re.sub(pattern, '', entity)
    return clean_entity

def get_words_in_parenthesis(text):
    pattern = r'\((.*?)\)'
    matches = re.findall(pattern, text)
    return matches

def parse_entities_promptner(output):
    entities = []
    for line in output.splitlines():
        try:
            parts = line.split("|")
            entity = remove_numbering(parts[0].strip())
            is_entity = parts[1].strip() == "True"
            reasoning = parts[2].strip()
            tag = get_words_in_parenthesis(reasoning)[0]
            entities.append((entity, is_entity, reasoning, tag))
        except:
            continue
    return entities

def get_token_labels(text, entities, label2index):
    text = text.lower().replace("( ", "(").replace(" )", ")")

    labels = ["O"] * len(text.split())
    for entity_info in entities:
        if not entity_info[1]:
            continue
        
        entity = entity_info[0].lower()
        tag = entity_info[3]
        if tag == "organization":
            tag = "organisation"
        if tag == "people":
            tag = "person"
        if "/" in tag:
            tag = tag.split("/")[0]
        if "or" in tag:
            tag = tag.split("or")[0]
        if ", " in tag:
            tag = tag.split(", ")[0]

        start = text.find(entity)
        end = start + len(entity)

        start_word = len(text[:text.find(" ", start)].split()) - 1
        end_word = len(text[:min(len(text), text.find(" ", end))].split())

        for i in range(start_word, end_word):
            if i == start_word:
                labels[i] = "B-" + tag
            else:
                labels[i] = "I-" + tag
    return [int(label2index[label]) for label in labels]