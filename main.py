# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Lsa
from sumy.summarizers.luhn import LuhnSummarizer as Luhn
from sumy.summarizers.text_rank import TextRankSummarizer as TextRank
from sumy.summarizers.lex_rank import LexRankSummarizer as LexRank
from sumy.summarizers.sum_basic import SumBasicSummarizer as SumBasic
from sumy.summarizers.kl import KLSummarizer as KLsum
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import PyPDF2
import os
import time
import shutil
import sys, traceback
import xlrd
import cutie
import getopt

# Helper class used to map pages numbers to bookmarks
class BookmarkToPageMap(PyPDF2.PdfFileReader):

    def getDestinationPageNumbers(self):
        def _setup_outline_page_ids(outline, _result=None):
            if _result is None:
                _result = {}
            for obj in outline:
                if isinstance(obj, PyPDF2.pdf.Destination):
                    _result[(id(obj), obj.title)] = obj.page.idnum
                elif isinstance(obj, list):
                    _setup_outline_page_ids(obj, _result)
            return _result

        def _setup_page_id_to_num(pages=None, _result=None, _num_pages=None):
            if _result is None:
                _result = {}
            if pages is None:
                _num_pages = []
                pages = self.trailer["/Root"].getObject()["/Pages"].getObject()
            t = pages["/Type"]
            if t == "/Pages":
                for page in pages["/Kids"]:
                    _result[page.idnum] = len(_num_pages)
                    _setup_page_id_to_num(page.getObject(), _result, _num_pages)
            elif t == "/Page":
                _num_pages.append(1)
            return _result

        outline_page_ids = _setup_outline_page_ids(self.getOutlines())
        page_id_to_page_numbers = _setup_page_id_to_num()

        result = {}
        for (_, title), page_idnum in outline_page_ids.items():
            result[title] = page_id_to_page_numbers.get(page_idnum, '???')
        return result

#Functon to convert pdf into text
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)
  #  Check :  print ('converting......')
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams(), codec='utf-8')
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

