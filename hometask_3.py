import xml.etree.ElementTree as ET
import sqlite3
import logging
import re
import os
import argparse
'''
parser = argparse.ArgumentParser()
parser.add_argument('input_dir_path', help = 'directory path to input folder')
parser.add_argument('incorrect_input_dir_path', help = 'directory for files with incorrect format')
parser.add_argument('file_format', help = 'file format to be processed')
parser.add_argument('connection_to_db', help = 'location of database file')
parser.parse_args()
'''
# Monitor folder 'input' for files for .fb2 files (if other file exist - move it to 'incorrect_input' folder)
def monitor_files(input_dir_path, incorrect_input_dir_path, file_format):
    contents = os.listdir(input_dir_path)
    print('getting the folder contents . . .') #this print-statements should be replaced with a proper logger
    print('found files in folder: {contents}')
    for file_name in contents:
        if file_name[-(len(file_format)):] == file_format:
            print ('file {file_name} is {file_format}, ready for analysis')
        else:
            print(f'{file_name} is of unsupported format, moving to {incorrect_input_dir_path}')
            os.replace(f'{input_dir_path}/{file_name}', f'{incorrect_input_dir_path}/{file_name}')

# a class that prepares file text for analysis and gets some file data
class FileAnalyzer():

    def __init__(self, file):
        self.file = file

# method to get a nice text w/o special symbols and numbers that we're going to analyze later
    def prepare_file_text(self, file):

        tree = ET.parse(self.file)
        root = tree.getroot()
        body = root.find("./{http://www.gribuser.ru/xml/fictionbook/2.0}body")
        text = ''
        for item in body.iter():
            if item.tag == '{http://www.gribuser.ru/xml/fictionbook/2.0}p' and item.text != None:
                text += (item.text + ' ')
        text = re.sub('[^А-Яа-я]+', ' ', text)
        return text

    def get_title(self, file):

        tree = ET.parse(self.file)
        root = tree.getroot()
        title_info = root.find(
            "./{http://www.gribuser.ru/xml/fictionbook/2.0}description/{http://www.gribuser.ru/xml/fictionbook/2.0}title-info")
        for item in title_info:
            if item.tag == '{http://www.gribuser.ru/xml/fictionbook/2.0}book-title':
                title = str(item.text)
                break
        return title

    def get_number_of_sections(self, file):

        tree = ET.parse(self.file)
        root = tree.getroot()
        body = root.find("./{http://www.gribuser.ru/xml/fictionbook/2.0}body")
        section_count = 0
        for item in body:
            if item.tag == '{http://www.gribuser.ru/xml/fictionbook/2.0}section':
                section_count += 1
        return section_count

# this class works with book text being analyzed only
class TextAnalyzer():

    def __init__(self, text):
        self.text = text

    def word_count(self, text):
        wordcount = 0
        words_list = text.split(' ')
        for word in words_list:
            wordcount += 1
        return wordcount

    def letter_count(self, text):
        lettercount = 0
        words_list = self.text.split(' ')
        for word in words_list:
            for letter in word:
                if letter.isalnum() == True:
                    lettercount += 1
        return lettercount

    def lowercase_wordcount(self, text):
        l_wordcount = 0
        words_list = self.text.split(' ')
        for word in words_list:
            if word == word.lower():
                l_wordcount += 1
        return l_wordcount

    def capitalized_wordcount(self, text):
        u_wordcount = 0
        words_list = self.text.split(' ')
        for word in words_list:
            if word.istitle() == True:
                u_wordcount += 1
        return u_wordcount

    def get_word_freq(self, text):
        wordfreq = []
        words_list = self.text.split(' ')

        for word in words_list:
            wordfreq.append(words_list.count(word))
        words_dict = dict(list(zip(words_list, wordfreq)))
        return words_dict

    def get_capitalized_freq(self, text):
        wordfreq = []
        words_list = self.text.split(' ')

        for word in words_list:
            if word.istitle() == True:
                wordfreq.append(words_list.count(word))
            else:
                wordfreq.append(0)
        cap_dict = dict(list(zip(words_list, wordfreq)))
        return cap_dict

# some functions to work with SQL TODO: wrap in class
def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn


def create_table(conn, create_table_statement):
    c = conn.cursor()
    c.execute(create_table_statement)


def insert_in_allbooks(conn, table):
    sql = f''' INSERT INTO all_books(book_name, number_of_paragraphs, number_of_words, number_of_letters, words_with_capital_letters, words_in_lowercase)
                  VALUES({title},{n_sections},{w_count},{l_count},{cap_wordcount},{lower_wordcount}) '''
    cur = conn.cursor()
    cur.execute(sql, table)
    conn.commit()


def insert_in_book_name(conn, book_name, word_freq, capitalized_freq):
    for key in word_freq.keys():
        sql = f''' INSERT INTO {title}(word, count, count_capitalized)
                      VALUES({key},{word_freq[value]},{capitalized_freq[value]}) '''

        cur = conn.cursor()
        cur.execute(sql, book_name)
        conn.commit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir_path', help = 'directory path to input folder')
    parser.add_argument('incorrect_input_dir_path', help = 'directory for files with incorrect format')
    parser.add_argument('file_format', help = 'file format to be processed')
    parser.add_argument('connection_to_db', help = 'location of database file')
    args = parser.parse_args()

    monitor_files(input_dir_path = args.input_dir_path, incorrect_input_dir_path = args.incorrect_input_dir_path, file_format = args.file_format)
    contents = os.listdir(args.input_dir_path)

    for file in contents:

        file = args.input_dir_path+'/'+file
        
        file_analyzer = FileAnalyzer(file)
        title = file_analyzer.get_title(file)
        n_sections = file_analyzer.get_number_of_sections(file)
        text = file_analyzer.prepare_file_text(file)

        text_analyzer = TextAnalyzer(text)
        w_count = text_analyzer.word_count(text)
        l_count = text_analyzer.letter_count(text)
        lower_wordcount = text_analyzer.lowercase_wordcount(text)
        cap_wordcount = text_analyzer.capitalized_wordcount(text)
        word_freq = text_analyzer.get_word_freq(text)
        capitalized_freq = text_analyzer.get_capitalized_freq(text)

        sql_create_all_books_table = """ CREATE TABLE IF NOT EXISTS all_books (
                                                book_name text NOT NULL,
                                                number_of_paragraphs integer,
                                                number_of_words integer,
                                                number_of_letters integer,
                                                words_with_capital_letters integer,
                                                words_in_lowercase integer
                                            ); """

        sql_create_book_name_table = """CREATE TABLE IF NOT EXISTS {} (
                                            word text NOT NULL,
                                            count integer,
                                            count_capitalized integer
                                        );""".format(title)

        conn = create_connection(args.connection_to_db)

        all_books_table = create_table(conn, sql_create_all_books_table)
        book_table = create_table(conn, sql_create_book_name_table)
        insert_in_allbooks(conn, all_books_table)
        insert_in_book_name(conn, book_table, word_freq, capitalized_freq)

if __name__ == '__main__':
    main()
