# Ordinary-text corpus

`austen.txt` contains 16,384 bytes of Jane Austen's *Pride and Prejudice* (1813),
starting at the first occurrence of `It is a truth universally acknowledged` in
the UTF-8 text downloaded on 27 October 2026 from
<https://www.gutenberg.org/ebooks/1342.txt.utf-8>.
Catalogue and transcription credits: <https://www.gutenberg.org/ebooks/1342>.
Jane Austen lived 1775-1817. The original novel is public domain; the catalogue
explicitly identifies its text as public domain in the USA. Only the original
novel excerpt is included, without the distributor's header, logo or licence.
This corpus provenance does not grant a software licence for the project.

The generator uses three different circular offsets into the excerpt and repeats
it when a longer text is required. These are related prose windows, not three
independent books. UTF-8 bytes remain bytes. No text decoding or normalization
occurs inside either search. The manifest records SHA-256 for the exact corpus,
text and pattern bytes, so network access is unnecessary for reproduction.
