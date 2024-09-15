import pytest
import allure
import random
from selenium import webdriver
from selenium.webdriver import Chrome
import time
import sqlalchemy as db
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime,timedelta
import json
import logging

import names
from webdriver_manager.chrome import ChromeDriverManager
from faker import Faker

fake = Faker()

@pytest.fixture(scope="module")
def browser():
    """instance browser."""

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)
    browser.maximize_window()
    yield browser
    browser.quit()

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown(browser):
    """Setup dan teardown untuk suite tes."""
    login_partner(browser) 
    yield

def login_partner(browser):
    """Login sebagai partner."""
    browser.get("https://mekar-test.xyz/pendanaan-koperasi-dashboard")
    email_field = browser.find_element(By.XPATH, '//*[@id="username"]')
    inputemail = "agil.luthfi+cekbug01@mekar.id"
    slow_typing(email_field, inputemail)

    password_field = browser.find_element(By.XPATH, '//*[@id="password"]')
    input_password = "P@ssw0rd"
    slow_typing(password_field, input_password)

    login_button = browser.find_element(By.XPATH, '//*[@id="login"]')
    login_button.click()
    time.sleep(1)
    pass

def switch_to_modal_frame(browser):
    """Navigasi dan beralih ke iframe di dalamnya."""
    with allure.step("Klik tombol Upload Pinjaman"):
        btn_uploadpinjaman = browser.find_element(By.XPATH, '//header/div[1]/ul[1]/li[2]/a[1]')
        btn_uploadpinjaman.click()
        time.sleep(1)
        allure.attach(browser.get_screenshot_as_png(), name="Tampilan dropdown Upload Pinjaman")
    
    with allure.step("Klik tombol Financing"):
        btn_financing = browser.find_element(By.XPATH, "//header/div[1]/ul[1]/li[2]/div[1]/a[2]")
        btn_financing.click()
        time.sleep(1)
        allure.attach(browser.get_screenshot_as_png(), name="Upload Pinjaman Financing")

    with allure.step("Klik tombol Ajukan Pinjaman"):
        btn_ajukanpinjaman = browser.find_element(By.XPATH, "//button[contains(text(),'Ajukan Pinjaman')]")
        btn_ajukanpinjaman.click()
        time.sleep(3)
        allure.attach(browser.get_screenshot_as_png(), name="Form pinjaman Financing")

    with allure.step("switch iframe dalam modal"):
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'modal-form')))
        browser.switch_to.frame('modal-form-frame')
        time.sleep(1)

def slow_typing(element, text):
    """Fungsi mengetik di elemen input."""
    for character in text:
        element.send_keys(character)
        time.sleep(0.01)

def clear_and_input(element, text):
    """Hapus nilai input dan masukkan teks baru."""
    element.clear()  # Hapus nilai yang ada
    element.send_keys(text)

def capture_screenshot(browser, step_name):
    """Mengambil screenshot dari browser dan menempelkan nama langkah dari Allure."""
    allure.attach(browser.get_screenshot_as_png(), name=f"Screenshot {step_name}", attachment_type=allure.attachment_type.PNG)

def scroll_to_element(browser, element):
    """Scroll ke elemen tertentu untuk memastikan elemen tersebut terlihat saat mengambil screenshot."""
    browser.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(2)  # Tunggu agar scroll selesai dan elemen terlihat

