import csv
import zipfile
import time
import random
import string
import requests
import os.path
import threading
import imaplib
import getpass, os, imaplib, email
import tkinter as tk
import names
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from email.parser import HeaderParser
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from random import randint
import pyotp


####################################
##        Created by Mufasa       ##
##         10 January 2020        ##
##  Last Change 11 January 2020   ##
####################################


def read_import_data():
    '''
    This is function to read data 
    
    # no input parameter
    '''
    with open('import.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        global list_task
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                task = {}
                task['email'] = row[0]
                task['origin_password'] = row[1]
                task['new_password'] = row[2]
                task['enable_gauth'] = row[3]
                list_task.append(task)
                line_count += 1
        print(f'Processed {line_count} lines.')

def Create_driver(address = "23.88.195.47:23667", username = "mare", userpass = "WuBA8ujAD"):
    proxy = {'address': address,
            'username': username,
            'password': userpass}

    capabilities = dict(DesiredCapabilities.CHROME)
    capabilities['proxy'] = {'proxyType': 'MANUAL',
                            'httpProxy': proxy['address'],
                            'ftpProxy': proxy['address'],
                            'sslProxy': proxy['address'],
                            'noProxy': '',
                            'class': "org.openqa.selenium.Proxy",
                            'autodetect': True}


    # capabilities['proxy']['socksUsername'] = proxy['username']
    # capabilities['proxy']['socksPassword'] = proxy['password']

    options = Options()
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors", "safebrowsing-disable-download-protection", "safebrowing-disable-auto-update", "disable-client-side-phishing-detection"])
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=default')
    options.add_argument('--incognito')
    options.add_argument('--disable-plugin-discovery')
    options.add_argument('--start-maximized')
    options.add_argument("--enable-automation")
    options.add_argument("--test-type=browser")
    if(address == ":"):
        driver = webdriver.Chrome(executable_path="chromedriver", options = options)
    else:
        driver = webdriver.Chrome(executable_path="chromedriver", options = options,desired_capabilities=capabilities)
    # desired_capabilities=capabilities
    time.sleep(3)
    
    return driver

def report_to_a(filename,data):
    with open("%s.txt"%filename,"a") as f:
        f.write(data)

def read_proxy_data():
    with open('proxy.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        global list_proxy
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                proxy = {}
                proxy['IP'] = row[0]
                proxy['Port'] = row[1]
                list_proxy.append(proxy)
                line_count += 1
        print(f'Processed {line_count} lines.')


def save_all_data(Email = "", password = "",  new_password = "", EnableGauth = "", DeleteTrust = "",security_key = "",status = ""):
    '''
    This is function to save result data
    
    # Email: account Email
    # Password: account password(Old)
    # New Password: account new Password
    # EnableGauth
    # DeleteTrust: Flag of delete device(0 or 1)
    # status: result of account
    '''
    upgrade_status("[:--->> Saving result data...")
    write_header = False
    if not os.path.exists('result.csv'):
        write_header = True
    with open('result.csv', 'a', newline='') as csvfile:

        fieldnames = ['Email','Password', 'New Password','EnableGauth','DeleteTrust','Security key','Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({'Email' : Email,'Password': password, 'New Password': new_password,'EnableGauth':EnableGauth,'DeleteTrust': DeleteTrust,'Security key':security_key,'Status':status})

def email_verify():
    '''
    This is function to get verify code
    
    # no input parameter
    '''
    try:
        conn = imaplib.IMAP4_SSL(host='ha01s015.org-dns.com')
        (retcode, capabilities) = conn.login("fifa@liveemail24.de","o17*7pwE")
    
    except:
        return "Error Log in"
    init_amount = 0
    comming = False
    for i in range(20):
        # conn.select(readonly = 1)
        time.sleep(3)
        typ, mcount = conn.select("Inbox")
        (retcode, message) = conn.search(None,'(UNSEEN)')
        print(int(mcount[0]))
        print(message[0])
        mail_ids = []
        for block in message:
            mail_ids += block.split()
        if comming and len(mail_ids) !=0:
            break
        if len(mail_ids) == 0:
            comming = True
        if init_amount !=0 and init_amount !=len(mail_ids):
            break
        init_amount = len(mail_ids)
    if len(mail_ids) == 0:
        return "Error No Email Received"

    success = False
    code = ""
    for i in mail_ids:
        conn.store(i, '+FLAGS', '\Seen') 
        status, data = conn.fetch(i, '(RFC822)')
        # print(data)
        
        link = None
        try:
            if "Dein EA-Sicherheitscode:" in str(data):
                report_to_a("email",str(data))
                print("3")
                code = str(data).split("Dein EA-Sicherheitscode lautet: ")[1].replace("\\n","").replace("\\r","").split('Date')[0].split(' ')[-1]
                print("4")
                success = True
                print(code)
            elif  "Your EA Security Code:" in str(data):
                report_to_a("email",str(data))
                print("1")
                code = str(data).split("Your EA Security Code")[1].replace("\\n","").replace("\\r","").split('Date')[0].split(' ')[-1]
                print("2")
                success = True
                print(code)
                # return link
            
        except:
            print("invalid format")
        conn.store(i, '+FLAGS', '\Seen')
        
    print("1",code)

    if success:
        return code
    return "Error Verification Failed"

def export_blocked_proxy(data):
    '''
    This is function to save crashed proxy list

    # data- list of crashed proxy
    '''

    with open("blocked_proxy.txt","a") as f:
        f.write("\n")
        f.write(data)

def upgrade_status(status):
    '''
    This is function to show off current status to UI
    
    # status: string - data to show
    '''

    print(status)
    T.insert(END, status +  "\n")
    T.see("end")
    root.update_idletasks()


def disable_status():

    Btn_start['state'] = 'disable'


def enable_status():
    Btn_start['state'] = 'normal'

def page_one(driver,task):
    '''
    This is function to login to EA

    # driver-chrome selenium driver
    # task-account info
    
    '''
    email = task["email"]
    password = task["origin_password"]
    new_password = task["new_password"]
    while True:
            try:
                input_email = driver.find_element_by_xpath('//*[@id="email"]')
                break
            except:
                time.sleep(2)
    input_password = driver.find_element_by_xpath('//*[@id="password"]')
    btn_login = driver.find_element_by_xpath('//*[@id="btnLogin"]')
    input_email.send_keys(email)
    input_password.send_keys(password)
    btn_login.click()

    time.sleep(3)
    try:
        error_msg = driver.find_element_by_xpath('//*[@id="loginForm"]/div[1]/div/div').get_attribute('innerHTML')
        print(error_msg)
        return "Error Wrong Password"
    except:
        pass
    start = time.time()
    no_verify = False
    while True:
        if (time.time()-start )> 5:
            no_verify = True
            break
        
        try:
            send_key = driver.find_element_by_xpath('//*[@id="btnSendCode"]')
            break
        except:
            time.sleep(2)
    if no_verify:
        return "Success"
    send_key.click()
    upgrade_status("sending code")
    verify_code = email_verify()
    if "Error" in verify_code:
        return "Error wrong code"
    if len(verify_code) != 6:
        upgrade_status("Error. Falue verify :%s"%verify_code)
        return "Error. Falue verify"
    input_veriycode = driver.find_element_by_xpath('//*[@id="oneTimeCode"]')
    input_veriycode.send_keys(verify_code)
    btn_verify = driver.find_element_by_xpath('//*[@id="btnSubmit"]')
    btn_verify.click()

    return "Success"
def page_two(driver, task):
    '''
    This is function to change password
     
    # driver-chrome selenium driver
    # task-account info
    '''
    email = task["email"]
    password = task["origin_password"]
    new_password = task["new_password"]

    while True:
        try:
            btn_security = driver.find_element_by_xpath('//*[@id="nav_security"]')
            break
        except:
            time.sleep(2)
    btn_security.click()

    while True:
        try:
            btn_edit_password = driver.find_element_by_xpath('//*[@id="editSecuritySection2"]')
            break
        except:
            time.sleep(2)
    btn_edit_password.click()
    time.sleep(2)
    while True:
        try:
            btn_send_code = driver.find_element_by_xpath('//*[@id="continuebtn_mfa_send_code"]')
            break
        except:
            time.sleep(2)
    btn_send_code.click()
    verifycode = email_verify()
    if "Error" in verifycode:
        return "Error wrong code"
    if len(verifycode) != 6:
        return "Error. Falue Verify"
    time.sleep(2)
    input_code = driver.find_element_by_xpath('//*[@id="mfa_code_input"]')
    input_code.send_keys(verifycode)
    btn_sumit = driver.find_element_by_xpath('//*[@id="submitbtn_mfa_verify_code"]')
    btn_sumit.click()
    time.sleep(2)
    input_original_password = driver.find_element_by_xpath('//*[@id="originalPassword"]')
    input_new_password = driver.find_element_by_xpath('//*[@id="newPassword"]')
    input_confirm_password = driver.find_element_by_xpath('//*[@id="newPasswordR"]')
    input_original_password.send_keys(password)
    input_new_password.send_keys(new_password)
    input_confirm_password.send_keys(new_password)
    btn_save = driver.find_element_by_xpath('//*[@id="savebtn_cpass"]')
    btn_save.click()

    return "Success"
def page_three(driver):
    '''
    This is function to enable gauth.
    
    '''
    print("P")
    while True:
        try:
            btn_security = driver.find_element_by_xpath('//*[@id="nav_security"]')
            break
        except:
            time.sleep(2)
    driver.execute_script("arguments[0].click();", btn_security)
    start = time.time()
    time.sleep(3)
    try:
        btn_on = driver.find_element_by_xpath('//*[@id="twofactoronbtn"]/span').get_attribute('innerHTML')
        print(btn_on)
        return "Already OFF"
    except:
        off = False
        while True:
            if (time.time()-start )> 5:
                off = True
                break
            try:
                btn_turn_off = driver.find_element_by_xpath('//*[@id="twofactoroffbtn"]')
                break
            except:
                time.sleep(2)
        print("on->off")
        driver.execute_script("arguments[0].click();", btn_turn_off)
        while True:
            try:
                btn_send_code = driver.find_element_by_xpath('//*[@id="continuebtn_mfa_send_code"]')
                break
            except:
                time.sleep(2)
        driver.execute_script("arguments[0].click();", btn_send_code)
        print(6)
        while True:
            try:
                input_verifycode = driver.find_element_by_xpath('//*[@id="mfa_code_input"]')
                break
            except:
                time.sleep(2)
        code = email_verify()
        if "Error" in code:
            return "Error wrong code"
        input_verifycode.send_keys(code)
        btn_continue = driver.find_element_by_xpath('//*[@id="submitbtn_mfa_verify_code"]')
        btn_continue.click()
        print(7)
        while True:
            try:
                btn_ok = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_turnoff"]')
                break
            except:
                time.sleep(2)
        driver.execute_script("arguments[0].click();", btn_ok)
        print(8)
        time.sleep(2)
        # btn_logout = driver.find_element_by_xpath('//*[@id = "logout"]')
        # driver.execute_script("arguments[0].click();", btn_logout)
        return "Success"
    
    # else:
    # print("off->on")
    # driver.execute_script("arguments[0].click();", btn_turn_off)
    # start = time.time()
    # require_verify = True
    # while True:
    #     if (time.time() - start )> 5:
    #         require_verify = False
    #         break
    #     try:
    #         btn_send_code = driver.find_element_by_xpath('//*[@id="continuebtn_mfa_send_code"]')
    #         break
    #     except:
    #         time.sleep(2)
    # print(1)
    # if require_verify :
    #     driver.execute_script("arguments[0].click();", btn_send_code)
    #     while True:
    #         try:
    #             input_verifycode = driver.find_element_by_xpath('//*[@id="mfa_code_input"]')
    #             break
    #         except:
    #             time.sleep(2)
    #     code = email_verify()
    #     input_verifycode.send_keys(code)
    #     btn_continue = driver.find_element_by_xpath('//*[@id="submitbtn_mfa_verify_code"]')
    #     btn_continue.click()
    # print(2)
    # time.sleep(2)
    # try:
    #     driver.execute_script("arguments[0].click();", btn_turn_off)
    # except:
    #     pass
    # while True:
    #     try:
    #         radio_email = driver.find_element_by_xpath('//*[@id="emailradiolabel"]')
    #         break
    #     except:
    #         time.sleep(2)
    # driver.execute_script("arguments[0].click();", radio_email)
    # btn_continue = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_turnon"]')
    # driver.execute_script("arguments[0].click();", btn_continue)
    # verify_code = email_verify()
    # print(3)
    # while True:
    #     try:
    #         input_code = driver.find_element_by_xpath('//*[@id="twofactorCode"]')
    #         break
    #     except:
    #         time.sleep(2)
    # print(4)
    # input_code.send_keys(verify_code)
    # btn_continue = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_verifycode"]')
    # driver.execute_script("arguments[0].click();", btn_continue)

    # #Off finish
    # while True:
    #     try:
    #         btn_turn_on = driver.find_element_by_xpath('//*[@id="twofactoronbtn"]')
    #         break
    #     except:
    #         time.sleep(2)
    # driver.execute_script("arguments[0].click();", btn_turn_on)
    # while True:
    #     try:
    #         radio_email = driver.find_element_by_xpath('//*[@id="emailradiolabel"]')
    #         break
    #     except:
    #         time.sleep(2)
    # driver.execute_script("arguments[0].click();", radio_email)
    # btn_continue = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_turnon"]')
    # driver.execute_script("arguments[0].click();", btn_continue)
    # verify_code = email_verify()
    # print(31)
    # while True:
    #     try:
    #         input_code = driver.find_element_by_xpath('//*[@id="twofactorCode"]')
    #         break
    #     except:
    #         time.sleep(2)
    # print(41)
    # input_code.send_keys(verify_code)
    # btn_continue = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_verifycode"]')
    # driver.execute_script("arguments[0].click();", btn_continue)

    # while True:
    #     try:
    #         btn_close = driver.find_element_by_xpath('//*[@id="cancelbtn_twofactor_backupcodes"]')
    #         break
    #     except:
    #         time.sleep(2)
    # driver.execute_script("arguments[0].click();", btn_close)
    # # end turn on
# def turn_on_gauth(driver):
#     while True:
#         try:
#             btn_security = driver.find_element_by_xpath('//*[@id="nav_security"]')
#             break
#         except:
#             time.sleep(2)
#     driver.execute_script("arguments[0].click();", btn_security)
#     while True:
#         try:
#             btn_turn_on = driver.find_element_by_xpath('//*[@id="twofactoronbtn"]')
#             break
#         except:
#             time.sleep(2)
#     driver.execute_script("arguments[0].click();", btn_turn_on)
#     while True:
#         try:
#             btn_send = driver.find_element_by_xpath('//*[@id="continuebtn_mfa_send_code"]')
#             break
#         except:
#             time.sleep(2)
#     driver.execute_script("arguments[0].click();", btn_send)
#     verify_code = email_verify()
#     while True:
#         try:
#             input_code = driver.find_element_by_xpath('//*[@id="mfa_code_input"]')
#             break
#         except:
#             time.sleep(2)
#     input_code.send_keys(verify_code)
#     time.sleep(2)
#     btn_continue = driver.find_element_by_xpath('//*[@id="submitbtn_mfa_verify_code"]')
#     driver.execute_script("arguments[0].click();", btn_continue)

#     print(9)
#     while True:
#         try:
#             radio_email = driver.find_element_by_xpath('//*[@id="emailradiolabel"]')
#             break
#         except:
#             time.sleep(2)
#     driver.execute_script("arguments[0].click();", radio_email)
#     btn_continue = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_turnon"]')
#     driver.execute_script("arguments[0].click();", btn_continue)
#     verify_code = email_verify()
#     print(10)
#     while True:
#         try:
#             input_code = driver.find_element_by_xpath('//*[@id="twofactorCode"]')
#             break
#         except:
#             time.sleep(2)
#     input_code.send_keys(verify_code)
#     time.sleep(2)
#     btn_continue = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_verifycode"]')
#     driver.execute_script("arguments[0].click();", btn_continue)
#     print(11)
#     while True:
#         try:
#             btn_close = driver.find_element_by_xpath('//*[@id="cancelbtn_twofactor_backupcodes"]')
#             break
#         except:
#             time.sleep(2)
#     time.sleep(1)
#     driver.execute_script("arguments[0].click();", btn_close)
#     print(12)
#     while True:
#         try:
#             btn_switch = driver.find_element_by_xpath('//*[@id="authenticator_switch_link"]')
#             break
#         except:
#             time.sleep(2)
#     driver.execute_script("arguments[0].click();", btn_switch)
#     while True:
#         try:
#             btn_continue = driver.find_element_by_xpath('//*[@id="setup_authenticator_turnon"]')
#             break
#         except:
#             time.sleep(1)
#     driver.execute_script("arguments[0].click();", btn_continue)
#     print(6)
#     while True:
#         try:
#             security_key = driver.find_element_by_xpath('//*[@id="tfa_qrcode_secretKey"]/strong').get_attribute('innerHTML')
#             break
#         except:
#             time.sleep(1)
#     print(security_key)

#     totp = pyotp.TOTP(security_key.replace(" ",""))
#     verify_code = totp.now()
#     print("Current OTP:", totp.now())
#     while True:
#         try:
#             input_verifycode = driver.find_element_by_xpath('//input[@id="twofactorQRCode"]')
#             break
#         except:
#             time.sleep(1)
#     time.sleep(10)
#     input_verifycode.send_keys(str(verify_code))
#     btn_save = driver.find_element_by_xpath('//*[@id="savebtn_twofactor_verifyQRcode"]')
#     driver.execute_script("arguments[0].click();", btn_save)
#     time.sleep(2)
#     try:
#         error_msg = driver.find_element_by_xpath('//*[@id="tfa_invalid_qrcode"]')
#         if error_msg.isDisplayed():
#             return "Verify code Error"
#     except:
#         pass
#     return "Success"



def Start():
    threading.Thread(target=main_loop).start()

def main_loop():
    '''
    This is main thread

    '''
    read_proxy_data()
    disable_status()
    URL = "https://signin.ea.com/p/web2/login?execution=e803193259s1&initref=https%3A%2F%2Faccounts.ea.com%3A443%2Fconnect%2Fauth%3Fclient_id%3Dcustomer_portal%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fmyaccount.ea.com%252Fcp-ui%252Faboutme%252Flogin%26locale%3Den_EN%26state%3DU1RiVVNsQ1Y2U2ZJSzJEdGU6cDJybXQ"
    for task in list_task:
        email = task["email"]
        password = task["origin_password"]
        new_password = task["new_password"]

        proxy_index = randint(0,len(list_proxy)-1)

        while True:
            driver = Create_driver(list_proxy[randint(0,proxy_index)]['IP'] + ":"  + list_proxy[randint(0,proxy_index)]['Port'])
            driver.get(URL)
            time.sleep(5)
            upgrade_status("start")
            try:
                msg_no_internet = driver.find_element_by_xpath('//*[@id="main-message"]/p').get_attribute('innerHTML')
                driver.close()
                upgrade_status(msg_no_internet)
                upgrade_status("Blocked proxy : " + list_proxy[proxy_index]['IP'])
                damaged_proxy_list.append(list_proxy[proxy_index]['IP'])
                while True:
                    proxy_index = randint(0,len(list_proxy)-1)
                    doublicated = False
                    for i in range(len(damaged_proxy_list)):
                        if proxy_index == damaged_proxy_list[i]:
                            doublicated = True
                            break
                    if doublicated == False:
                        break
            except:
                break
        result = page_one(driver,task)
        upgrade_status(result)
        if "Error" in result:
            save_all_data(Email = email,password = password,status = "Error login")
            driver.close()
            continue
        if(password != new_password):
            result = page_two(driver,task)
            upgrade_status(result)
            if "Error" in result:
                save_all_data(Email = email,password = password, status = "Failed on change password")
                driver.close()
                continue
        if task["enable_gauth"] == "1":
            print("run!")
            result = page_three(driver)
            upgrade_status(result)
            if "Error" in result:
                save_all_data(Email = email,password = password, status = "Failed on delete untrust devices")
                driver.close()
                continue
            driver.close()
            # proxy_index = randint(0,len(list_proxy)-1)
            # while True:
            #     driver = Create_driver(list_proxy[randint(0,proxy_index)]['IP'] + ":"  + list_proxy[randint(0,proxy_index)]['Port'])
            #     driver.get(URL)
            #     time.sleep(5)
            #     upgrade_status("start")
            #     try:
            #         msg_no_internet = driver.find_element_by_xpath('//*[@id="main-message"]/p').get_attribute('innerHTML')
            #         driver.close()
            #         upgrade_status(msg_no_internet)
            #         upgrade_status("Blocked proxy : " + list_proxy[proxy_index]['IP'])
            #         damaged_proxy_list.append(list_proxy[proxy_index]['IP'])
            #         while True:
            #             proxy_index = randint(0,len(list_proxy)-1)
            #             doublicated = False
            #             for i in range(len(damaged_proxy_list)):
            #                 if proxy_index == damaged_proxy_list[i]:
            #                     doublicated = True
            #                     break
            #             if doublicated == False:
            #                 break
            #     except:
            #         break
            # driver.get(URL)
            # result = page_one(driver,task)
            # result = turn_on_gauth(driver)
            # if "Error" in result:
            #     save_all_data(Email = email,password = password, status = "Failed on delete untrust devices")
            #     driver.close()
            #     continue

        save_all_data(Email = email,password = password, new_password = new_password, status = result)

    for i in range(len(damaged_proxy_list)):
        export_blocked_proxy(str(damaged_proxy_list[i]))
    file_directory = os.path.dirname(os.path.abspath(__file__))
    upgrade_status("********All task Finished******** \n result data saved in %s \ result.csv"%file_directory)   
    enable_status()


'''
Start of script

Create UI
 # no input parameter
'''
if __name__ == '__main__':

    list_city = []
    list_agent = []
    list_task = []
    list_proxy = []
    damaged_proxy_list = []
    read_import_data()
    city_limit = len(list_city)-1
    print(city_limit)
    root = Tk() 
    root.geometry("700x250")
    root.title("EA Account Manager")
    root.wm_attributes("-topmost", 1)


    root.grid_columnconfigure(0, weight = 1)
    root.grid_columnconfigure(1, weight = 3)
    root.grid_columnconfigure(2, weight = 1)


    Btn_start = Button(root, width = 20, text = "Start", command = lambda: Start() )
    Btn_start.grid( row = 1, column = 2, sticky = W + E)
    Btn_start.grid(padx=30, pady=5)

    Label_status =  Label(root, text="Current status", width = 20)
    Label_status.grid(row = 2, column = 0 , sticky = E)

    output_status = Frame(root,width = 700,height = 10, background = "pink")
    output_status.grid(columnspan = 5, row = 3,rowspan = 8, sticky = W+E,padx=20, pady=5)

    S = Scrollbar(output_status)
    T = Text(output_status, height=10, width=700, state="normal")
    S.pack(side=RIGHT, fill=Y)
    T.pack(side=TOP, fill=Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)


    mainloop()


