import pdfExtracter as pdf
import json

try:
    with open('AppSettings.json') as json_file:
        appSettingData = json.load(json_file)
        filePathData = appSettingData['fileSettings']
        
except Exception as e:
    pass


if __name__ == "__main__":
    try:
        rawData = pdf.Get.RawData(filePathData) #봉사실적, 창의적체험활동상황, 진로희망사항, 세부특기사항, 수상실적, 과목

        print("Save Data...", end = "")

        ouputData = {
            "봉사실적": pdf.FormatJson.data_봉사실적(rawData[0]),
            "창의적체험활동상황": pdf.FormatJson.data_창의적체험활동상황(rawData[1]),
            "진로희망사항": pdf.FormatJson.data_진로희망사항(rawData[2]),
            "세부특기사항": pdf.FormatJson.data_세부특기사항(rawData[3]),
            "수상실적": pdf.FormatJson.data_수상실적(rawData[4]),
        }

        with open(appSettingData['savePoint'] + filePathData['fileName'] + "_outputData.json", "w", encoding='utf-8') as json_file:
            json.dump(ouputData, json_file, indent="\t", ensure_ascii = False)

        print("Done")

    except Exception as e:
        print(e)
    
