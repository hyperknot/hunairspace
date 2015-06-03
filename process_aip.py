#!/usr/bin/env python

from pgairspace.hun_aip import process_chapters, process_airports

process_chapters()
process_airports()


from pgairspace.hun_aip import process_chapter

data = process_chapter('2.1')
