'''
Post processing of data crawled by ``ReindeerBot`` of rekhta.com
'''
import requests
import tempfile
import difflib
import os
from exceptions import Exception
from threading import Thread
from django.shortcuts import render, get_object_or_404

from crawlers.processors.tesseract import image_to_text_for_reindeer, check_packages
from crawlers.models import RawArticle
from common.utils import html_to_plain_text


def download_image(image_url):
    '''
    @image_url: Image url

    @summary: Returns image (full path name) downloaded from `image_url`
    '''
    print('Downloading image from', image_url)
    # Steam the image from the url
    try:
        request = requests.get(image_url, stream=True)
    except Exception as e:
        print('ERR:: Exception occurred.')
        print(e)
        return False

    # Was the request OK?
    if request.status_code != requests.codes.ok:
        # Nope, error handling, skip file etc etc etc
        print('ERR: response is', request.status_code)
        return False

    # Get the filename from the url, used for saving later
    file_name = image_url.split('/')[-1]

    # Create a temporary file
    lf = tempfile.NamedTemporaryFile(delete=False)

    # Read the streamed image in sections
    for block in request.iter_content(1024 * 8):

        # If no more file then stop
        if not block:
            break

        # Write image block to temporary file
        lf.write(block)

    # Close file and returns it's full path name
    lf.close()
    return lf.name


def get_poetry_img_url(poetry_url, language):
    '''
    @summary: Returns poetry image URL form ``poetry_url`` of language ``language``

    @note: ``poetry_url`` can be like 'https://rekhta.org/nazms/chand-roz-aur-mirii-jaan-faiz-ahmad-faiz-nazms?lang=hi'
    or 'https://rekhta.org/nazms/chand-roz-aur-mirii-jaan-faiz-ahmad-faiz-nazms'
    If ``language`` is 'hi', poetry image url will be 'https://rekhta.org/Images/UrduShayari/hi_chand-roz-aur-mirii-jaan-faiz-ahmad-faiz-nazms.png'
    '''

    base_url  = 'http://rekhta.org/Images/UrduShayari/'
    # I'm using http because https is giving SSLError, and I don't want to debug :P

    poetry_slug = poetry_url.split('/')[-1].split('?')[0]

    return base_url + language + '_' + poetry_slug + '.png'


def measure_similarity(str1, str2):
    '''
    @summary: Returns a float in [0, 1], measuring the similarity between two strings.
    As a rule of thumb, a value over 0.6 means the strings are close matches.

    @note: https://docs.python.org/2/library/difflib.html
    '''

    d = difflib.SequenceMatcher(None, str1, str2)
    s = round(d.ratio(), 3)
    #print 'DBG: similarity is ', s
    return s


def _is_similar(str1, str2):
    s = measure_similarity(str1, str2)
    if s > 0.6: #TODO: increase the value if you are not getting correct output
        return True
    else:
        return False


def correct_poetry_lines_order(shuffled_lines, ocr_lines):
    '''
    @summary: Correct the line ordering of shuffled_lines

    @shuffled_lines: Individual lines are correct, and ordering of lines are incorrect.
    @ocr_lines: Individual lines are partially correct, and ordering of lines are correct.
    '''

    len_suffled = len(shuffled_lines)
    len_ocr = len(ocr_lines)
    print('Correcting poetry lines ordering... (shuffled %d <-> ocr %d)'%(len_suffled, len_ocr))

    mapping = {}
    matched_ocr_lines = []

    for i in range(0, len_suffled):
        mapping[i] = {'index': i, 'weight': 0, 'final': -1}
        for j in range(0, len(ocr_lines)):
            if j not in matched_ocr_lines:
                s = measure_similarity(shuffled_lines[i], ocr_lines[j])
                if s > mapping[i]['weight'] and s > 0.6:
                    # Assuming s > 0.6 is very similar
                   mapping[i] = {'index': j, 'weight': s, 'final': j}

        # Mark the best match from ocr_lines\
        if mapping[i]['weight'] > 0:
            matched_ocr_lines.append(mapping[i]['index'])

    #print mapping
    ordered_lines = []
    # In case mapping->final is grater than len_shuffled: to prevent IndexError
    l = len_suffled if len_suffled > len_ocr else len_ocr
    for i in range(0, l):
        ordered_lines.append('')

    dup_lines = [] # For duplicate entries

    # Detect duplicate mapping and decide the winner(final)
    for i in range(0, len_suffled):
        for j in range(i+1, len_suffled):
            if mapping[i]['index'] == mapping[j]['index']:
                if mapping[i]['weight'] < mapping[j]['weight']:
                    mapping[i]['final'] = -1
                else:
                    mapping[j]['final'] = -1

    #print mapping
    for key, val in list(mapping.items()):
        if mapping[key]['final'] == -1:
            dup_lines.append(shuffled_lines[key])
        else:
            ordered_lines[val['index']] = shuffled_lines[key]

    if len(dup_lines):
        ordered_lines.append("###")

    return ordered_lines + dup_lines


