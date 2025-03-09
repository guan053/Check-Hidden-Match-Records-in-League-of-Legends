# -*- coding: gbk -*-
import tkinter as tk
import psutil
import base64
import requests
import yaml
import urllib3
import io
from PIL import Image, ImageTk

# ����ssl����
urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)

# �����̣���ȡ�˿ں�token
cmds = []
for process in psutil.process_iter():
    if process.name().removesuffix(".exe") == "LeagueClientUx":
        cmds = process.cmdline()
        break
token = None
port = None
for cmd in cmds:
    ary = cmd.split("=")
    if ary[0] == "--remoting-auth-token":
        token = ary[1]
    if ary[0] == "--app-port":
        port = ary[1]

if token and port:
    tokens = base64.b64encode(("riot:%s" % token).encode())
    author = {"Authorization": "Basic %s" % tokens.decode()}

    # ��ѯ��ǰ�ٻ�ʦ
    result = requests.get(
        url="https://127.0.0.1:" + port + "/lol-summoner/v1/current-summoner",
        headers=author,
        verify=False
    )
    if result.status_code == 200:
        result.encoding = "utf-8"
        userinfo = yaml.load(result.text, Loader=yaml.FullLoader)
        result.close()

    userimg = 'https://wegame.gtimg.com/g.26-r.c2d3c/helper/lol/assis/images/resources/usericon/%s.png' % (
        userinfo['profileIconId'])

    result = requests.get(
        url="https://127.0.0.1:" + port + "/lol-ranked/v1/ranked-stats/%s" % (userinfo['puuid']),
        headers=author,
        verify=False
    )
    if result.status_code == 200:
        result.encoding = "utf-8"
        rank_info = yaml.load(result.text, Loader=yaml.FullLoader)
        result.close()

    result = requests.get(
        url="https://127.0.0.1:" + port + "/lol-match-history/v1/products/lol/%s/matches" % userinfo['puuid'],
        headers=author,
        verify=False
    )
    if result.status_code == 200:
        result.encoding = "utf-8"
        match_history = yaml.load(result.text, Loader=yaml.FullLoader)
        result.close()

    # ����������
    root_window = tk.Tk()
    root_window.title('С�ز�ѯ���֣�vxG2603004227��')
    root_window.geometry('400x200')
    root_window.resizable(0, 0)

    # ��ʾ�ٻ�ʦͷ��
    image_bytes = requests.get(userimg).content
    data_stream = io.BytesIO(image_bytes)
    pil_image = Image.open(data_stream)
    tk_image = ImageTk.PhotoImage(pil_image)
    lab1 = tk.Label(root_window, image=tk_image)
    lab1.pack()

    #  ��ʾ�ٻ�ʦ����
    lab2 = tk.Label(root_window, text=userinfo["displayName"])
    lab2.pack()

    #  ��ʾ�ٻ�ʦ��˫��λ
    lab3 = tk.Label(root_window, text=rank_info["queueMap"]['RANKED_SOLO_5x5']['tier'])
    lab3.pack()

    # ��ʾ������
    name_entry = tk.Entry(root_window)
    name_entry.pack()


    # ������ť�󶨺���
    def search():
        name = name_entry.get()
        print(name)

        result = requests.get(
            url="https://127.0.0.1:" + port + "/lol-summoner/v1/summoners/",
            headers=author,
            params={'name': name},
            verify=False,
        )
        s_info = yaml.load(result.text, Loader=yaml.FullLoader)
        search_puuid = s_info['puuid']
        result.close()

        result = requests.get(
            url="https://127.0.0.1:" + port + "/lol-match-history/v1/products/lol/%s/matches" % search_puuid,
            headers=author,
            params={'begIndex': 0, 'endIndex': 8},
            verify=False,
        )
        his_info = yaml.load(result.text, Loader=yaml.FullLoader)
        print(his_info)
        result.close()

        newWindow = tk.Toplevel(root_window)
        newWindow.title('(%s)��ս��' % name)
        newWindow.geometry('400x200')
        newWindow.resizable(0, 0)

        # ��� 'games' ���Ƿ����
        games = his_info.get('games')
        if games and 'games' in games:
            for i in games['games']:
                start_time = i["gameCreationDate"][0:10]
                champ_id = i["participants"][0]["championId"]

                result = requests.get(
                    url="https://127.0.0.1:" + port + "/lol-champ-select/v1/grid-champions/"
                        + str(i['participants'][0]['championId']),
                    headers=author,
                    verify=False,
                )
                champion = "[" + result.json()['name'] + "]"
                result.close()
                gamemode = i["gameMode"]
                kill = i["participants"][0]["stats"]["kills"]
                deaths = i["participants"][0]["stats"]["deaths"]
                assists = i["participants"][0]["stats"]["assists"]
                w_d = i["participants"][0]["stats"]['win']

                if w_d:
                    wd = "ʤ"
                else:
                    wd = "��"

                output = start_time + '\t' + wd + '\t' + str(kill) + '/' + str(deaths) + '/' + str(
                    assists) + '\t' + gamemode + "\t " + champion
                out_lab = tk.Label(newWindow, text=output, anchor="nw")
                out_lab.pack()
        else:
            # ����û����Ϸ��¼�����
            no_record_label = tk.Label(newWindow, text="û���ҵ���Ϸ��¼", anchor="nw")
            no_record_label.pack()


    # ��ʾ������ť
    search_button = tk.Button(root_window, text='��ѯ', command=search)
    search_button.pack()

    # ��������
    root_window.mainloop()