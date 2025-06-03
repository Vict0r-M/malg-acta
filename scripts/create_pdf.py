from weasyprint import HTML
from datetime import datetime
from datetime import timedelta
import json
import os

def computeNeededResults(dataObject):
        baseObj={
                "probe_date": dataObject["probe_date"], 
                "beneficiar": dataObject["beneficiar"], 
                "clasa_betonului": dataObject["clasa_betonului"], 
                "numar_teste": dataObject["numar_teste"], 
                "internal_code": dataObject["internal_code"],
                "try_date": dataObject["try_date"]
        }
        avgWeight = 0
        avgDensity = 0
        avgPressure = 0
        avgForce = 0
        tests=[]
        for i in range(0,dataObject["numar_teste"]):
                test = {
                        "weight" : float(dataObject["tests"][i]["scale_data"].split(" ")[0])/1000,
                        "force" : float(dataObject["tests"][i]["compression_data"]["kN"])*1000
                }
                test["density"] = (test["weight"]*(100*100*100))/(15*15*15)
                test["pressure"] = test["force"]/22500
                avgWeight = avgWeight + test["weight"]
                avgDensity = avgDensity + test["density"]
                avgPressure = avgPressure + test["pressure"]
                avgForce = avgForce + test["force"]
                test["weight"] =str(round(test["weight"],5))
                test["force"] = str(int(test["force"]))
                test["density"] = str(round(test["density"],2))
                test["pressure"] = str(round(test["pressure"],2))
                tests.append(test)
        avgWeight = avgWeight / dataObject["numar_teste"]
        avgDensity = avgDensity / dataObject["numar_teste"]
        avgPressure = avgPressure / dataObject["numar_teste"]
        avgForce = avgForce / dataObject["numar_teste"]
        
        test = {
                "weight" : avgWeight,
                "density" : avgDensity,
                "force" : avgForce,
                "pressure" : avgPressure
        }
        test["weight"] =str(round(test["weight"],5))
        test["force"] = str(int(test["force"]))
        test["density"] = str(round(test["density"],2))
        test["pressure"] = str(round(test["pressure"],2))
        tests.append(test)
        
        baseObj["tests"] = tests
        return baseObj

#def computeTryDate(probe_date):
#        date_obj = datetime.strptime(probe_date,'%d.%m.%Y').date() 
#        date_obj = date_obj + timedelta(days=28)
#        return date_obj.strftime('%d.%m.%Y')

