import requests                                 # request para o json
import selenium                                 # selenium para acesso ao link final
from inspect    import stack                    # para deixar funções privadas
from selenium   import webdriver                # cria instancia do objeto edge
from time       import sleep        as Wait     # espera para o final do download
from json       import loads        as Load     # carrega os json dos arquivos
from base64     import b64encode    as Encoder  # decodificador para base64
from datetime   import datetime     as Date     # criador de datas
from os         import path         as Find     # procura arquivos da querys
from datetime   import datetime     as Now      # para criar Report Id

# URL da pagina de acesso desejado
siteURL = "https://wrs.solutions.iqvia.com/run.php"
mainHeader = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
  'Accept-Language' : 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
  'Connection' : 'keep-alive'
}

# classe principal
class querysHTTPS:
  def __init__(self):
    self.Getter = QuerysGetter() # função responsavel pelos jsons

  # função inicial de chamadas para  as ações
  def start(self): 
    self.sendHTTPSRequests() # chama função de requisiçao http

  # função que coleta as querys e manda para o servidor em cadeia
  def sendHTTPSRequests(self):
    datas = self.loadQuerys() # define variavel com os json´s
    session = requests.Session() # inicia uma seção https

    # inicia loop enviando todas as querys
    for data in datas:
      responseRequest = session.post(url=siteURL ,data=data, headers=mainHeader, allow_redirects=False)
      if datas.index(data) == 3: 
        datas[4]["reportId"] = str(Load(bytes(responseRequest.text, "utf-8"))["REPORT_ID"])
        
      if responseRequest.status_code != 200: 
        print("{} resposta inesperada, impossivel continuar".format(responseRequest.status_code))
        exit
      else: print("{} post realizado com sucesso" .format(responseRequest.status_code))
    
    RetivedJson = responseRequest.text[str(responseRequest.text).find("{"):len(responseRequest.text)]
    lastQueryGetLink = self.sendLastRequest(Load(RetivedJson))

    responseRequest = session.post(url=siteURL,data=lastQueryGetLink,headers=mainHeader)

    pass

  def sendLastRequest(self, anwser):
    """ >> Após o ultimo request contido no arquivo "jsonDownload.txt", o metodo
    sendHTTPSRequests() pega a resposta desse request como json e adpta a requesição
    para o formato do site. Após isso ele manda o ultimo request e pega o link para 
    a requisição do tipo GET. """

    with open (Find.dirname(__file__) + "\\Json\\jsonGetRequest.txt") as f: # abre arquivo contendo o ultimo json
      lastJson = str(f.read()).replace("\n","").replace(" ","")

    def ReplaceData(actFile, actTarget, actValue):
      if actTarget in actFile: return lastJson.replace(actTarget, str(actValue))
      else: return actFile

    for item, value in anwser.items():
      TargetReplace = str("$" + item + "$")
      if "dict" not in str(type(value)): lastJson = ReplaceData(lastJson, TargetReplace, value)
      else: 
        for subItem, subValue in value.items(): lastJson = ReplaceData(lastJson, str("$" + subItem + "$"),  subValue)

    return Load(lastJson.replace("\\","\\\\"))

  # função que trata e le os jsons
  def loadQuerys(self) -> vars:
    return self.Getter.sendAllJsons()

  # função que aguarda o download terminar
  def checkOut_Download(self, nameFile) -> bool:
      downloadPath = Find.expanduser(Find.join('~', 'Downloads')) # acha a pasta de download do computador atual
      while not Find.exists(Find.join(downloadPath , nameFile)): Wait(float(2))
      return True

class QuerysGetter:
    def __init__(self):
      try:
        if stack()[1][0].f_locals["self"].__class__.__name__ == "querysHTTPS": pass
      except: exit

    def sendAllJsons(self): # organizador, pega todos os json´s e organiza em uma array
      data = []
      data = self.getLogin()
      data.append(self.getQuery())
      data.append(self.getDownload())

      return data

    def readerFile(self,FileName:str): # metodo universal leitor de arquivos
      finalName = ""
      for i in FileName:
        if str(i).isalpha(): finalName += i

      with open(Find.dirname(__file__) + "\\Json\\{}.txt".format(finalName), "r", encoding="utf-8") as f:
        file = f.read().replace(" ",  "").replace("\n","")

      return file

    def getLogin(self): # pega arquivo contendo o json para o login incial
      file = self.readerFile("jsonLogin")
      contents = file.replace("\t","").replace("\n","").replace("'","\"").split(">>>>")

      for content in contents: 
        contents[contents.index(content)] = Load(content)

      return contents

    def getQuery(self): # pega arquivo contendo o json para a query principal

      def generate_report_id():
        return Now.now().strftime('%d%H%M%S')
      
      file             = self.readerFile("jsonTable")
      file = file.replace("$REPORT_ID$",generate_report_id())
      mainJson         = Load(file.split(">>>>")[0])
      data             = str(Date.now().strftime("%Y%D")[0:6])
      infosJsonDecoded = file.split(">>>>")[1].replace("#DateToSwitch", data).split("@ins")
      RowsTarget       = ["FILTER_TMP", "LAYOUT_FILTERS", "LAYOUT_MEASURES", "LAYOUT_ROWS"]

      for item, infoDecoded in zip(RowsTarget, infosJsonDecoded):
        mainJson[item] = Encoder(bytes(infoDecoded,"utf-8"))

      return mainJson

    def getDownload(self): # pega arquivo contendo o json para donwload
      file                = self.readerFile("jsonDownload")
      mainPart            = Load(file.split("@ins")[0])
      mainPart["dadosJs"] = Encoder(bytes(file.split("@ins")[1],"utf-8"))

      return mainPart

def caller(protocol):
  if int(protocol) == 4002: # evitar chamadas desnecessarias
    instance = querysHTTPS()
    instance.start()
  
if __name__  == '__main__': caller(4002)