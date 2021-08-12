
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import string

#put in path to chromedriver here
PATH = "C:\\Users\\elino\\Documents\\ChromeDriver\\chromedriver.exe"
driver = webdriver.Chrome(PATH)

class Word:
    def __init__(self, value):
        self.word_text = value
        self.count = 0

    def assign_count(self, value):
        self.count = value

def make_sections(chunk, tag_index):
    tag_names = ['h2', 'h3', 'h4', 'h5', 'h6']
    new_chunk = []
    part_chunk = []
    i = 0
    j = 0
    count_tag = 0;
    for i in range(len(chunk)):
        if(chunk[i].tag_name == tag_names[tag_index] and i != 0):
            if count_tag == 0: #if this is the first tag encountered, the items so far are from the previous section
                while j < i:
                    new_chunk.append(chunk[j])
                    j += 1
                count_tag += 1
            else: #creates new chunk within old chunk
                while j < i:
                    part_chunk.append(chunk[j])
                    j += 1
                new_chunk.append(part_chunk)
                part_chunk = []
                count_tag += 1
    #add last part of chunk
    part_chunk = []
    if count_tag == 0: #aka if we have not run into any tags
        while j < len(chunk):
            new_chunk.append(chunk[j])
            j += 1

    else:
        while j < len(chunk):
            part_chunk.append(chunk[j])
            j += 1
        new_chunk.append(part_chunk)
    #go through new_chunk, and for each sublist, apply make_sections(sublist, index + 1)
    final_chunk = []
    if tag_index < len(tag_names):
        for item in new_chunk:
            if isinstance(item, list):
                final_chunk.append(make_sections(item, tag_index + 1))
            else:
                final_chunk.append(item)
        return final_chunk
    else:
        return new_chunk




def get_strings_from_text(text):
    text_strings = []
    raw_strings = re.findall(r'\w+', text)
    for item in raw_strings:
        text_strings.append(item.lower()) #adds words converted to lowercase
    return text_strings


def sort_key(word_obj):
    return word_obj.count


def get_section_words(section1, stop_words):
    all_words = []
    #eliminate reference text
    for item in section1:
        if(item.tag_name == 'a'):
            parent = item.find_element_by_xpath('..')
            if(parent.get_attribute('class') == 'reference'):
                continue
        all_words.extend(get_strings_from_text(item.text))
    #eliminate stop words
    no_stop_words = []
    for word in all_words:
        if not(word in stop_words):
            no_stop_words.append(word)
    # get rid of repetitions
    words_no_reps = [i for n, i in enumerate(no_stop_words) if i not in no_stop_words[:n]]
    word_objects = [] #list that holds word objects, which have a text value and a count value
    for word in words_no_reps:
        word_obj = Word(word)
        word_obj.assign_count(no_stop_words.count(word))
        word_objects.append(word_obj)

    #find most frequent words by reverse sorting the list by count, and then returning the first three items
    word_objects.sort(reverse=True, key=sort_key)
    top_three_words = word_objects[0:3]
    return top_three_words

def get_hyperlinks(section2):
    links = []
    for item in section2:
        if item.tag_name == "a":
            links.append(item.get_attribute('href'))
    return links


def do_chunk(sect, stopWords, index):
    tags = ['h2', 'h3', 'h4', 'h5', 'h6']
    #create indentation
    indent = ''
    for i in range(index):
        indent = indent + '\t'
    #print title
    if sect[0].tag_name == tags[index]:
        print(indent + 'Section Title: ' + sect[0].text)
    else: #this means that this is the paragraph that comes before the first header/section
        print('Beginning Paragraph:')
        index -= 1
    j = 0
    temp_chunk = []
    while (j < len(sect) and not isinstance(sect[j], list)):
        temp_chunk.append(sect[j])
        j += 1
    top_section_words = get_section_words(temp_chunk, stopWords)
    str_top_words = ''
    for i in range(len(top_section_words)):
        if (i < len(top_section_words) - 1):
            str_top_words += top_section_words[i].word_text + ', '
        else:
            str_top_words += top_section_words[i].word_text
    print(indent + '\tTop Words: ' + str_top_words)
    hyperlinks = get_hyperlinks(temp_chunk)
    for item in hyperlinks:
        if item is not None:
            print(indent + '\t' + item)
    while j < len(sect):
        if (index < len(tags)):
            do_chunk(sect[j], stopWords, index + 1)
            j += 1
    return

def delete_section(section):
    for item in section:
        del item

wikiPage = input('Please type in a wikipedia page link: ')
wikiBrowser = driver.get(wikiPage)
stopWords = ['am', 'is', 'are', 'were', 'was', 'be', 'being', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
             'will', 'would', 'should', 'could', 'shall', 'may', 'might', 'can', 'he', 'she', 'it', 'they', 'them', 'their'
             'her', 'him', 'its', 'a', 'an', 'the', 'who', 'what', 'why', 'how', 'where', 'while', 'if', 'that', 'and',
             'by', 'with', 'to', 'at', 'in', 'on', 'as', 'like', 'for', 'but', 'of', 'about', 'or', 'from', 'this']
articleTitle = driver.find_element_by_tag_name("h1").text
print("Article Title: " + articleTitle)
#find all h2, h3, h4, h5, h6, a, th, ul, li, dt, dl, dd tags
nodes = driver.find_elements_by_xpath('//*[@id="bodyContent"]/descendant::h2 | //*[@id="bodyContent"]/descendant::h3 | //*[@id="bodyContent"]/descendant::p | //*[@id="bodyContent"]/descendant::h4 | //*[@id="bodyContent"]/descendant::h5 | //*[@id="bodyContent"]/descendant::h6 | //*[@id="bodyContent"]/descendant::ul | //*[@id="bodyContent"]/descendant::a | //*[@id="bodyContent"]/descendant::th | //*[@id="bodyContent"]/descendant::li | //*[@id="bodyContent"]/descendant::dt | //*[@id="bodyContent"]/descendant::dl | //*[@id="bodyContent"]/descendant::dd')

sections = make_sections(nodes, 0)

do_chunk(sections, stopWords, 0)
for section in sections:
    if isinstance(section, list):
        delete_section(section)
    else:
        del section