def refine_poetry(crawled_poetry, url, language):
    '''
    '''

    # Get image of the poetry
    f_image = download_image(get_poetry_img_url(url, language))
    if f_image is False:
        print('ERR:: failed to download image')
        return False

    # Get text from poetry image : ocr_text
    ret = image_to_text_for_reindeer(f_image, language)
    if ret is False:
        print('ERR: falied to convert image to text')
        return False

    ocr_text = ret.strip()

    # Delete the `f_image` file from the storage
    try:
        os.remove(f_image)
    except:
        print('ERR:: failed to delete f_image')
        pass

    # Make list of lines from ``crawled_poetry`` and ``ocr_text``
    #print '--- ocr text ---'
    #print ocr_text
    ocr_lines = [x for x in ocr_text.split('\n') if len(x) > 0]

    cp = html_to_plain_text(crawled_poetry)
    #print '--- crawled poetry ---'
    #print cp
    crawled_lines = [x for x in cp.split('\n') if len(x) > 0]

    # Correct the line order of ``crawled_poetry``
    poetry_lines = correct_poetry_lines_order(crawled_lines, ocr_lines)
    poetry = '\n'.join(poetry_lines)

    #print '--- Final poetry ---'
    #print poetry
    # Return
    return poetry


class processArticleThread(Thread):
    '''
    @summary: process articles in multithreads
    '''    
    def __init__(self, threadID, name, articles):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.articles = articles
        
    def run(self):
        print(">> Starting thread " + self.name)
        process_articles(self.name, self.articles)
        print(">> Ending thread " + self.name)


def process_articles(name=None, articles=None):
    '''
    Process given list of articles.
    '''
    count_total = 0
    count_saved = 0
        
    if articles is not None:
        for obj in articles:
            count_total += 1
            poetry = refine_poetry(obj.content, obj.source_url, obj.language)
            if poetry:
                obj.content = poetry
                obj.valid = True
                obj.save()
                count_saved += 1
            else:
                return False

            # print stats
            if count_total % 100 == 0:
                print("> thread %s: saved %d out of %d processed"%(name, count_saved, count_total))    
    
    
def process_all_articles(num_thread=1):
    '''
    @summary: Post processing of all articles crawled by the ``ReindeerBot``
    Assuming all articles are valid=False.
    Process the article, write back to db, set valid=True(so that process can be resumed in case of failure)
    '''
    if num_thread < 1:
        num_thread = 1
    
    # Process only Hindi and English.
    #TODO Urdu OCR tessdata is not available currently. Add in the list, once it's available.
    language_list = ['hi', 'en']

    total_articles = RawArticle.objects.all().filter(source_url__icontains='rekhta.org').filter(valid=False, language__in=language_list)
    num_total = total_articles.count()
    print('Total articles to be proccessed : %d'%(num_total))
    print('Number of threads to be created : %d'%(num_thread))
    q = num_total / num_thread
    r = num_total - (q * num_thread)
        
    threads = []
    
    # Create new threads
    for i in range(0, num_thread):
        extra = r if (i == (num_thread - 1)) else 0
        num_start = i*q
        num_end = num_start + q + extra
        thread_name = 'Thread-'+str(i)
        
        print('Starting thread for total_articles[%d : %d]'%(num_start, num_end))
        
        t = processArticleThread(i, thread_name, total_articles[num_start : num_end])
        t.start()
        threads.append(t)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    print("Exiting Main Thread")            

    # print stats
    print("> THE END")


def set_all_invalid():
    print('Setting all articles of rekhta.org as invalid...')
    articles = RawArticle.objects.all().filter(valid=True).filter(source_url__icontains='rekhta.org')
    if articles is not None:
        for a in articles:
            a.valid = False
            a.save()
    print('Done!')


def cmd_init_reindeer():
    print('============= Initializing reindeer ==============')
    # Check for 'tesseract' and 'imagemagick' packages
    if check_packages() is False:
        return False
    set_all_invalid()
    print('================ init finished ===================')

def cmd_resume_reindeer(num_thread=1):
    print('=========== Resuming/running reindeer ============')
    process_all_articles(num_thread)
    print('=============== resume finished ==================')

def cmd_exit_reindeer():
    print('=============== Exiting reindeer =================')
    set_all_invalid()
    print('================= exit finished ==================')

def cmd_test_reindeer():
    print('=============== Testing reindeer =================')
    obj = get_object_or_404(RawArticle, pk=130831)
    poetry = refine_poetry(obj.content, obj.source_url, obj.language)
    print('================= test finished ==================')
    print(poetry)