@allure.feature('Upload Loan Financing')
@allure.story('Input "Tanggal Batch" Positif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_001(browser):
    switch_to_modal_frame(browser)

    with allure.step("Input Tanggal Batch dengan Format yang Valid"):
        tanggal_batch = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='batch-date']")))
        
        valid_date_format_1 = "2024/09/06"  # Format YYYY/MM/DD
        clear_and_input(tanggal_batch, valid_date_format_1)
        actual_value = tanggal_batch.get_attribute('value')
        allure.attach(actual_value, name="Actual Input Tanggal Batch", attachment_type=allure.attachment_type.TEXT)
        allure.attach(valid_date_format_1, name="Expected Tanggal Batch Format 1", attachment_type=allure.attachment_type.TEXT)

        klik_main = browser.find_element(By.XPATH, '//body/div[1]/main[1]')
        klik_main.click()
        time.sleep(1)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(valid_date_format_1, name="Input Tanggal Batch", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Batch Format Positif")
        assert actual_value == valid_date_format_1

        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan 2 diisi otomatis dengan 0 jika Jenis Jaminan 2 diisi None')
@allure.severity(allure.severity_level.NORMAL)
def testcase_069(browser):
    """Testcase *Negatif*: Nilai Jaminan 2 diisi otomatis dengan 0 jika Jenis Jaminan 2 diisi None"""
    try:
        with allure.step("Pilih None untuk Jenis Jaminan 2"):
            click_Jenis_Jaminan_2 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='collateral-2']")))
            browser.execute_script("arguments[0].scrollIntoView(true);", click_Jenis_Jaminan_2)
            time.sleep(1)
            click_Jenis_Jaminan_2.click()

            option_xpath_none = '//button[contains(text(),"None")]'
            option_none = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath_none)))
            option_none.click()
            time.sleep(1)

            selected_value_2 = click_Jenis_Jaminan_2.get_attribute('value')
            assert selected_value_2 == "None", (
                f"Jenis Jaminan yang dipilih seharusnya 'None', tetapi ditemukan '{selected_value_2}'."
            )

        with allure.step("Verifikasi Nilai Jaminan 2 diisi otomatis dengan 0 dan tidak bisa di edit"):
            nilai_jaminan_2 = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value-2']")))
            expected_value = "0"
            actual_value = nilai_jaminan_2.get_attribute('value')
            assert actual_value == expected_value, (
                f"Nilai jaminan seharusnya otomatis diisi dengan '{expected_value}', tetapi ditemukan '{actual_value}'."
            )

            nilai_jaminan_2.send_keys("123456")
            actual_value_after_edit = nilai_jaminan_2.get_attribute('value')
            assert actual_value_after_edit == expected_value, (
                "Nilai jaminan seharusnya tidak bisa diubah setelah diatur ke 0."
            )

            browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan_2)
            time.sleep(1)

            allure.attach(nilai_jaminan_2.get_attribute('value'), name="Nilai Jaminan 2", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Verifikasi Nilai Jaminan 2 Otomatis")
        
        click_Jenis_Jaminan_2.clear()
        nilai_jaminan_2.clear()
        time.sleep(1)

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan 2 di isi Nol Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_070(browser):
    """Testcase Negatif: mencoba Input Nilai Jaminan 2 dengan "0"
    
    kena validasi : "Harap isi Nilai Jaminan 2!"
    """
    try:
        with allure.step("Input Nilai Jaminan 2 dengan nilai Nol"):
#reset dl nilai jaminan 2
            click_Jenis_Jaminan_2 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='collateral-2']")))
            click_Jenis_Jaminan_2.click()  
            time.sleep(0.5)
            reset_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="collateral-2-dropdown"]/div[1]/button')))
            reset_button.click()
            time.sleep(1)


            nilai_jaminan2 = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value-2']")))

            input_nol = "0"
            nilai_jaminan2.clear()  
            nilai_jaminan2.send_keys(input_nol)
            time.sleep(0.5)  
            
            WebDriverWait(browser, 10).until(lambda driver: driver.find_element(By.XPATH, "//input[@id='collateral-value-2']").get_attribute('value') == input_nol)

            nilai_jaminan2.send_keys(Keys.RETURN)
            time.sleep(1)

            browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan2)
            time.sleep(1)

            allure.attach(input_nol, name="Input Nilai Jaminan 2 Nol", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan 2 Nol")

            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan 2!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nilai jaminan 2!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)

    except Exception as e:
        logging.error(f"Error : {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise
