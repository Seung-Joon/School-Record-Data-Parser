import pdfplumber
# pdf 데이터 파싱 모듈.
# 참고사이트: https://github.com/jsvine/pdfplumber

class Get:
    def aranngeList(data, start, end):
        del data[start:end]
        return data
        
    def RawDataSetPage(file, index):
        with pdfplumber.open(file) as pdf:
            targetPage = pdf.pages[index]
            return targetPage.extract_tables()

    def RawData(file):
        with pdfplumber.open(file['filePath'] + file['fileName']) as pdf:
            봉사실적 = [] 
            창의적체험활동상황 = [] 
            진로희망사항 = [] 
            세부특기사항 = []
            수상실적 = [] 
            과목 = ['현장실습유형', '현장실습 직무분야', '실습기간', '실습내용']

            # 생기부 버전 읽기
            try:
                pageVersion = int(pdf.pages[0].extract_tables()[-2][0][1][:4])
            except:
                pageVersion = int(pdf.pages[0].extract_tables()[-1][0][1][:4])

            print("Target Page Verison: ",pageVersion)
            print("Extract Data...", end = "")


            for pageIndex in range(len(pdf.pages)):
                targetPage = pdf.pages[pageIndex]
                table = targetPage.extract_tables()


                for dataSets in table:

                    if len(dataSets[0]) > 0:
                        if dataSets[0][0] != None:
                            flagData = dataSets[0][0].replace(" ", "") #2020년 생기부 데이터 기준 파싱 위치
                            if flagData[2:] == '세부능력및특기사항':
                                세부특기사항.append(dataSets[1])

                            # ==== 수상경력 데이터 파싱 부분 ====

                            if flagData[2:] == '수상경력': # 해당 부분은 2016버전, 2020버전 모두 동작함.
                                [수상실적.append(index) for index in dataSets[2:]]

                            if flagData == '수상명': # 2020 버전만 동작함
                                [수상실적.append(index) for index in dataSets[1:]]

                            # ==== 진로희망사항 데이터 파싱 부분 ====

                            if flagData[2:] == '진로희망사항' and pageVersion <= 2016: # 2016년 이하 버전에서만 동작
                                [진로희망사항.append([index[0], index[3], index[4]]) for index in dataSets[3:]]



                    if len(dataSets[0]) > 1:
                        if dataSets[0][1] != None:
                            flagData = dataSets[0][1].replace(" ", "")
                            # ==== 창의적체험활동상황 데이터 파싱 부분 ====
                            
                            if  flagData == '창의적체험활동상황':              
                                [창의적체험활동상황.append(index) for index in dataSets[2:]]

                            # ==== 봉사활동실적 데이터 파싱 부분 ====

                            if flagData == '봉사활동실적':
                                [봉사실적.append(index[0:-1]) for index in dataSets[2:]]



                    if len(dataSets) > 1:
                        if len(dataSets[0]) > 1 :
                            if dataSets[1][1] != None: 
                                flagData = dataSets[1][1].replace(" ", "")
                                # ==== 진로희망 데이터 파싱 부분 ====
                                if flagData == '진로희망': #2020년 버전만 동작함, 처음 항목 파싱
                                    [진로희망사항.append(index) for index in dataSets[2:]]
                                
                                # ==== 과목 데이터 파싱(예체능 과목) ====
                                if flagData == '과목': # 2016, 2020년 버전 동작, 예체능 데이터 추출
                                    for index in dataSets[2:]:
                                        if index[1] != None:
                                            과목.append(index[1].replace("\n", ""))

                                # =============================

                            if dataSets[0][1] != None:
                                flagData = dataSets[0][1].replace(" ", "")
                                
                                #==== 과목 데이터 파싱(일반교과 과목) ====
                                if flagData  == '과목': # 2016, 2020년 버전 동작, 일반교과 데이터 추출
                                    for index in dataSets[1:]:
                                        if index[1] != None:
                                            과목.append(index[1].replace("\n", ""))
                                
                                
                                # ==== 진로희망 데이터 파싱 부분 ====

                                if flagData  == '진로희망': #2020년 버전만 동작
                                    [진로희망사항.append(index) for index in dataSets[2:]]

                                # ==== 생기부 수상경력 데이터 파싱 부분 ====

                                if flagData == '수상명': # 2016 버전만 동작함, index 0번 데이터가 비어있음.
                                    [수상실적.append(index) for index in dataSets[1:]]

                                # ==== 진로희망 데이터 파싱 부분 ====

                                if flagData == '특기또는흥미': # 2016 버전만 동작함. 편의를 위해 특기또는흥미로 검색하도록 설정함
                                    [진로희망사항.append(Get.aranngeList(index, 1, 3)) for index in dataSets[2:]]
        print("Done")
        return [봉사실적, 창의적체험활동상황, 진로희망사항, 세부특기사항, 수상실적, 과목]


