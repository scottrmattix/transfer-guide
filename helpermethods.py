import re
from string import capwords

# method to make course_title strings match those of SIS
# ex: "The intro stars and The galaxies" -> "The Intro Stars and the Galaxies"
# ex: "University Of Texas" -> "University of Texas"
def course_title_format(s):
    pattern = re.compile(r'\b(?:and|or|in|to|the|of)\b', re.IGNORECASE)

    s = s.strip()
    if not s:
        return s

    words = s.split() #split by space
    title_words = []
    if words[0].lower() == "the":
        title_words.append("The") #dont change first word for courses starting with The (they exist for some reason)
        words = words[1:]

    for word in words:
        title_word = capwords(word) #capwords capitalizes first letter of word()
        if pattern.match(word):
            title_word = title_word.lower() #if and,or,in, etc lowercase it
        title_words.append(title_word)
    return ' '.join(title_words)