def printPDFV2(dataObject):
        baseObj = computeNeededResults(dataObject)
        try_date = dataObject["try_date"]
        testNumber=dataObject["numar_teste"]
        htmlTemplate = '''<html style="
        size: a4;
        "><head>
        <style type="text/css" id="operaUserStyle">
                @page {
                size: A4; /* Change from the default size of A4 */
                margin: 10mm; /* Set margin on each page */
                </style>
        </head>

        <body style="
        }">
        <header style="font-size: 11pt;"><b> PILOT 4, Model 50 - C4642 Serial Nr. 12010780 </b><br>
        </header>
        
        <div>
                <b style="
                        font-size: 13pt;
                        ">
                <p>Rezultatele încercării:</p>
                </b>
                <table style="line-height: 15pt;
                margin:auto;border-collapse: collapse;text-align: center;">
                <tbody style="border: 0.5pt black solid;">
                        <tr style="
                                border: 2pt black solid;
                                ">
                        <td colspan="3" style="
                                border-top: hidden;
                                border-left: hidden;
                                "> Indicativ Proba '''+str(baseObj["internal_code"])+'''</td>'''
                                
        for i in range(1,testNumber+1):
                htmlTemplate=htmlTemplate+'''
                        <td style="
                                border: inherit ;
                                ">'''+str(baseObj["internal_code"])+'''/'''+str(i)+'''</td>'''
        htmlTemplate=htmlTemplate+'''
                        <td style="
                                border-collapse: collapse;
                                border: inherit;
                                ">Media</td>
                        </tr>
                        <tr style="
                                border-collapse: collapse;
                                border: inherit;
                                ">
                        <td colspan="3" style="border: 2pt black solid">Data confecționării</td>
                        <td colspan="'''+str(testNumber+1)+'''" style="
                                border-collapse: collapse;
                                border: inherit;
                                ">'''+ dataObject["probe_date"]+'''</td>
                        </tr>
                        <tr style="
                                border: inherit;
                                ">
                        <td colspan="3" style="border: 2pt black solid">Data încercării</td>
                        <td colspan="'''+str(testNumber+1)+'''" style="
                                border: inherit;
                                ">''' + try_date +'''</td>
                        </tr>
                        
                        <tr style="
                                border: inherit;
                                ">
                        <td rowspan="3" colspan="2" style="border: 2pt black solid">Dimensiunile Cubului</td>
                        <td style="border: 2pt black solid">x [mm]</td>'''
        for i in range(1,testNumber+2):                
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">150</td>'''
        htmlTemplate = htmlTemplate + '''</tr>
                        <tr style="
                                border: inherit;
                                ">
                        <td style="border: 2pt black solid">y [mm]</td>'''
        for i in range(1,testNumber+2):                
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">150</td>'''
        htmlTemplate = htmlTemplate + '''</tr>
                                <tr style="
                                border: inherit;
                                ">
                        <td style="border: 2pt black solid">z [mm]</td>'''
        for i in range(1,testNumber+2):                
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">150</td>'''
        htmlTemplate = htmlTemplate + '''</tr>
                        <tr style="
                                border: inherit;
                                ">
                        <td colspan="3" style="border: 2pt black solid">Suprafața de compresiune [mm²]</td>'''
        for i in range(1,testNumber+2):                
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">&nbsp;22500&nbsp;</td>'''
        htmlTemplate=htmlTemplate+'''</tr>
                        <tr style="
                                border: inherit;
                                ">
                        <td colspan="3" style="border: 2pt black solid">Greutatea cubului [Kg]</td>'''
        for i in range(0,testNumber+1):                
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">''' + baseObj["tests"][i]["weight"] +'''</td>'''
                      
        htmlTemplate=htmlTemplate+'''</tr>
                        <tr style="
                                border: inherit;
                                ">
                        <td colspan="3" style="border: 2pt black solid">Densitatea specifică aparentă [Kg/m³]</td>'''
        for i in range(0,testNumber+1):                
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">''' + baseObj["tests"][i]["density"] +'''</td>'''
                        
        htmlTemplate=htmlTemplate+'''</tr>
                        <tr style="
                                border: inherit;
                                ">
                        <td colspan="3" style="border: 2pt black solid">Sarcina de rupere la compresiune [N]</td>'''
        for i in range(0,testNumber+1):
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">''' + baseObj["tests"][i]["force"] +'''</td>'''
                        
        htmlTemplate=htmlTemplate+'''</tr>
                        <tr style="
                                border: inherit;
                                ">
                        <td colspan="3" style="border: 2pt black solid">Rezistența de rupere la compresiune [N/mm²]
                        </td>'''
        for i in range(0,testNumber+1):                
                htmlTemplate=htmlTemplate+'''<td style="
                                border: inherit;
                                ">''' + baseObj["tests"][i]["pressure"] +'''</td>'''
                        
        htmlTemplate=htmlTemplate+'''</tr>
                </tbody>
                </table>
                
        </div>


        </body></html>'''
        html=HTML(string=htmlTemplate)
        filename = "{}_{}_{}.pdf".format(
                dataObject["beneficiar"].replace(" ", "_"),
                dataObject["internal_code"],
                dataObject["clasa_betonului"].replace("/", "_").replace(" ", "_")
        )
        # Construct the relative path to the 'rapoarteGenerate' folder
        target_folder = "rapoarteGenerate"
        target_path = os.path.join(target_folder, filename)

        # Ensure that the target directory exists
        os.makedirs(target_folder, exist_ok=True)

        # Write the PDF to the target path
        html.write_pdf(target_path, presentational_hints=True)

def test_pdf():     
        dataJSON='''{
                "probe_date": "20.06.1975", 
                "beneficiar": "AGREMIN SRL", 
                "clasa_betonului": "C 25.0/30", 
                "numar_teste": 2, 
                "tests": [
                {
                        "scale_data": "7548.5 g H", 
                        "compression_data": {
                        "kN": "00663.3", 
                        "MPa": "0029.48"
                        }
                }, 
                {
                        "scale_data": "7538.5 g H", 
                        "compression_data": 
                        {
                        "kN": "00583.4",
                        "MPa": "0025.93"
                        }
                }],
                "internal_code": "123",
                "try_date": "04.02.2025"
        }'''
        test_data=json.loads(dataJSON)
        printPDFV2(test_data)

if __name__ == "__main__":
        test_pdf()