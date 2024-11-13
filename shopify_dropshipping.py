#!/usr/bin/python3
from selenium.webdriver.common.keys import Keys
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from query_llm import QueryOpenAI
from product_url_list_formatted import product_url_list

class DSersAndShopify():

    def __init__(self, product_url_list: list = [], product_list_no_input_file: str = '/Users/stephen/socials/product_list_no_edit.txt', input_file: str = '/Users/stephen/socials/product_url_list_raw', output_file: str = '/Users/stephen/socials/product_url_list_formatted.py'):
        self.input_value = input('1: DSers: Import aliexpress\n2: DSers: Upload to shop\n3: Shopify\n4: Extract product_url_list\nEnter the input value: ')
        self.input_file = input_file
        self.product_list_no_input_file = product_list_no_input_file
        self.output_file = output_file
        self.product_url_list = product_url_list

        if self.input_value == '4':
            self.extract_links()
        else:
            self.create_driver()
            self.wait = WebDriverWait(self.driver, 10)

            if self.input_value in ['1', '2']:
                self.initiate_dsers()
            elif self.input_value == '3':
                self.initiate_shopify()

            time.sleep(36000)

    def create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('--remote-debugging-pipe')
        options.add_argument("user-data-dir=/Users/stephen/Library/Application Support/Google/Chrome")
        options.add_argument("profile-directory=Stephen")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)

    def initiate_dsers(self):
        self.driver.get("https://www.dsers.com/application/import_list")

        self.driver.maximize_window()

        login_required = input('Login required? [y/n]:\n')
        if login_required == 'y':
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "login_email")))
            email_field.send_keys("")

            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "login_password")))
            password_field.send_keys("")

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Login_button__Hpdt-')]//span[text()='LOG IN']")))
            login_button.click()

        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print('initial pause')
        time.sleep(13)
        self.close_dsers_popups()

        self.product_link_field = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Please enter the product link here to easily import the product into your DSers account.']")))

        if self.input_value == '1':
            self.import_to_dsers()

        elif self.input_value == '2':
            self.push_to_shopify()

    def import_to_dsers(self):
        product_url_list_len = len(self.product_url_list)
        for entry_iter, entry in enumerate(self.product_url_list):
            print(f'entry {entry_iter} of {product_url_list_len}')
            print('clear')
            self.driver.execute_script("arguments[0].value = '';", self.product_link_field)
            print('populate field')
            self.product_link_field.send_keys(f"{entry}")
            ok_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(@class, 'ant-btn ant-btn-default')]//span[text()='OK']")))
            print('click')
            ok_button.click()
            print('pause entry')
            time.sleep(8)

    def push_to_shopify(self):
        go_to_next = 'y'
        first_run = True
        while go_to_next == 'y':
            if not first_run:
                self.click_pre_iteration_button()
                self.driver.quit()

            return_value = self.push_to_store()
            first_run = False

            if return_value:
                go_to_next = input("Go to next page (y/n)? ").lower()
            else:
                print("No more pages to process.")
                break

    def push_to_store(self, page_limit: int = 20):
        self.run_text_click(text='Filter')

        self.run_text_click(text='No pushed to Stor')

        self.run_text_click(text='onfirm')

        list_items = self.driver.find_elements(By.XPATH, "//div[@class='ant-row']//div[@class='ant-list-item']")

        for item_iter, item in enumerate(list_items):
            if item_iter == page_limit - 1:
                return True
            try:
                #---------------------------------------------------------------------------
                span_element = item.find_element(By.CLASS_NAME, "sc_below_toolbarItem")
                span_element.click()
                print("Clicked on span element")
                time.sleep(4)
                #---------------------------------------------------------------------------

                self.run_text_click(text='Images', time_to_sleep=2)

                self.run_text_click(text='Select Image', time_to_sleep=2)


                all_option = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ant-dropdown-menu-title-content')]//span[text()='All']"))
                )
                all_option.click()
                print("Clicked on All option")
                time.sleep(2)
                #---------------------------------------------------------------------------

                self.run_text_click(text='PUSH TO STORE', time_to_sleep=2)

                save_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='ant-btn ant-btn-default' and @style='text-transform: uppercase;']//span[text()='save']"))
                )
                save_button.click()
                print("Clicked on Save button")

                self.run_text_click(text='ou have manually edited the product price on D', time_to_sleep=2, checkbox=True)

                self.run_text_click(text='Continue selling when out of stock', time_to_sleep=2, checkbox=True)

                self.run_text_click(text='utomatic Price Upda', time_to_sleep=2, checkbox=True)

                self.run_text_click(text='anual Price Upd', time_to_sleep=2, checkbox=True)

                #---------------------------------------------------------------------------
                push_to_stores_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='ant-btn ant-btn-default']//span[text()='PUSH TO STORES']"))
                )
                push_to_stores_button.click()
                print("Clicked on PUSH TO STORES button")
                time.sleep(2)
                #---------------------------------------------------------------------------


                #---------------------------------------------------------------------------
                close_icon = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@class='ant-modal-close-x']"))
                )
                close_icon.click()
                print("Clicked on modal close icon")
                time.sleep(2)
                #---------------------------------------------------------------------------

                close_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ant-modal-close-x"))
                )

                self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                time.sleep(1)

                close_button.click()
                time.sleep(3)
                print("CLICKED on the close button")
            except Exception as e:
                print(f"Could not click the span element in this item: {e}")

    def initiate_shopify(self):
        self.driver.get("https://www.shopify.com")
        self.open_ai = QueryOpenAI()

        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception:
            pass

        self.driver.refresh()

        self.driver.maximize_window()
        self.run_text_click(text='Log in', time_to_sleep=2)

        login_required = input('Login required? [y/n]:\n')
        self.shopify_user_input = input('User input? [y/n]: \n')
        if login_required == 'y':
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "account_email")))
            email_field.send_keys("")

            self.run_text_click(text='Continue with email', time_to_sleep=4)
            continue_input = input('Enter key to coninue:\n')
            if continue_input:
                password_field = self.wait.until(EC.presence_of_element_located((By.ID, "account_password")))
                password_field.send_keys("")

                self.run_text_click(text=' Log in', time_to_sleep=2)
                pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
                continue_input = input('Enter key to coninue:\n')

                if continue_input:
                    self.run_shopify()
        else:
            self.run_shopify()

    def run_shopify(self):
        self.run_text_click(text='Products', time_to_sleep=2)
        self.iterate_shopify_products()

    def iterate_shopify_products(self):
        while True:
            self.td_elements = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._TitleWrapper_110mh_16 span.Polaris-Text--root.Polaris-Text--bodyMd"))
            )

            for td_element_iter, td_element in enumerate(self.td_elements):
                self.td_elements = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._TitleWrapper_110mh_16 span.Polaris-Text--root.Polaris-Text--bodyMd"))
                )

                with open(self.product_list_no_input_file, 'r') as file:
                    self.content = file.read()

                text = self.td_elements[td_element_iter].text
                print('title', text)
                self.td = self.td_elements[td_element_iter]

                if text.replace("'", '').lower() not in self.content:
                    print('in')
                    self.set_shopify_product_values()
                else:
                    print('out')

                if td_element_iter + 1 == len(self.td_elements):
                    button = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "nextURL"))
                    )
                    button.click()
                    time.sleep(3)
                    self.iterate_shopify_products()

    def toggle_sales_channels(self):
        button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Manage']"))
        )
        print('Click ellipsis')
        button.click()

        self.run_text_click(text='Manage sales channels')

        popup = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'Polaris-Modal__Body')]"))
        )

        checkbox_labels = [
            "Online Store",
            "Point of Sale",
            "Shop",
            "Google & YouTube",
            "Facebook & Instagram"
        ]

        is_clicked = False

        for label in checkbox_labels:
            checkbox_xpath = f"//span[contains(@class, 'Polaris-Text--bodyMd') and contains(text(), '{label}')]//ancestor::label//input"
            checkbox = popup.find_element(By.XPATH, checkbox_xpath)

            if not checkbox.is_selected():
                if label != "Point of Sale":
                    checkbox.click()
                    is_clicked = True
            else:
                if label == "Point of Sale":
                    checkbox.click()
                    is_clicked = True
                print(f"Checkbox '{label}' is already checked.")
            time.sleep(0.1)

        footer_element = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'Polaris-Modal-Footer'))
        )

        print('is_clicked', is_clicked)

        if is_clicked:
            done_button = footer_element.find_element(By.XPATH, ".//button[contains(@class, 'Polaris-Button--variantPrimary')]//span[contains(@class, 'Polaris-Text--medium') and contains(text(), 'Done')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", done_button)
            done_button.click()
        else:
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Polaris-Button--variantTertiary') and contains(@aria-label, 'Close')]"))
            )

            close_button.click()

        time.sleep(0.5)

    def shopify_user_click(self):
        self.driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", self.td)

        if self.shopify_user_input == 'y':
            user_click = input('Click? [y/n]:\n')
            return user_click
        else:
            return 'y'

    def show_html(self):
        element = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Show HTML']"))
        )
        element.click()

    def specify_product_category(self):
        input_field = self.wait.until(EC.element_to_be_clickable((By.ID, "ProductCategoryPickerId")))
        input_field.click()

        while input_field.get_attribute("value"):
            input_field.send_keys(Keys.BACK_SPACE)
            time.sleep(0.1)

        input_field.send_keys("Decor")
        time.sleep(1.5)
        input_field.send_keys(Keys.RETURN)

    def choose_iframe(self):
        self.iframe = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
        )

    def switch_to_iframe(self):
        self.driver.switch_to.frame(self.iframe)

    def switch_to_default_context(self):
        self.driver.switch_to.default_content()

    def get_title_text(self):
        self.input_field = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='title']"))
        )

        self.input_text = self.input_field.get_attribute('value')
        print(self.input_text)

    def get_body_text(self):
        self.body_element = self.wait.until(
            EC.presence_of_element_located((By.ID, 'tinymce'))
        )

        self.body_text = self.body_element.get_attribute('innerHTML')

        print(self.body_text)

    def ai_generate_title_and_body(self):
        product_text = 'product name: ' + self.input_text + '\n' + self.body_text

        self.product_title = self.open_ai.run_query(prompt_type_input=1, user_input=product_text)
        self.product_body = self.open_ai.run_query(prompt_type_input=2, user_input=product_text)
        self.product_bullets = self.open_ai.run_query(prompt_type_input=3, user_input=product_text)

        self.body_and_bullets = self.product_body + '\n' + self.product_bullets

    def replace_title_text(self):
        self.input_field.send_keys(Keys.COMMAND + 'a')
        self.input_field.send_keys(Keys.BACKSPACE)
        self.input_field.send_keys(self.product_title.replace('"', '').replace("'", ''))

    def replace_body_text(self):
        self.body_element.send_keys(Keys.COMMAND + 'a')
        self.body_element.send_keys(Keys.BACKSPACE)
        time.sleep(1)
        self.body_element.send_keys(self.body_and_bullets)

    def replace_body_html_text(self):
        self.body_element.send_keys(Keys.COMMAND + 'a')
        self.body_element.send_keys(Keys.BACKSPACE)
        time.sleep(1)

        revised_body_text = self.body_text.replace('<li>- ', '<li>')
        self.body_element.send_keys(revised_body_text)

    def ai_title_and_body(self):
        self.get_title_text()
        time.sleep(0.5)
        self.choose_iframe()
        time.sleep(0.5)
        self.show_html()
        time.sleep(0.5)
        self.switch_to_iframe()
        time.sleep(0.5)
        self.get_body_text()
        time.sleep(0.5)
        self.replace_body_html_text()
        time.sleep(0.5)
        self.switch_to_default_context()
        time.sleep(0.5)

    def update_product_list_no_input_file(self):
        with open(self.product_list_no_input_file, 'a') as file:
            file.write(f"\n{self.input_text.lower()}\n")

        print(f"Updated product_list_no_edit.")

    def save_shopify(self):
        self.run_text_click(text='Save', time_to_sleep=2)

    def shopify_go_back(self):
        a_element = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'Polaris-Box--printHidden')]//a[@aria-label='Products']"))
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", a_element)

        a_element.click()

    def set_shopify_product_values(self):
        try:
            user_click = self.shopify_user_click()

            if user_click.lower() == 'y':
                self.td.click()

                self.toggle_sales_channels()
                self.specify_product_category()
                self.ai_title_and_body()
                self.save_shopify()
                self.update_product_list_no_input_file()

                if self.shopify_user_input == 'y':
                    go_back = input('Go back? [y/n]:\n')
                else:
                    go_back = 'y'

                if go_back.lower() == 'y':
                    self.shopify_go_back()
            else:
                self.driver.execute_script("arguments[0].style.border='2px solid red'", self.td)
            time.sleep(1)

        except Exception as e:
            print(f"Error: Could not click on the td element: {e}")

    def run_text_click(self, text: str, time_to_sleep: int = 1, checkbox: bool = False):
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)

            if checkbox:
                containing_label = element.find_element(By.XPATH, "./ancestor::label[contains(@class, 'ant-checkbox-wrapper')]")
                if 'ant-checkbox-wrapper-checked' in containing_label.get_attribute('class'):
                    containing_label.click()
                    time.sleep(time_to_sleep)
                    print(f"CLICKED on the checkbox containing '{text}'")
                else:
                    print(f"NOT CLICKED on the checkbox containing '{text}'")
            else:
                element.click()
                time.sleep(time_to_sleep)
                print(f"CLICKED on the element containing '{text}'")

        except Exception as e:
            print(f"Error: Could not click the element containing '{text}': {e}")

    def click_pre_iteration_button(self):
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="scrollContainer"]/div/div/div/div/div[9]/div/div/div/div[1]/button[2]')))
            button.click()
            print("Clicked pre-iteration button")
        except Exception as e:
            print(f"Could not click the pre-iteration button: {e}")

    def close_dsers_popups(self):
        try:
            close_button = self.driver.find_element(By.XPATH, "//img[@src='https://img.dsers.com/shopify/order/close.png']")
            if close_button:
                close_button.click()
                time.sleep(1)
        except Exception as e:
            print(f"No popups to close or unable to close popup: {e}")

    @staticmethod
    def run_cmd_within_script():
        while True:
            command = input("Enter a Selenium command (or 'exit' to quit): ").strip()
            if command.lower() == 'exit':
                break
            try:
                eval(command)
            except Exception as e:
                print(f"Error executing command: {e}")

    def extract_links(self):
        try:
            with open(self.input_file, 'r') as file:
                links = file.readlines()

            open(self.output_file, 'w').close()

            with open(self.output_file, 'w') as file:
                for link_iter, link in enumerate(links):
                    if link_iter == 0:
                        file.write('product_url_list = [' + "'" + link.strip() + "'" + ',' + '\n')
                    elif link_iter + 1 == len(links):
                        file.write("'" + link.strip() + "'" + ']')
                    else:
                        file.write("'" + link.strip() + "'" + ',' + '\n')
            print(f"Links have been successfully written to {self.output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    dsers = DSersAndShopify(product_url_list=product_url_list)
