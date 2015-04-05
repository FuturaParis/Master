

import gzip
import simplejson
import ast
import nltk
import collections 

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

def CountWords(filename,SortDict=False):
  '''
  Function counts frequency for each token existing in review.
  Token present multiple times in one review is counted as one.
  '''
  ReviewCount = 0
  WordCountDict = collections.defaultdict(int)
  for DataSetReview in parse(filename):
    ReviewCount +=  1
    try:
      CategorizedReview = ast.literal_eval(simplejson.dumps(DataSetReview))
      #get review text
      TokenizedReviewText = nltk.word_tokenize(CategorizedReview['review/text'])
      TokensAppeared = set([])
      for Token in TokenizedReviewText:
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
      SortedDictStr = SortedDictStr + "'" + Token + "': " + str(WordCountDict[Token]) + ", "

  MostCommonName = max(WordCountDict, key=WordCountDict.get)    
  print 'Tokens analysed:', len(WordCountDict), 'most common token:', MostCommonName

  with open("CleanerAttributes.txt", "w") as DestFile:
    ReviewCountInfo = str(ReviewCount) + '\n'

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
          SelectedTokens = ast.literal_eval(SrceFile.read())
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

def CreateDataSet(filename,SelectedTokens = 'SelectedTokens.txt'):
  print '-----Creating Data Set-----'
  
  #if list of selected token isn't currently loaded, get it from file
  if isinstance(SelectedTokens, basestring):
    with open("SelectedTokens.txt", "w") as SrceFile:
      SelectedTokens = ast.literal_eval(SrceFile.read())
  else:
    pass

  #Clean old contents of dataset file
  open('matrixJewelry.txt', 'w').close()

  SelectedTokensDict ={}
  for Token in SelectedTokens:
    SelectedTokensDict[Token] = 0
  
  ReviewCount = 0
  with open("matrixJewelry.txt", "a") as matrix:
    for DataSetReview in parse(filename):
      try:
        ReviewCount +=  1

        CategorizedReview = ast.literal_eval(simplejson.dumps(DataSetReview))
        #get review text
        TokenizedReviewText = nltk.word_tokenize(CategorizedReview['review/text'])
        for Token in TokenizedReviewText:
          if Token in SelectedTokensDict:
            SelectedTokensDict[Token] = 1

        MetaData = (str(CategorizedReview["product/price"]) + ', ' +
                    str(CategorizedReview["review/time"]) + ', ' +
                    str(CategorizedReview["product/productId"]) +
                    str(CategorizedReview["review/helpfulness"]) + ', '+
                    str(CategorizedReview["review/summary"]) + ', '+
                    str(CategorizedReview["review/userId"]) + ', '+
                    str(CategorizedReview["review/score"]) + ', ')
        DatasetRow = MetaData + str(SelectedTokensDict.values())[1:-1] + '\n'
     
        matrix.write(DatasetRow)
      except:
        print DataSetReview

      SelectedTokensDict = dict.fromkeys(SelectedTokensDict, 0)

filename = "Jewelry.txt.gz"
CountWordsResults = CountWords(filename)
SelectTokensResults = SelectTokens(1,60,CountWordsResults)
CreateDataSet(filename,SelectTokensResults)

