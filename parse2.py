import gzip
import json
import ast
import nltk
import collections 

def ngrams(sequence, n, lower=True):
    """
    Return the ngrams generated from a sequence of items, as an iterator.
    For example:

        >>> from nltk.util import ngrams
        >>> list(ngrams([1,2,3,4,5], 3))
        [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

    :param sequence: the source data to be converted into ngrams
    :type sequence: sequence or iter
    :param n: the degree of the ngrams
    :type n: int
    :type pad_symbol: any
    :rtype: iter(tuple)
    :param lower: convert to lovwercase
    :type param: bool
    """
    if lower:
      sequence = [str(token).lower() for token in sequence]

    PunctMarks = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    sequence = iter(sequence)

    history = []
    while n > 1:
        history.append(next(sequence))
        n -= 1
    for item in sequence:
        history.append(item.translate(None, PunctMarks))
        yield tuple(history)
        del history[0]


def parse(filename):
  f = gzip.open(filename, 'r')
  entry = {}
  for l in f:
    l = l.strip()
    colonPos = l.find(b':')
    if colonPos == -1:
      yield entry
      entry = {}
      continue
    eName = l[:colonPos]
    rest = l[colonPos+2:]
    entry[eName] = rest
  yield entry

def CountWords(filename,SortDict=False,NGramNum=1):
  '''
  Function counts frequency for each token existing in review.
  Token present multiple times in one review is counted as one.
  '''
  ReviewCount = 0
  WordCountDict = collections.defaultdict(int)
  for DataSetReview in parse(filename):
    ReviewCount +=  1
    try:
      CategorizedReview = ast.literal_eval(json.dumps(DataSetReview))
      #get review text
      TokenizedReviewText = nltk.word_tokenize(CategorizedReview['review/text'])
      TokensAppeared = set([])
      for Token in ngrams(TokenizedReviewText, NGramNum):
        if Token not in TokensAppeared:
          WordCountDict[Token] += 1
          TokensAppeared.add(Token)
    except:
      print 'Error on ', Token

  #sort collected tokens by frequency
  if SortDict:
    print 'Sorting Dictionary'
    SortedDictStr = ''
    for Token in sorted(WordCountDict, key=WordCountDict.get, reverse=True):
      SortedDictStr = SortedDictStr + "'" + str(Token) + "': " + str(WordCountDict[Token]) + ", "

  MostCommonName = max(WordCountDict, key=WordCountDict.get)    
  print 'Tokens analysed:', len(WordCountDict), 'most common token:', MostCommonName

  ResultFileName = "CleanerAttributesNGram" + str(NGramNum) + ".txt" 

  with open("CleanerAttributes.txt", "w") as DestFile:
    ReviewCountInfo = str(ReviewCount).replace(',',';') + '\n'

  with open("CleanerAttributes.txt", "a") as DestFile:

    if SortDict:
      SortedDictStrToFile = '{' + SortedDictStr[:-1] + '}'
      DestFile.write(SortedDictStrToFile)
    else:
      WordCountDictToFile = '{' + str(WordCountDict)[:-1] + '}'
      DestFile.write(WordCountDictToFile)

  return WordCountDict, ReviewCount

def SelectTokens(BottomTreshold,UpperTreshold,wordCountResults = 'CleanerAttributes.txt'):
  
  #if Word Count dictionary isn't currently loaded, get it from file
  if isinstance(wordCountResults, basestring):
    with open("SelectedTokens.txt", "r") as SrceFile:
      LineCount = 0
      for line in SrceFile:
        if LineCount == 0:
          ReviewCount = line
        else:
          WordCountDict = ast.literal_eval(SrceFile.read())
        LineCount += 1
  else:
    WordCountDict = wordCountResults[0]
    ReviewCount = wordCountResults[1]

  print 'Reviews number:', ReviewCount
  SelectedTokens = []
  for Token in WordCountDict:
    Freq = float(WordCountDict[Token]) / float(ReviewCount)
    if Freq > float(UpperTreshold) / 100:
      print Token, WordCountDict[Token], Freq
    if Freq < float(UpperTreshold) / 100 and Freq > float(BottomTreshold) / 100:
      SelectedTokens.append(Token)

  print 'Tokens selected:', len(SelectedTokens), 'tokens rejected:', len(WordCountDict) - len(SelectedTokens)

  with open("SelectedTokens.txt", "w") as DestFile:
    DestFile.write(str(SelectedTokens))

  return SelectedTokens

def CreateDataSet(filename,SelectedTokens = 'SelectedTokens.txt',NGramNum=1):
  print '-----Creating Data Set-----'
  
  #if list of selected token isn't currently loaded, get it from file
  if isinstance(SelectedTokens, basestring):
    with open("SelectedTokens.txt", "r") as SrceFile:
      SelectedTokens = ast.literal_eval(SrceFile.read())
  else:
    pass
  MetaHeaderList = "'METAprice';'METAtime';'METAproductId';'METAuserId';'METAscore';"
  SelectedTokensStr = str(SelectedTokens)[1:-1]
  HeaderList = MetaHeaderList + SelectedTokensStr
  ClearedHeaderList = HeaderList.replace("'","").replace('),',');').replace(',(',';(')

  print ClearedHeaderList
  #Clean old contents of dataset file
  with open('matrixJewelry.txt', 'w') as matrix:
    matrix.write(ClearedHeaderList + '\n')

  SelectedTokensDict = {}
  for Token in SelectedTokens:
    SelectedTokensDict[Token] = 0
  
  ReviewCount = 0
  with open("matrixJewelry.txt", "a") as matrix:
    for DataSetReview in parse(filename):
      try:
        ReviewCount +=  1
  
        CategorizedReview = ast.literal_eval(json.dumps(DataSetReview))
  
        #get review text
        TokenizedReviewText = nltk.word_tokenize(CategorizedReview['review/text'])
  
        for Token in ngrams(TokenizedReviewText, NGramNum):
          if Token in SelectedTokensDict:
            SelectedTokensDict[Token] = 1
  
        MetaData = (str(CategorizedReview["product/price"]) + '; ' +
                    str(CategorizedReview["review/time"]) + '; ' +
                    str(CategorizedReview["product/productId"]) + '; ' +
                    #str(CategorizedReview["review/helpfulness"]) + '; '+
                    #str(CategorizedReview["review/summary"]) + '; '+
                    str(CategorizedReview["review/userId"]) + '; '+
                    str(CategorizedReview["review/score"]) + '; ')
        TokensCoding = str(SelectedTokensDict.values())[1:-1]
        DatasetRow = MetaData + TokensCoding.replace(',',';') + '\n'
        DatasetRowWithoutSpaces = DatasetRow.replace(' ','')
        matrix.write(DatasetRowWithoutSpaces)
      except:
        print DataSetReview

      SelectedTokensDict = dict.fromkeys(SelectedTokensDict, 0)

filename = "Jewelry.txt.gz"
CountWordsResults = CountWords(filename,True,NGramNum = 2)
SelectTokensResults = SelectTokens(1,50,CountWordsResults)
CreateDataSet(filename,SelectTokensResults,NGramNum = 2)

