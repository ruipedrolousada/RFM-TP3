from flask import Flask, render_template
import re
import urllib.parse

import subprocess




command_output = subprocess.check_output(['netsh', 'wlan', 'show', 'networks', 'mode=bssid']).decode('utf-8')


output_lines = command_output.splitlines()
# Skip the first four rows
output_lines = output_lines[4:]

# Save the command output to a text file
with open('output.txt', 'w') as f:
    f.write('\n'.join(output_lines))

app = Flask(__name__)

info = {}

ssidBestAp = {}# ssid : best signal AP
apsSignal = {}#ssid : {bssid : signal , bssid: signal}


@app.route('/')
def index():
    with open("output.txt", "r") as f:
        lines = f.readlines()

    x = []
    y = []
    curr_ssid = ""
    curr_bssid = ""
    for elem in lines:
        
        if elem == "\n":
            pass
        elif re.search("BSSID", elem):
            aux = elem.split(" : ")
            curr_bssid = aux[0].strip()
            ssid_info = info[curr_ssid]
            aux2 = aux[1].split("\n")
            aux2 = aux2[0]
            ssid_info[curr_bssid] = {"id": aux2}
            
        elif re.match("SSID", elem):
            curr_bssid = ""
            aux = elem.split(" :")
            curr_ssid = aux[0].strip()
            aux2 = aux[1].split("\n")
            aux2 = aux2[0]
            info[curr_ssid] = {"name": aux2}

            apsSignal[curr_ssid] = {}
        elif curr_bssid != "":
            aux = elem.split(" :")
            key = aux[0].strip()
            aux2 = aux[1].split("\n")
            value = aux2[0]
            info_ssid_bssid = info[curr_ssid][curr_bssid]
            info_ssid_bssid[key] = value

            if key == "Signal" :
                signal = value.split("%")
                signal = int(signal[0].strip())
                apsSignal[curr_ssid][curr_bssid] = signal

        else:
            aux = elem.split(" :")
            key = aux[0].strip()
            aux2 = aux[1].split("\n")
            value = aux2[0]
            info_ssid = info[curr_ssid]
            info_ssid[key] = value
            

    

    for k, v in info.items():
        for k1, v1 in v.items():
            if k1 == 'name':
                name = v1
            elif re.match("BSSID", k1):
                if name in ssidBestAp:
                    signal = v1["Signal"].split("%")
                    signal = int(signal[0].strip())
                    if ssidBestAp[name] < signal:
                        ssidBestAp[name] = signal
                else:
                    signal = v1["Signal"].split("%")
                    signal = int(signal[0].strip())
                    ssidBestAp[name] = signal

    sorted_ssidBestAp = dict(sorted(ssidBestAp.items(), key=lambda x: x[1], reverse=True))#ordem decrescente para usar os maiores
    
    for k,v in sorted_ssidBestAp.items() :
        x.append(k)
        y.append(v)
        
    x = x[:5]
    y = y[:5]

    return render_template('index.html', info=info, x=x, y=y)

#print(info)

@app.route('/aps/<path:ssid>')
def aps(ssid):
    ssid_decoded = urllib.parse.unquote(ssid)
    try:
        aps_info = info[ssid_decoded]
        currSSID = apsSignal[ssid_decoded]
        x = list(currSSID.keys())
        y = list(currSSID.values())
        return render_template('aps.html', ssid=ssid_decoded, aps_info=aps_info, x=x,y=y)
    except KeyError:
        return "SSID not found."

if __name__ == '__main__':
    app.run()
