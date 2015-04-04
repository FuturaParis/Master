

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
    ReviewCount = ReviewCount +  1
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
    if SortDict:
      DestFile.write(SortedDictStr)
    else:
      DestFile.write(str(WordCountDict))

  return WordCountDict, ReviewCount

def SelectTokens(wordCountResults,BottomTreshold,UpperTreshold):
  # if not WordCountDict:
  #   Attributes = open(filename).read()
  #   DictString = '{' + Attributes[:-1] + '}'
  #   WordCountDict = ast.literal_eval(DictString)
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

def CreateDataSet(filename,SelectedTokens,TokensList):
  

  ReviewCount = 0
  WordCountDict = collections.defaultdict(int)
  for DataSetReview in parse(filename):
    ReviewCount = ReviewCount +  1
    try:
      CategorizedReview = ast.literal_eval(simplejson.dumps(DataSetReview))
      #get review text
      TokenizedReviewText = nltk.word_tokenize(CategorizedReview['review/text'])
      for Token in TokenizedReviewText:
        if Token in atributes:
          atributes[word] = 1
        else:
          pass
      MetaData = (str(dataset["product/price"]) + ', ' +
                  str(dataset["review/time"]) + ', ' +
                  str(dataset["product/productId"]) +
                  str(dataset["review/helpfulness"]) + ', '+
                  str(dataset["review/summary"]) + ', '+
                  str(dataset["review/userId"]) + ', '+
                  str(dataset["review/score"]) + ', ')
      DatasetRow = MetaData + str(atributes.values())[1:-1] + '\n'
    except:
      print 'Error on ', Token


      #print DatasetRow    
      with open("matrixJewelry.txt", "a") as matrix:
        matrix.write(DatasetRow)
      atributes = collections.OrderedDict.fromkeys(dictkeys, 0)
    except:
      print(dataset)
      pass

WordCountsDict = CountWords("Jewelry.txt.gz")
print type(WordCountsDict)
SelectTokens(WordCountsDict,1,60)

#a = open("E:/python/DICTtest.txt").read()
#dictkeys = ast.literal_eval(a)
#dictkeys = dictkeys[:5000]
#atributes = collections.OrderedDict.fromkeys(dictkeys, 0)
#
#
#  
#dataset = {}
#TextToWrite = []
#
#var = 0
#
#
#for e in parse("C:\Users\T530\Desktop\Jewelry.txt.gz"):
#  var = var + 1
#  try:
#    dataset = ast.literal_eval(simplejson.dumps(e))
#    tokens = nltk.word_tokenize(dataset['review/text'])
#    for word in tokens:
#      if word in atributes:
#        atributes[word] = 1
#      else:
#        pass
#    if var > 100000:
#      break
#    MetaData = (str(dataset["product/price"]) + ', ' +
#                str(dataset["review/time"]) + ', ' +
#                str(dataset["product/productId"]) +
#                str(dataset["review/helpfulness"]) + ', '+
#                str(dataset["review/summary"]) + ', '+
#                str(dataset["review/userId"]) + ', '+
#                str(dataset["review/score"]) + ', ')
#    DatasetRow = MetaData + str(atributes.values())[1:-1] + '\n'
#
#    #print DatasetRow    
#    with open("matrixJewelry.txt", "a") as matrix:
#      matrix.write(DatasetRow)
#
#    atributes = collections.OrderedDict.fromkeys(dictkeys, 0)
#  except:
#    print(dataset)
#    pass
#
