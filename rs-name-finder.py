import pandas as pd
import concurrent.futures
import requests
import time
import os
import re

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

RS3_Base_URL = "https://services.runescape.com/m=hiscore/index_lite.ws?player="
OSRS_Base_URL = "https://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player="

NameListFile = os.getcwd() + "/names-list.txt"
# AvaNames = os.getcwd() + "/Available_Names.txt"
time1 = None
time2 = None

out = []
CONNECTIONS = 25
TIMEOUT = 30

RS3_URL_List = list() # List of RS3 URLs to check the status for
RS3_NameNotFound = list() # List of RS3 names that don't exist: responded 404 | We then check OSRS HS for these names
RS3_Conn_Rej = list() # List of RS3 names that had their request rejected: responded 503
RS3_Name_Exists = list() # List of RS3 names that exist: responded 200
RS3_RunTime = None # in seconds

OSRS_URL_List = list() # List of all OSRS URLs to check, this one should only fill as we run into 404 responses from the RS3 list
OSRS_NameNotFound = list() # List of RS3 names that don't exist: responded 404 | We then check OSRS HS for these names
OSRS_Conn_Rej = list() # List of RS3 names that had their request rejected: responded 503
OSRS_Name_Exists = list() # List of RS3 names that exist: responded 200
OSRS_RunTime = None # in seconds
cls()
print("Preparing web requests...")

with open(NameListFile, 'r') as NameList:
    for name in NameList:
        RS3_URL_List.append(RS3_Base_URL + name)

print("Loaded " + str(len(RS3_URL_List)) + " RS3 names to check...")

def load_url(url, timeout):
    mode = None
    if ("hiscore_oldschool" in str(url)):
        mode = "OSRS"
    else:
        mode = "RS3"

    ans = requests.get(url, timeout=timeout)
    
    try:
        name = url.split("player=")
        #print("[" + str(ans) + "] Username potentiall available: " + name)

        if ("503" in str(ans)): # .......................... Service Unavailable (prolly too many requests)
            if (mode == "RS3"):
                RS3_Conn_Rej.append(name[1])
            else:
                OSRS_Conn_Rej.append(name[1])

        elif ("404" in str(ans)): # ........................ Doesn't exist on RS3 HS
            if (mode == "RS3"):
                RS3_NameNotFound.append(name[1])
                OSRS_URL_List.append(OSRS_Base_URL + name[1])
            else:
                OSRS_NameNotFound.append(name[1])

        elif ("200" in str(ans)): # ........................ Exists
            if (mode == "RS3"):
                RS3_Name_Exists.append(name[1]) 
            else:
                OSRS_Name_Exists.append(name[1])
        else:
            print("Not 200/404/503: " + str(ans))
    except:
        print("[" + str(ans) + "] Exception: " + str(url))
    finally:
        return ans #+ " - " + name[1] #.status_code

def CheckForNames(url_list, gamemode="RS3"):
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        future_to_url = (executor.submit(load_url, url, TIMEOUT) for url in url_list)
        time1 = time.time()
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
            except Exception as exc:
                data = str(type(exc))
            finally:
                out.append(data)
                
                if (gamemode == "RS3"):
                    print("[RS3] Names Checked: " + str(len(out)) + " | Exist: " + str(len(RS3_Name_Exists)) + " | Don't Exist: " + str(len(RS3_NameNotFound)) + " | Rejected: " + str(len(RS3_Conn_Rej)),end="\r")
                else:
                    print("[OSRS] Names Checked: " + str(len(out)) + " | Exist: " + str(len(OSRS_Name_Exists)) + " | Don't Exist: " + str(len(OSRS_NameNotFound)) + " | Rejected: " + str(len(OSRS_Conn_Rej)),end="\r")
                
    time2 = time.time()

    if (gamemode == "RS3"):
        RS3_RunTime = round(time2-time1, 2)
        print("\n")
        print(str(len(RS3_URL_List)) + " RS3 name checks, total response time: " + str(RS3_RunTime) + " seconds\n\n")
        print("Non-Existing RS3 names:\t\t" + str(len(RS3_NameNotFound)))
        print("Rejected RS3 name checks:\t" + str(len(RS3_Conn_Rej)))
        print("Number of names on the RS3 HS:\t" + str(len(RS3_Name_Exists)))
        print("\n")
        print("Because " + str(len(RS3_NameNotFound)) + " names weren't found on the RS3 highscores, we'll check them on the OSRS highscores")
        print("\n")
        DumpRS3Data()
        out.clear()
        input("Press enter to start the OSRS highscore check...")
        CheckForNames(OSRS_URL_List, gamemode="OSRS")
    else:
        OSRS_RunTime = round(time2-time1, 2)
        print("\n")
        print(str(len(OSRS_URL_List)) + " OSRS name checks, total response time: " + str(OSRS_RunTime) + " seconds\n\n")
        print("Non-Existing OSRS names:\t" + str(len(OSRS_NameNotFound)))
        print("Rejected OSRS name checks:\t" + str(len(OSRS_Conn_Rej)))
        print("Number of names on the OSRS HS:\t" + str(len(OSRS_Name_Exists)))
        DumpOSRSData()

        NameCheckRequests = len(RS3_URL_List) + len(OSRS_URL_List)
        print("\n")
        print("Checked a total of " + str(NameCheckRequests) + " names")


    #print(str(len(RS3_URL_List)) + " name checks, total response time: "f'Took {time2-time1:.2f} seconds' + "\n\n")
    #print("Taken Names:\t\t\t" + str(len(RS3_Name_Exists)))
    #print(pd.Series(out).value_counts())
    #print(f'Took {time2-time1:.2f} s')
    
    #cls()
    #CheckForNames(RS3_Rej_URL_List)

# RS3 Dump
def DumpRS3Data():
    # Names Not Found
    with open(os.getcwd() + "/RS3_Data/Undetected_Names.txt", 'w') as out:
        for name in RS3_NameNotFound:
            out.write(name)

    # Names Rejected
    with open(os.getcwd() + "/RS3_Data/Rejected_Names.txt", 'w') as out:
        for name in RS3_Conn_Rej:
            out.write(name)

    # Names Found
    with open(os.getcwd() + "/RS3_Data/Detected_Names.txt", 'w') as out:
        for name in RS3_Name_Exists:
            out.write(name)

# OSRS Dump
def DumpOSRSData():
    # Names Not Found
    with open(os.getcwd() + "/OSRS_Data/Undetected_Names.txt", 'w') as out:
        for name in OSRS_NameNotFound:
            out.write(name)

    # Names Rejected
    with open(os.getcwd() + "/OSRS_Data/Rejected_Names.txt", 'w') as out:
        for name in OSRS_Conn_Rej:
            out.write(name)

    # Names Found
    with open(os.getcwd() + "/OSRS_Data/Detected_Names.txt", 'w') as out:
        for name in OSRS_Name_Exists:
            out.write(name)

CheckForNames(RS3_URL_List)