class Data:
    def NormalizationEmptyData(rawData, appendLength = 1): # 봉사실적, 수상 실적, 진로희망사항
        for cursor in range(len(rawData) - 1):
            for index in range(appendLength):
                if rawData[cursor][index] != None:
                    flagData = rawData[cursor][index]

                if rawData[cursor + 1][index] == None or rawData[cursor + 1][index] == '':
                    rawData[cursor + 1][index] = flagData
        
        return rawData
    
    def Normalization_봉사실적(rawData):
        for index in range(len(rawData)):
            if rawData[index][2] == '-':
                rawData[index][1] += ' - ' + rawData[index][3]
                
            rawData[index] = Get.aranngeList(rawData[index], 2, 4)
            
            
        return Data.NormalizationEmptyData(rawData)
            

    def Normalization_창의적체험활동상황(rawData):
        return Data.NormalizationEmptyData(rawData, 2)

    def Normalization_진로희망사항(rawData):
        initData = [[], [], []]
        rawData = Data.NormalizationEmptyData(rawData, 1)
      
        for index in range(len(rawData)):
            if rawData[index][1] == '':
                initData[int(rawData[index - 1][0]) - 1][2] += rawData[index][2]
                
            else:
                initData[int(rawData[index][0]) - 1] = rawData[index]
        
        return initData

    def Normalization_수상실적(rawData):
        return Data.NormalizationEmptyData(rawData)

    def Normalization_세부특기사항(rawData):
        rawDataString = ""
        initData = []
        splitedData = []

        for data in rawData: rawDataString += data[0] #init rawDataString
        
        for data_step1 in rawDataString.split('\n'): #split Data \n
            for data_step2 in data_step1.split('.'): #split Data .
                splitedData.append(data_step2.split(":"))
        
        return [splitedData, rawDataString]

