# coding: utf-8


def parse_ref(bible_reference='1 John 5:3-5,7-10,14'):
    '''
    >>> parse_ref(' John ') == {'book': 'John'}
    True
    >>> parse_ref(' 1  John ') == {'book': '1 John'}
    True
    >>> parse_ref(' 1  John  3  ') == {'book': '1 John', 'chapter': 3}
    True
    >>> parse_ref(' 1  John  3  :  1 - 3 , 5, 7 - 9  ') == {'book': '1 John', 'chapter': 3, 'verses': '1-3,5,7-9'}
    True
    '''
    book_and_chapter, _, verses = bible_reference.strip().partition(':')
    book, _, chapter = book_and_chapter.strip().rpartition(' ')
    try:
        chapter = int(chapter)
    except ValueError:
        book = book_and_chapter
        chapter = 0
    book = book.strip().replace(' ' * 3, ' ').replace(' ' * 2, ' ')
    book_chapter_and_verses = {'book': book}
    if chapter:
        book_chapter_and_verses['chapter'] = chapter
    verses = verses.replace(' ', '')
    if verses:
        book_chapter_and_verses['verses'] = verses
    return book_chapter_and_verses


def parse_refs(bible_reference='1 John 5:3-5,7-10,14;Mark 7:4-6;8:3-6,10'):
    return [parse_ref(ref) for ref in bible_reference.split(';')]


print(parse_refs())
