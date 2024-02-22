import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup 
import cv2
import json

class DLStatusChecker:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get('https://parivahan.gov.in/rcdlstatus/?pur_cd=101')

    def get_captcha(self):
        try:
            ele_captcha = self.driver.find_element(By.ID, 'form_rcdl:j_idt39:j_idt44')
            img_captcha_base64 = self.driver.execute_async_script("""
            var ele = arguments[0], callback = arguments[1];
            ele.addEventListener('load', function fn(){
              ele.removeEventListener('load', fn, false);
              var cnv = document.createElement('canvas');
              cnv.width = this.width; cnv.height = this.height;
              cnv.getContext('2d').drawImage(this, 0, 0);
              callback(cnv.toDataURL('image/jpeg').substring(22));
            }, false);
            ele.dispatchEvent(new Event('load'));
            """, ele_captcha)
            with open(r"captcha.jpg", 'wb') as f:
                f.write(base64.b64decode(img_captcha_base64))
            image = cv2.imread("./captcha.jpg") 
            cv2.imshow("Enter this Captcha", image) 
            cv2.waitKey(0) 
            cv2.destroyAllWindows() 
        except Exception as e:
            print(f"Error in get_captcha: {e}")

    def enter_details(self, DL_num, DL_dob, captcha):
        try:
            dl_input = self.driver.find_element(By.XPATH, "/html/body[@id='mymain']/form[@id='form_rcdl']/div[@class='ui-grid ui-grid-responsive']/div[@class='container']/div[@class='top-space bottom-space']/div[@id='form_rcdl:rcdl_pnl']/div[@id='form_rcdl:rcdl_pnl_content']/div[@id='form_rcdl:j_idt20']/div[@class='ui-grid-row bottom-space'][1]/div[@class='ui-grid-col-3']/input[@id='form_rcdl:tf_dlNO']")
            dl_input.send_keys(DL_num) 

            date_input = self.driver.find_element(By.XPATH, "/html/body[@id='mymain']/form[@id='form_rcdl']/div[@class='ui-grid ui-grid-responsive']/div[@class='container']/div[@class='top-space bottom-space']/div[@id='form_rcdl:rcdl_pnl']/div[@id='form_rcdl:rcdl_pnl_content']/div[@id='form_rcdl:j_idt20']/div[@class='ui-grid-row bottom-space'][2]/div[@class='ui-grid-col-3']/span[@id='form_rcdl:tf_dob']/input[@id='form_rcdl:tf_dob_input']")
            self.driver.execute_script("window.scrollBy(0, 400)")
            self.driver.execute_script("arguments[0].removeAttribute('readonly')", date_input)
            date_input.send_keys(DL_dob) 

            captcha_input = self.driver.find_element(By.XPATH, "/html/body[@id='mymain']/form[@id='form_rcdl']/div[@class='ui-grid ui-grid-responsive']/div[@class='container']/div[@class='top-space bottom-space']/div[@id='form_rcdl:rcdl_pnl']/div[@id='form_rcdl:rcdl_pnl_content']/div[@id='form_rcdl:captchaPnl']/div[@class='ui-grid-row bottom-space']/div[@class='ui-grid-col-8 inline-section field-label-mandate']/div[@class='ui-grid-row']/div[@class='ui-grid-col-6']/table[@class='vahan-captcha inline-section']/tbody/tr/td[3]/input[@id='form_rcdl:j_idt39:CaptchaID']")
            captcha_input.send_keys(captcha) 

            check_status_button = self.driver.find_element(By.XPATH, "/html/body[@id='mymain']/form[@id='form_rcdl']/div[@class='ui-grid ui-grid-responsive']/div[@class='container']/div[@class='top-space bottom-space']/div[@id='form_rcdl:rcdl_pnl']/div[@id='form_rcdl:rcdl_pnl_content']/div[@class='ui-grid-row bottom-space center-position']/div[@class='ui-grid-col-12']/button[@id='form_rcdl:j_idt50']/span[@class='ui-button-text ui-c']")
            check_status_button.click()

            time.sleep(3)
        except Exception as e:
            print(f"\nError in enter_details: \n{e}")

    def extract_data(self):
        try:
            page_table = self.driver.find_element(By.ID, 'form_rcdl:j_idt73')
            htmldata = self.driver.execute_script("return arguments[0].innerHTML;", page_table)

            soup = BeautifulSoup(htmldata, 'html.parser') 
            data = soup.find_all('td')
            data_dict = {
                "current_status":data[1].get_text(),
                "holder_name": data[3].get_text(),
                "old_new_dl_no": data[5].get_text(),
                "source_of_data": data[7].get_text(),
                "initial_issue_date": data[9].get_text(),
                "initial_issuing_office": data[11].get_text(),
                "last_endorsed_date": data[13].get_text(),
                "last_endorsed_office": data[15].get_text(),
                "last_completed_transaction": data[17].get_text(),

                "driving_license_validity_details":{
                    "non_transport":{
                        "valid_from": data[19].get_text()[6:],
                        "valid_upto": data[20].get_text()[4:],
                    },
                    "transport":{
                        "valid_from": data[22].get_text()[6:],
                        "valid_upto": data[23].get_text()[4:],
                    }
                },

                "hazardous_valid_till": data[25].get_text(),
                "hill_valid_till": data[27].get_text(),

                "class_of_vehicle_details":[
                {
                    "cov_category": data[28].get_text(),
                    "class_of_vehicle": data[29].get_text(),
                    "cov_issue_date": data[30].get_text(),
                },
                {
                    "cov_category": data[31].get_text(),
                    "class_of_vehicle": data[32].get_text(),
                    "cov_issue_date": data[33].get_text(),
                },
                {
                    "cov_category": data[34].get_text(),
                    "class_of_vehicle": data[35].get_text(),
                    "cov_issue_date": data[36].get_text(),
                },

                ]
            }

            data_json = json.dumps(data_dict)
            print("\n")
            print(data_json)
        except Exception as e:
            print(f"\nError in extract_data: \n{e}")

if __name__ == "__main__":
    dl_checker = DLStatusChecker()
    
    try:
        DL_num = input('Enter your DL Number: ')
        DL_dob = input('Enter your DOB (in DD-MM-YYYY format): ')
        print("Enter the CAPTCHA: ", end="")
        dl_checker.get_captcha()
        captcha = input()
        dl_checker.enter_details(DL_num, DL_dob, captcha)
        dl_checker.extract_data()
    except Exception as e:
        print(f"An error occurred: {e}")