class FormatJson:
    def data_진로희망사항(raw_data_list):
        formatedData = {
        "1학년":{
                "진로희망": "",
                "희망사유": "",
            },
            "2학년":{
                "진로희망": "",
                "희망사유": "",
            } ,
            "3학년":{
                "진로희망": "",
                "희망사유": "",
            } ,
        } 
        
        raw_data_list = Data.Normalization_진로희망사항(raw_data_list)
        
        for dataSet in raw_data_list:
            if len(dataSet) > 2: # 데이터가 모두 들어있을때만 입력
                formatedData[dataSet[0] + "학년"]= {
                    "진로희망": dataSet[1].replace("\n", ""),
                    "희망사유": dataSet[2].replace("\n", "")
                }
        return formatedData


    def data_봉사실적(raw_data_list):
        initData = [[], [], []]
        
        raw_data_list = Data.Normalization_봉사실적(raw_data_list)
        
        for index in range(len(raw_data_list)):
            dataSet = raw_data_list[index]
            initData[int(dataSet[0]) - 1].append(
                {
                    "날짜": dataSet[1].replace("\n", ""),
                    "기관": dataSet[2].replace("\n", ""),
                    "활동내용": dataSet[3].replace("\n", ""),
                    "봉사시간": dataSet[4].replace("\n", ""),
                }
            )
            
        formatedData = {
            "1학년": {},
            "2학년": {},
            "3학년": {},
        }
            
        for gradeIndex in range(len(initData)):
            dataSets = initData[gradeIndex]
            for index in range(len(dataSets)):
                formatedData[str(gradeIndex + 1)  + "학년"][index] = dataSets[index]

        return formatedData


    def data_수상실적(raw_data_list):
        formatedData = {} 
        
        raw_data_list = Data.Normalization_수상실적(raw_data_list)
        
        for index in range(len(raw_data_list)):
            dataSet = raw_data_list[index]
            formatedData[index] = {
                "구분": dataSet[1].replace("\n", ""),
                "수상명": dataSet[2].replace("\n", ""),
                "등급": dataSet[3].replace("\n", ""),
                "수여기관": dataSet[4].replace("\n", ""),
                "참가대상": dataSet[4].replace("\n", ""),
            }
                   
        return formatedData

    def data_세부특기사항(raw_data_list):
        nomalizationData = Data.Normalization_세부특기사항(raw_data_list)
        raw_data_list = nomalizationData[0]
        formatedData = {}
        dataIndex = ''
        
        
        for index in raw_data_list:
           
            if len(index) > 1: # 키 데이터 분리, 키 지정
                dataIndex = index[0].rstrip()
                formatedData[dataIndex] = ''
                for cursor in index[1:]: formatedData[dataIndex] += cursor #데이터 기준
                
            else :
                for cursor in index: formatedData[dataIndex] += cursor
            
            if len(index) == 1:
                if index[0] == '': #끝이. 이었던 부분은 데이터 split시 '' 혹은 ' '형태로 나타남
                    formatedData[dataIndex] += '.'
                else:
                    try: # 날짜 데이터 형식은 YYYY(길이 4), MM, DD(길이 2)로 나타남 날짜 데이터 나타날경우 . 붙여줌
                        if len(index[0]) == 2 or len(index[0]) == 4:
                            int(index[0]) #날짜 데이터 복원 여기서 날짜 형식이 아닌경우 에러남
                            formatedData[dataIndex] += '.' #데이터에 따라 제대로 작동되지 않을 수 있음으로 날짜 . 붙이는건 포기 추천
                    except:
                        pass
            
        return {"formatedData": formatedData, "rawData": nomalizationData[1]}

    def data_창의적체험활동상황(raw_data_list):
        formatedData = {
            "1학년": {
                "자율활동":{
                    "시간": "",
                    "내용": "",
                },
                "동아리활동": {
                    "시간": "",
                    "내용": "",
                },
                "봉사활동": {
                    "시간": "",
                    "내용": "",
                },
                "진로활동": {
                    "시간": "",
                    "내용": "",
                }
            },
            "2학년": {
                "자율활동":{
                    "시간": "",
                    "내용": "",
                },
                "동아리활동": {
                    "시간": "",
                    "내용": "",
                },
                "봉사활동": {
                    "시간": "",
                    "내용": "",
                },
                "진로활동": {
                    "시간": "",
                    "내용": "",
                }
            },
            "3학년": {
                "자율활동":{
                    "시간": "",
                    "내용": "",
                },
                "동아리활동": {
                    "시간": "",
                    "내용": "",
                },
                "봉사활동": {
                    "시간": "",
                    "내용": "",
                },
                "진로활동": {
                    "시간": "",
                    "내용": "",
                }
            }
        }

        raw_data_list = Data.Normalization_창의적체험활동상황(raw_data_list)

        for dataSet in raw_data_list:
            formatedData[str(dataSet[0]) + "학년"][dataSet[1]]["시간"] += dataSet[2]
            formatedData[str(dataSet[0]) + "학년"][dataSet[1]]["내용"] += dataSet[3].replace("\n", "")
        
        return formatedData