##########################  Main Program   ########################
def main(argv):
    # Leer parametros archivo entrada y directorio salida
    try:
        opts, args = getopt.getopt(argv,"i:o:",["inputFile=","outputDirectory="])
    except getopt.GetoptError:
        print('main.py -i <inputFile> -o <outputDirectory>')
        sys.exit(2)
    
    if (len(opts) != 2):
        print('main.py -i <inputFile> -o <outputDirectory>')
        sys.exit(2)

    PDF_SummaryDir = ''
    sourcePDFFile = ''

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i <inputFile> -o <outputDirectory>')
            sys.exit()
        elif opt in ("-i", "--inputFile"):
            sourcePDFFile = arg
            if os.path.exists(sourcePDFFile):
                print('[+] Archivo PDF encontrado')
        elif opt in ("-o", "--outputDirectory"):
            PDF_SummaryDir = arg
            #Check if the directory PDF_summary exists or not
            if not os.path.exists(PDF_SummaryDir):
                os.makedirs(PDF_SummaryDir)
                print('[+] Directorio creado')

    #Set parameters
    languages = ['spanish', 'english']
    print('Seleccionar lenguaje')
    LANGUAGE = languages[cutie.select(languages)]
    print('[+] Lenguaje seleccionado')
    SENTENCES_COUNT = 30

    algoritmos = ['Luhn', 'Lsa', 'LexRank', 'TextRank', 'SumBasic', 'KLsum']
    print('Seleccionar algoritmo')
    chooseAlgo = algoritmos[cutie.select(algoritmos)]

    #create directories for output files
    outputPDFDir = os.path.dirname(PDF_SummaryDir + '/pdf/pdf_split_files/')
    if not os.path.exists(outputPDFDir):
        os.makedirs(PDF_SummaryDir + '/pdf/pdf_split_files/')

    outputTXTDir = os.path.dirname(PDF_SummaryDir + '/Text_Files/')
    if not os.path.exists(outputTXTDir):
        os.makedirs(PDF_SummaryDir + '/Text_Files/')

    outputSummaryDir = os.path.dirname(PDF_SummaryDir + '/Summary/')
    if not os.path.exists(outputSummaryDir):
        os.makedirs(PDF_SummaryDir + '/Summary/')

    #Name prefix for split files
    outputNamePrefix = 'Split_Chapter_'
    timeSuffixSummary = str(time.strftime("%d-%m-%Y_%H.%M.%S"))
    targetPDFFile = 'temppdfsplitfile.pdf' # Temporary file


    # Append backslash to output dir ofor pdf if necessary
    if not outputPDFDir.endswith('/'):
        outputPDFDir = outputPDFDir + '/'

    # Append backslash to output dir for txt if necessary
    if not outputTXTDir.endswith('/'):
        outputTXTDir = outputTXTDir + '/'

    # Append backslash to output dir ofor pdf if necessary
    if not outputSummaryDir.endswith('/'):
        outputSummaryDir = outputSummaryDir + '/'

    #Check and Verify if PDF is ready for splitting
    while not os.path.exists(sourcePDFFile):
        print('Source PDF not found, sleeping...')
        #Sleep
        time.sleep(10)

    if os.path.exists(sourcePDFFile):
        #print('Found source PDF file')
        #Copy file to local working directory
        shutil.copy(sourcePDFFile, targetPDFFile)

        #Process file
        #Create object and Open File in Read Binary Mode
        pdfFileObj2 = open(targetPDFFile, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj2)
        pdfFileObj = BookmarkToPageMap(pdfFileObj2)

        #Get total pages
        numberOfPages = pdfReader.numPages

        i = 0
        newPageNum = 0
        prevPageNum = 0
        newPageName = ''
        prevPageName = ''

        for p,t in sorted([(v,k) for k,v in pdfFileObj.getDestinationPageNumbers().items()]):
            template = '%-5s  %s'
        #   To Check Page number and Title of the Chapter Uncomment the following lines
        ##  print (template % ('Page', 'Title'))
        ##  print (template % (p+1,t))

            newPageNum = p + 1
            newPageName = t
            
            if prevPageNum == 0 and prevPageName == '':
            #  First Page
                prevPageNum = newPageNum
                prevPageName = newPageName
            else:
            # Next Page
                pdfWriter = PyPDF2.PdfFileWriter()
                page_idx = 0
                for i in range(prevPageNum, newPageNum):
                    pdfPage = pdfReader.getPage(i-1)
                    pdfWriter.insertPage(pdfPage, page_idx)
            #   Check : print('Added page to PDF file: ' + prevPageName + ' - Page #: ' + str(i))
                    page_idx+=1

            #   Creating names of split files
                pdfFileName = str( outputNamePrefix + prevPageName + '.pdf' ).replace(':','_').replace('*','_')
                txtFileName = str( outputNamePrefix + prevPageName + '.txt' ).replace(':','_').replace('*','_')

            #   Writing each chapter to the .pdf file
                pdfOutputFile = open(outputPDFDir + pdfFileName, 'wb')
                pdfWriter.write(pdfOutputFile)
                pdfOutputFile.close()

            #   Check : print('Created PDF file: ' + outputPDFDir + pdfFileName)

            #   Calling convert function and writing each chapter to the .txt file
                txtOutputFile = open(outputTXTDir + txtFileName, 'w')
                txtOutputFile.write(convert(outputPDFDir + pdfFileName))
                txtOutputFile.close()
            #   Check :print('Created TXT file: ' + outputTXTDir + txtFileName)

            #   for plain text files create Summary
                parser = PlaintextParser.from_file(outputTXTDir + txtFileName, Tokenizer(LANGUAGE))
                stemmer = Stemmer(LANGUAGE)
            #   Using LsaSummarizer to create summary
            ##  Select from different algorithms to create summary by using different algorithms
                if chooseAlgo == 'Lsa' :
                    summarizer = Lsa(stemmer)
                elif chooseAlgo == 'LexRank':
                    summarizer = LexRank(stemmer)
                elif  chooseAlgo == 'TextRank':
                    summarizer = TextRank(stemmer)
                elif  chooseAlgo == 'Luhn':
                    summarizer = Luhn(stemmer)
                elif  chooseAlgo == 'SumBasic':
                    summarizer = SumBasic(stemmer)
                elif  chooseAlgo == 'KLsum':
                    summarizer = KLsum(stemmer)
                else :
                    print ( 'Wrong Algorithm selected.')
                    sys.exit(0)

                summarizer.stop_words = get_stop_words(LANGUAGE)
            #   Open file in append mode so that summary will be added at the bottom of file
                summaryOutputFile = open(outputSummaryDir + chooseAlgo + '_Summary_File' + timeSuffixSummary + '.txt','a')
                for sentence in summarizer(parser.document, SENTENCES_COUNT):
            #   Check : print (sentence)
                    summaryOutputFile.write(str(sentence))

            #   To create Separation between Chapters
                summaryOutputFile.write(str('\n\n'+ 'Title : '+t+'\n'+'\t'))
                summaryOutputFile.close()

            i = prevPageNum
            prevPageNum = newPageNum
            prevPageName = newPageName
            
        # Split the last page
        pdfWriter = PyPDF2.PdfFileWriter()
        page_idx = 0
        for i in range(prevPageNum, numberOfPages + 1):
            pdfPage = pdfReader.getPage(i-1)
            pdfWriter.insertPage(pdfPage, page_idx)
        #   Check : print('Added page to PDF file: ' + prevPageName + ' - Page #: ' + str(i))
            page_idx+=1

        pdfFileObj2.close()
        print('[+] Archivo creado: ' + outputSummaryDir + 'SummaryFile.txt')

    # Delete temp file
    os.unlink(targetPDFFile)
    
if __name__ == "__main__":
   main(sys.argv[1:])