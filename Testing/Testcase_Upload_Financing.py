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
from datetime import datetime
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

@allure.feature('Upload Loan Financing')
@allure.story('Input "Tanggal Batch" *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_001(browser):
    switch_to_modal_frame(browser)

    with allure.step("Input Tanggal Batch dengan Format yang Valid"):
        tanggal_batch = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@id='batch-date']")))
        
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
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Batch Format *Positif*")
        assert actual_value == valid_date_format_1
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Batch Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_002(browser):
    """Testcase *Negatif* : input tanggal batch dengan tanggal yang tidak ada.

    Catatan: Validasi untuk tanggal yang tidak ada telah ditambahkan ke sistem.
    contoh input 32 sistem akan otomatis menjadi "2024-10-02"
    """

    with allure.step("Input Tanggal Batch dengan Tanggal Tidak Ada"):
        tanggal_batch = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='batch-date']")))
        
        invalid_date_1 = "2024-09-32"  
        clear_and_input(tanggal_batch, invalid_date_1)
        time.sleep(1)  

        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)  

        actual_value = tanggal_batch.get_attribute('value')
        actual_value = actual_value.replace('/', '-')  

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(invalid_date_1, name="Input Tanggal Batch", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Batch Tanggal Tidak Ada")

        expected_date = "2024-10-02"  
        assert actual_value == expected_date, f"Tanggal yang tidak ada seharusnya dikoreksi menjadi {expected_date}."

        clear_and_input(tanggal_batch, "")

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Batch Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_003(browser):
    """Testcase *Negatif* : input tanggal batch dengan bulan yang tidak ada.

    Catatan: Validasi untuk bulan yang tidak ada telah ditambahkan ke sistem.
    contoh input bulan 13 sistem akan otomatis menjadi "bulan : 01"
    """
    with allure.step("Input Tanggal Batch dengan Bulan Tidak Ada"):
        tanggal_batch = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='batch-date']")))
        
        invalid_date_2 = "2024-13-01"  # Bulan ke-13 tidak valid
        clear_and_input(tanggal_batch, invalid_date_2)
        time.sleep(1)
        
        actual_value = tanggal_batch.get_attribute('value')

        # Klik elemen lain untuk memicu validasi
        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(invalid_date_2, name="Input Tanggal Batch", attachment_type=allure.attachment_type.TEXT)

        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Batch Bulan Tidak Ada")

#convert
        actual_value = tanggal_batch.get_attribute('value')
        actual_value = actual_value.replace('/', '-')  

        expected_date = "2024-01-01"  
        assert actual_value == expected_date, f"Bulan yang tidak ada seharusnya dikoreksi menjadi {expected_date}."

        # Clear input setelah verifikasi
        clear_and_input(tanggal_batch, "")
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Batch Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_004(browser):
    """Testcase *Negatif* : input tanggal batch dengan format yang salah.

    catatan : case minor """

    with allure.step("Input Tanggal Batch dengan Format yang Salah"):
        tanggal_batch = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='batch-date']")))
        
        invalid_date_3 = "01/09/2024"  
        clear_and_input(tanggal_batch, invalid_date_3)
        time.sleep(1)

        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(invalid_date_3, name="Input Tanggal Batch", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Batch Format Salah")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih tanggal batch!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap pilih tanggal batch!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")
        

        except Exception as e:
            logging.error(f"Error dalam testcase_015: {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        time.sleep(1)
        
        clear_and_input(tanggal_batch, "")

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Batch Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_005(browser):
    """Testcase *Negatif* : input tanggal batch yang kosong. 
     
    *pesan error : Harap isi nama batch!
       """

    with allure.step("Input Tanggal Batch Kosong"):
        tanggal_batch = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='batch-date']")))
        
        clear_and_input(tanggal_batch, "")
        time.sleep(1)
        
        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = tanggal_batch.get_attribute('value')
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Batch Kosong")

        assert actual_value == "", "Tanggal batch yang kosong seharusnya tetap kosong."
        
        clear_and_input(tanggal_batch, "")

        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nama Batch Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_006(browser):
    """Testcase *Positif* : input Name batch valid"""
    # switch_to_modal_frame(browser)
    
    with allure.step("Input Nama Batch"):
        nama_batch = browser.find_element(By.XPATH, "//input[@id='batch-name']")
        input_nama_batch = fake.numerify('QATEST-1######')
        slow_typing(nama_batch, input_nama_batch)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(input_nama_batch, name="Input Nama Batch", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nama Batch")
        nama_batch.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nama Batch Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_007(browser):
    """Testcase *Negatif* : input Nama Batch kosong
    
    *pesan error : Harap isi nama batch!
    """
    
    with allure.step("Input Nama Batch"):
        nama_batch = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='batch-name']")))
        nama_batch.clear()  # Pastikan inputan sudah bersih
        nama_batch.send_keys("")  # Input kosong

        btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
        btn_validasi.click()
        time.sleep(1)

        error_message_element = WebDriverWait(browser, 10).until( EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nama batch!')]")))
        error_message_text = error_message_element.text
        
        expected_error_message = "Harap isi nama batch!"  
        assert expected_error_message in error_message_text, (
            f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
            f"Pesan kesalahan yang ditemukan '{error_message_text}'."
        )
        
        allure.attach("", name="Input Nama Batch Kosong", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nama Batch Kosong")

@allure.feature('Upload Loan Financing')
@allure.story('Nomor Pinjaman valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_008(browser):
    """Testcase *Positif* : input Nomor Pinjaman valid"""
    # switch_to_modal_frame(browser)
    
    with allure.step("Input Nomor Pinjaman"):
        nomor_pinjaman = browser.find_element(By.XPATH, "//input[@id='loan-number']")
        input_nomorpinjaman = fake.numerify('PinjamNo-1######')
        slow_typing(nomor_pinjaman, input_nomorpinjaman)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(input_nomorpinjaman, name="Input Nomor Pinjaman", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nomor Pinjaman")
        nomor_pinjaman.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nomor Pinjaman Kosong')
@allure.severity(allure.severity_level.NORMAL)
def testcase_009(browser):
    """Testcase *Negatif* : input Nomor Pinjaman kosong
    
    *pesan error : Harap isi nama batch!
    """
    
    

    with allure.step("Input Nomor Pinjaman Kosong"):
        nomor_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-number']")))
        nomor_pinjaman.clear()
        
        btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
        btn_validasi.click()
        
        time.sleep(1)

        error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nomor pinjaman!')]")))
        error_message_text = error_message_element.text
        
        expected_error_message = "Harap isi nomor pinjaman!"  
        assert expected_error_message in error_message_text, (
            f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
            f"Pesan kesalahan yang ditemukan '{error_message_text}'."
        )
        
        allure.attach("", name="Input Nomor Pinjaman Kosong", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nomor Pinjaman Kosong")
        
@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_010(browser):
    """Testcase *Positif* :  input Nominal Pinjaman dengan data valid *Only Number"""
    # switch_to_modal_frame(browser)
    
    with allure.step("Input Nominal Pinjaman"):
        nominal_pinjaman = browser.find_element(By.XPATH, "//input[@id='loan-nominal']")
        nominal_pinjaman.clear()
        input_nominal_pinjaman = random.choice(["100000", "250000", "300000"])
        slow_typing(nominal_pinjaman, input_nominal_pinjaman)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)
        
        allure.attach(input_nominal_pinjaman, name="Input Nominal Pinjaman", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman")
        nominal_pinjaman.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_011(browser):
    """Testcase *Negatif* : input nominal pinjaman dengan input yang tidak valid."""

    with allure.step("Input Nominal Pinjaman Kosong"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']")))
        clear_and_input(nominal_pinjaman, "")
        time.sleep(1)  

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = nominal_pinjaman.get_attribute('value')
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman Kosong")
        
        assert actual_value == "", "Nominal pinjaman tidak boleh kosong."

@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_012(browser):
    """Testcase *Negatif* : input nominal pinjaman dengan karakter non-numerik.
    
    Catatan: Sistem telah update untuk menolak karakter non-numerik dan input harus kosong.
    """
    
    with allure.step("Input Nominal Pinjaman dengan Karakter Non-Numerik"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']")))
        invalid_value = "abc!@#"
        clear_and_input(nominal_pinjaman, invalid_value)
        time.sleep(1)  

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = nominal_pinjaman.get_attribute('value')
        allure.attach(invalid_value, name="input Nominal Pinjaman", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman Non-Numerik")

        assert actual_value == "", "Nominal pinjaman dengan karakter non-numerik seharusnya tidak diterima dan input harus kosong."
        nominal_pinjaman.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_013(browser):
    """Testcase *Negatif* input nominal pinjaman dengan angka *Negatif*.
    
    catatan : nilai *Negatif* (-) tidak di terima 
    sistem otomatis merubah (-) menjadi (+).
    """

    with allure.step("Input Nominal Pinjaman dengan Angka *Negatif*"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']")))
        invalid_value = "-100000"
        clear_and_input(nominal_pinjaman, invalid_value)
        time.sleep(1) 

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = nominal_pinjaman.get_attribute('value')
        allure.attach(invalid_value, name="input Nominal Pinjaman", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman *Negatif*")
        
        assert actual_value == "100.000", "Sistem menghilangkan (-) di depan angka"
        nominal_pinjaman.clear()
        time.sleep(1)
        print(f"Actual value: {actual_value}")

@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_014(browser):
    """Testcase *Negatif* input nominal pinjaman (MAX / MIN)
    
    Expect:
    minimal : 100.000
    maximal : 2.000.000.000 

    Test data:
    minimal : 99999
    maximal : 2.000.000.001
    """

    minimal_invalid_value = "99999"
    maximal_invalid_value = "2000000001"
    expected_error_message_minimal = "Minimal pinjaman adalah Rp. 100000!"
    expected_error_message_maximal = "Maksimal pinjaman adalah Rp. 2000000000!"

    with allure.step("Input Nominal Pinjaman di Bawah Batas Minimal"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']"))
        )
        nominal_pinjaman.clear()
        slow_typing(nominal_pinjaman, minimal_invalid_value)

        nominal_pinjaman.send_keys(Keys.TAB)
        time.sleep(1)

        actual_value = nominal_pinjaman.get_attribute('value')
        allure.attach(minimal_invalid_value, name="Input Nominal Pinjaman (Minimal Invalid)", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman Terlalu Kecil")

        try:
            error_message_element = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, f"//div[contains(text(),'{expected_error_message_minimal}')]"))
            )
            error_message_text = error_message_element.text

            assert expected_error_message_minimal in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message_minimal}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan Minimal Invalid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan Minimal Invalid")

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error Minimal Invalid", attachment_type=allure.attachment_type.PNG)
            raise

        nominal_pinjaman.clear()

    # Langkah 2: Input Nominal Pinjaman di Atas Batas Maksimal
    with allure.step("Input Nominal Pinjaman di Atas Batas Maksimal"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']"))
        )
        nominal_pinjaman.clear()
        slow_typing(nominal_pinjaman, maximal_invalid_value)

        nominal_pinjaman.send_keys(Keys.TAB)
        time.sleep(1)

        actual_value = nominal_pinjaman.get_attribute('value')
        allure.attach(maximal_invalid_value, name="Input Nominal Pinjaman (Maximal Invalid)", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman Terlalu Besar")

        try:
            error_message_element = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, f"//div[contains(text(),'{expected_error_message_maximal}')]"))
            )
            error_message_text = error_message_element.text

            assert expected_error_message_maximal in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message_maximal}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan Maximal Invalid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan Maximal Invalid")

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error Maximal Invalid", attachment_type=allure.attachment_type.PNG)
            raise

        nominal_pinjaman.clear()
        

@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman Non-Numerik *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_015(browser):
    """Testcase *Negatif*: mencoba Input Nominal Pinjaman dengan "KOMA" berulang dan verifikasi pesan kesalahan.
    
    Note: sistem otomatis menghapus value yang bukan numeric.
    """
    
    with allure.step("Input Nominal Pinjaman dengan Karakter Non-Numerik"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']")))

        input_non_numerik = "," * 20
        browser.execute_script("arguments[0].value = arguments[1];", nominal_pinjaman, input_non_numerik)
            
        browser.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", nominal_pinjaman)
        nominal_pinjaman.send_keys(Keys.TAB)

        nominal_pinjaman.send_keys(Keys.ENTER)
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nominal Pinjaman Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Format tidak valid!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Format tidak valid!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error : {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nominal_pinjaman.clear()
        time.sleep(1)
        

@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman di isi Nol *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_016(browser):
    """Testcase *Negatif*: mencoba Input Nominal Pinjaman dengan "0" 
    
    expect : muncul pesan error, "Harap isi nominal pinjaman!".
    """
    
    with allure.step("Input Nominal Pinjaman dengan nilai Nol"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']")))

        input_non_numerik = "0"
        nominal_pinjaman.clear()
        slow_typing(nominal_pinjaman, input_non_numerik)
        nominal_pinjaman.send_keys(Keys.RETURN)
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nominal Pinjaman Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nominal pinjaman!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nominal pinjaman!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error dalam testcase_016: {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nominal_pinjaman.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman di isi desimal Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_017(browser):
    """Testcase Negatif: mencoba Input Nominal Pinjaman 2 dengan angka desimal

    0,02
    
    kena validasi : "Harap isi nominal pinjaman!"
    """
    
    with allure.step("Input Nominal Pinjaman dengan nilai Desimal"):
        nilai_jaminan2 = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']")))

        input_non_numerik = "0,02"
        nilai_jaminan2.clear()
        slow_typing(nilai_jaminan2, input_non_numerik)

        nilai_jaminan2.send_keys(Keys.RETURN)
        time.sleep(1)

        btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
        btn_validasi.click()
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nilai Jaminan 2 Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan 2 Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nominal pinjaman!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nominal pinjaman!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nilai_jaminan2.clear()
        time.sleep(1)


@allure.feature('Upload Loan Financing')
@allure.story('Nominal Pinjaman Nol berulang Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_018(browser):
    """Testcase Negatif: mencoba Input Nominal Pinjaman dengan "Nol" berulang dan verifikasi pesan kesalahan.
    
    """
    
    with allure.step("Input Nominal Pinjaman dengan Karakter Non-Numerik"):
        nominal_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-nominal']")))

        input_non_numerik = "0" * 20
        nominal_pinjaman.clear()
        slow_typing(nominal_pinjaman, input_non_numerik)
        nominal_pinjaman.send_keys(Keys.RETURN)
        time.sleep(1)

        btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
        btn_validasi.click()
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nominal Pinjaman Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nominal Pinjaman Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nominal pinjaman!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nominal pinjaman!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error : {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nominal_pinjaman.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Tenor valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_019(browser):
    """Testcase *Positif* pilih Tenor dropdown valid.
    
    """
    
    with allure.step("Pilih Tenor"):

        click_tenor = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.XPATH, "//input[@id='tenor']")))
        click_tenor.clear()
        click_tenor.click()
        time.sleep(0.5)  
        
        tenor_options = ["1 Bulan", "2 Bulan", "3 Bulan"]
        selected_tenor = random.choice(tenor_options)
        option_xpath = f'//div[@id="tenor-dropdown"]//button[text()="{selected_tenor}"]'
        
        option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        option.click()
        time.sleep(1) 
        
        selected_value = click_tenor.get_attribute('value')
        assert selected_value == selected_tenor, f"Tenor yang dipilih seharusnya '{selected_tenor}', tetapi ditemukan '{selected_value}'."

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(selected_value, name="Input Tenor", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pilih Tenor")
        
        click_tenor.clear()

@allure.feature('Upload Loan Financing')
@allure.story('Tenor Kosong')
@allure.severity(allure.severity_level.NORMAL)
def testcase_020(browser):
    """Testcase *Negatif*: Tenor tidak boleh kosong
    
    expect : muncul pesan error 
    """
    
    with allure.step("Tenor Kosong dan Verifikasi Pesan Kesalahan"):
        tenor_input = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='tenor']")))
        tenor_input.click()
        time.sleep(0.5)
        reset_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' -- Reset --']")))
        reset_button.click()
        time.sleep(1)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot After Reset", attachment_type=allure.attachment_type.PNG)
        
        tenor_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tenor Kosong", attachment_type=allure.attachment_type.PNG)
        
        
        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih tenor!')]")))
            error_message_text = error_message_element.text
            expected_error_message = "Harap pilih tenor!"

            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

        except Exception as e:
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Tenor Kosong Error", attachment_type=allure.attachment_type.PNG)
            raise e

@allure.feature('Upload Loan Financing')
@allure.story('Dropdown Tenor dan Input Ulang')
@allure.severity(allure.severity_level.NORMAL)
def testcase_021(browser):
    """Testcase *Negatif*: Pilih dari dropdown dan kemudian input ulang menyebabkan pesan kesalahan
    
    test step : pilih dropdown sesuai value , lalu ketik ulang "cobatenor"

    expect : muncul pesan error
    """
    
    try:
        with allure.step("Pilih Tenor dari Dropdown dan ketik di textbox"):
            click_tenor = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='tenor']")))
            click_tenor.clear()
            click_tenor.click()
            time.sleep(1)  
            
            tenor_options = ["1 Bulan", "2 Bulan", "3 Bulan"]
            selected_tenor = random.choice(tenor_options)
            option_xpath = f'//div[@id="tenor-dropdown"]//button[text()="{selected_tenor}"]'
            
            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            
            # Simpan nilai tenor yang dipilih untuk digunakan dalam allure.attach
            input_tenor = selected_tenor

            allure.attach(f"Input Tenor: {input_tenor}", name="Input Tenor sesuai value dropdown", attachment_type=allure.attachment_type.TEXT)
            time.sleep(1)
            click_tenor.clear()

            input_tenor = "coba tenor"
            slow_typing(click_tenor, input_tenor) 
            click_tenor.send_keys(Keys.RETURN)
            time.sleep(1)

            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih tenor!')]")))
            error_message_text = error_message_element.text

            allure.attach(f"Input Tenor: {input_tenor}", name="Input Tenor tidak sesuai dropdown", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input tidak sesuai dropdown")
            
            expected_error_message = "Harap pilih tenor!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            click_tenor.clear()

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise
    

@allure.feature('Upload Loan Financing')
@allure.story('Jenis Pinjaman Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_022(browser):
    """Testcase *Positif* : pilih Jenis Pinjaman dropdown valid.
    
    """
    
    with allure.step("Pilih Jenis Pinjaman"):

        click_jenis_pinjaman = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.XPATH, "//input[@id='loan-type']")))
        click_jenis_pinjaman.click()
        time.sleep(0.5)  
        
        Jenis_Pinjaman_options = ["MULTIGUNA"]
        selected_Jenis_Pinjaman_options = random.choice(Jenis_Pinjaman_options)
        option_xpath = f'//div[@id="loan-type-dropdown"]//button[text()="{selected_Jenis_Pinjaman_options}"]'
        
        option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        option.click()
        time.sleep(1) 
        
        selected_value = click_jenis_pinjaman.get_attribute('value')
        assert selected_value == selected_Jenis_Pinjaman_options, f"Jenis Pinjaman yang dipilih seharusnya '{selected_Jenis_Pinjaman_options}', tetapi ditemukan '{selected_value}'."
        
        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)
        
        allure.attach(selected_value, name="Input Jenis Pinjaman", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pilih Jenis Pinjaman")

        click_jenis_pinjaman.clear()

@allure.feature('Upload Loan Financing')
@allure.story('Jenis Pinjaman Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_023(browser):
    """Testcase *Negatif*: Jenis Pinjaman tidak boleh kosong
    
    expect : muncul pesan error
    """
    
    try:
        with allure.step("Biarkan Jenis Pinjaman Kosong dan Verifikasi Pesan Kesalahan"):
            click_jenis_pinjaman = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='loan-type']")))
            click_jenis_pinjaman.click()  

            option_xpath = '//*[@id="loan-type-dropdown"]/div[1]/button'  
            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih jenis pinjaman!')]")))
            error_message_text = error_message_element.text
            
            expected_error_message = "Harap pilih jenis pinjaman!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach("", name="Input Jenis Pinjaman Kosong", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Jenis Pinjaman Kosong")

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Jenis Pinjaman Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_024(browser):
    """Testcase *Negatif*: Pilih Jenis Pinjaman dari Dropdown dan Input Ulang Memunculkan Pesan Kesalahan"""
    
    with allure.step("Pilih Jenis Pinjaman dari Dropdown dan Input Ulang"):
        try:

            click_jenis_pinjaman = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='loan-type']")))
            click_jenis_pinjaman.click()
            time.sleep(1)  

            Jenis_Pinjaman_options = ["MULTIGUNA"]
            selected_Jenis_Pinjaman = random.choice(Jenis_Pinjaman_options)
            option_xpath = f'//div[@id="loan-type-dropdown"]//button[text()="{selected_Jenis_Pinjaman}"]'
            
            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(1)  
            click_jenis_pinjaman.clear()

            click_jenis_pinjaman = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='loan-type']")))
            input_jenis_pinjaman = "coba jenis pinjaman"
            slow_typing (click_jenis_pinjaman,input_jenis_pinjaman)


            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih jenis pinjaman!')]")))
            error_message_text = error_message_element.text
            
            expected_error_message = "Harap pilih jenis pinjaman!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )


            allure.attach("Coba Jenis Pinjaman", name="Input Jenis Pinjaman Setelah Dropdown", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Jenis Pinjaman Setelah Dropdown")
            click_jenis_pinjaman.send_keys(Keys.RETURN)

        except Exception as e:
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

@allure.feature('Upload Loan Financing')
@allure.story('Tujuan Pinjaman Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_025(browser):
    """Testcase *Positif* : input Tujuan Pinjaman valid *Freetext*
    
    """
    
    with allure.step("Input Tujuan Pinjaman"):
        tujuan_pinjaman = browser.find_element(By.XPATH, "//input[@id='loan-destination']")
        input_tujuan_pinjaman = random.choice(["MODAL USAHA", "RENOVASI RUMAH", "BIAYA ANAK SEKOLAH"])
        slow_typing(tujuan_pinjaman, input_tujuan_pinjaman)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(input_tujuan_pinjaman, name="Input Nama Batch", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nama Batch")
        tujuan_pinjaman.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Tujuan Pinjaman Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_026(browser):
    """Testcase *Positif* : input tujuan pinjaman dengan teks yang mengandung Special Karakter."""

    with allure.step("Input Tujuan Pinjaman dengan Teks Mengandung Special Karakter"):
        tujuan_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-destination']")))
        
        special_text = "Pengembangan Infrastruktur @Pusat Pelatihan Karyawan #1"
        clear_and_input(tujuan_pinjaman, special_text)
        time.sleep(1)  

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = tujuan_pinjaman.get_attribute('value')
        allure.attach(special_text, name="Input Tujuan Pinjaman", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tujuan Pinjaman")
        
        assert actual_value == special_text, "Tujuan pinjaman dengan teks mengandung Special Karakter seharusnya diterima dan disimpan dengan benar."
        tujuan_pinjaman.clear()

@allure.feature('Upload Loan Financing')
@allure.story('Tujuan Pinjaman Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_027(browser):
    """Testcase *Positif* input tujuan pinjaman dengan teks panjang yang valid."""

    with allure.step("Input Tujuan Pinjaman dengan long_text"):
        tujuan_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-destination']")))
        
        long_text = "Pengembangan Infrastruktur Digital untuk Peningkatan Akses Internet di Daerah Terpencil"
        clear_and_input(tujuan_pinjaman, long_text)
        time.sleep(1)  

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = tujuan_pinjaman.get_attribute('value')
        allure.attach(long_text, name="Input Tujuan Pinjaman", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tujuan Pinjaman")
        
        assert actual_value == long_text, "Tujuan pinjaman dengan long_text yang valid seharusnya diterima dan disimpan dengan benar."
        tujuan_pinjaman.clear()

@allure.feature('Upload Loan Financing')
@allure.story('Tujuan Pinjaman Tidak Diisi')
@allure.severity(allure.severity_level.NORMAL)
def testcase_028(browser):
    """Testcase *Negatif*: Tujuan Pinjaman tidak boleh kosong"""

    with allure.step("Biarkan Tujuan Pinjaman Kosong dan Verifikasi Pesan Kesalahan"):
        tujuan_pinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-destination']")))
        tujuan_pinjaman.clear() 
        tujuan_pinjaman.send_keys(Keys.RETURN)

        time.sleep(1.5)

        error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi tujuan pinjaman!')]")))
        error_message_text = error_message_element.text
        
        expected_error_message = "Harap isi tujuan pinjaman!"
        assert expected_error_message in error_message_text, (
            f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
            f"Pesan kesalahan yang ditemukan '{error_message_text}'."
        )
        
        allure.attach("", name="Input Tujuan Pinjaman Kosong", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Tujuan Pinjaman Kosong")

        tujuan_pinjaman.clear()

@allure.feature('Upload Loan Financing')
@allure.story('Sektor Tujuan Pinjaman Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_029(browser):
    """Testcase *Positif*: Pilih Sektor Tujuan Pinjaman dari dropdown yang valid."""

    with allure.step("Pilih Sektor Tujuan Pinjaman"):

        try:
            click_sektor_tujuan_pinjaman = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='loan-destination-sector']")))
            click_sektor_tujuan_pinjaman.click()
            time.sleep(1) 

            # Pilih opsi dari dropdown
            sektor_tujuan_pinjaman_option = [
                "Konsumtif",
                "Administrasi Pemerintahan, Pertahanan, dan Jaminan Sosial Wajib"
            ]

            selected_Sektor_Tujuan_Pinjaman = random.choice(sektor_tujuan_pinjaman_option)
            option_xpath = f'//div[@id="loan-destination-sector-dropdown"]//button[text()="{selected_Sektor_Tujuan_Pinjaman}"]'

            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(1) 

            selected_value = click_sektor_tujuan_pinjaman.get_attribute('value')

            # Klik tombol validasi
            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            allure.attach(selected_value, name="Input Tujuan Pinjaman", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pilih Sektor Tujuan Pinjaman")
            click_sektor_tujuan_pinjaman.clear()


        except Exception as e:
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

@allure.feature('Upload Loan Financing')
@allure.story('Sektor Tujuan Pinjaman Tidak Diisi')
@allure.severity(allure.severity_level.NORMAL)
def testcase_030(browser):
    """Testcase *Negatif*: Sektor Tujuan Pinjaman tidak boleh kosong"""

    with allure.step("Biarkan Sektor Tujuan Pinjaman Kosong dan Verifikasi Pesan Kesalahan"):

        click_sektor_tujuan_pinjaman = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='loan-destination-sector']")))
        click_sektor_tujuan_pinjaman.clear()
        click_sektor_tujuan_pinjaman.click()
        click_sektor_tujuan_pinjaman.send_keys(Keys.RETURN)
        time.sleep(1)
        
        allure.attach(browser.get_screenshot_as_png(), name="screenshoot sektor pinjaman kosong", attachment_type=allure.attachment_type.PNG)
        
        try:
            error_message_element = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih sektor tujuan pinjaman!')]"))
            )
            error_message_text = error_message_element.text
            expected_error_message = "Harap pilih sektor tujuan pinjaman!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )
        except Exception as e:
            allure.attach(browser.get_screenshot_as_png(), name="Error Message Not Found", attachment_type=allure.attachment_type.PNG)
            raise e


@allure.feature('Upload Loan Financing')
@allure.story('Sektor Tujuan Pinjaman Valid dan Input Text Kosong')
@allure.severity(allure.severity_level.NORMAL)
def testcase_031(browser):
    """Testcase *Negatif*: Pilih sektor tujuan pinjaman dari dropdown dan ketik teks invalid"""

    with allure.step("Pilih sektor tujuan pinjaman dari dropdown dan ketik teks invalid"):
        try:
            click_sektor_tujuan_pinjaman = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='loan-destination-sector']")))
            click_sektor_tujuan_pinjaman.click()
            time.sleep(1) 

            sektor_tujuan_pinjaman_option = [
                "Konsumtif",
                "Administrasi Pemerintahan, Pertahanan, dan Jaminan Sosial Wajib"
            ]
            selected_Sektor_Tujuan_Pinjaman = random.choice(sektor_tujuan_pinjaman_option)
            option_xpath = f'//div[@id="loan-destination-sector-dropdown"]//button[text()="{selected_Sektor_Tujuan_Pinjaman}"]'

            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(1) 

            invalid_text = "Coba Sektor Tujuan Pinjaman"
            slow_typing(click_sektor_tujuan_pinjaman,invalid_text)

            click_sektor_tujuan_pinjaman.send_keys(Keys.RETURN)
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih sektor tujuan pinjaman!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap pilih sektor tujuan pinjaman!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )


            allure.attach(invalid_text, name="Input Sektor Tujuan Pinjaman", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Sektor Tujuan Pinjaman")

        except Exception as e:
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

#-------- belum di test--------#

@allure.feature('Upload Loan Financing')
@allure.story('Bunga Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_032(browser):
    """Testcase *Positif* : input bunga dengan nilai valid"""
    
    try:
        with allure.step("Input Bunga Valid dengan Dua Digit Setelah Desimal"):
            bunga = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='interest']")))
            
            valid_values = ["5,22", "3,10", "6,77"]
            input_bunga = random.choice(valid_values)
            clear_and_input(bunga, input_bunga)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            actual_value = bunga.get_attribute('value')
            assert actual_value == input_bunga, f"Bunga dengan nilai valid seharusnya '{input_bunga}', tetapi ditemukan '{actual_value}'."
            
            allure.attach(input_bunga, name="Input Bunga Valid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Bunga Valid")

#raise exception jika testcase gagal.            
    except Exception as e:
        logging.error(f"Error dalam bunga_*Positif*: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise  

@allure.feature('Upload Loan Financing')
@allure.story('Bunga Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_033(browser):
    """Testcase *Negatif* : input bunga dengan karakter non-numerik"""
    
    try:
        with allure.step("Input Bunga dengan Karakter Non-Numerik"):
            bunga = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='interest']")))
            
            invalid_value = "abc!@#"
            clear_and_input(bunga, invalid_value)
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            actual_value = bunga.get_attribute('value')
            assert actual_value == "", "Input dengan karakter non-numerik seharusnya tidak diterima dan input harus kosong."
            
            allure.attach(invalid_value, name="Input Bunga Invalid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Bunga Invalid")
            
    except Exception as e:
        logging.error(f"Error dalam bunga_*Negatif*_01: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Bunga Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_034(browser):
    """Testcase *Negatif* : input bunga dengan format tidak valid (lebih dari dua digit setelah desimal)
    
    sistem otomatis menghapus.
    """
    
    try:
        with allure.step("Input Bunga dengan Format Tidak Valid"):
            bunga = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='interest']")))
            
            invalid_value = "5,123"
            clear_and_input(bunga, invalid_value)
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            actual_value = bunga.get_attribute('value')
            assert actual_value == "5,12", "Input dengan format tidak valid seharusnya tidak diterima dan input harus kosong."
            
            allure.attach(invalid_value, name="Input Bunga Format Tidak Valid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Bunga Format Tidak Valid")
            
    except Exception as e:
        logging.error(f"Error dalam bunga_*Negatif*_02: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Bunga Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_035(browser):
    """Testcase *Negatif* : untuk input bunga dengan nilai *Negatif*, dengan harapan sistem mengubah nilai menjadi *Positif*"""
    
    try:
        with allure.step("Input Bunga dengan Nilai *Negatif*"):
            bunga = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='interest']")))
            
            invalid_value = "-5,22"
            clear_and_input(bunga, invalid_value)
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            actual_value = bunga.get_attribute('value')
            expected_value = "5,22"  

            assert actual_value == expected_value, f"Input dengan nilai *Negatif* '{invalid_value}' seharusnya diubah menjadi '{expected_value}', tetapi ditemukan '{actual_value}'."
            
            allure.attach(invalid_value, name="Input Bunga Nilai *Negatif*", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Bunga Nilai *Negatif*")
            
    except Exception as e:
        logging.error(f"Error dalam testcase_024: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Bunga Kosong *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_036(browser):
    """Testcase *Negatif*: Mengisi field bunga dengan nilai kosong, dengan harapan sistem menunjukkan pesan kesalahan."""
    
    try:
        with allure.step("Input Bunga dengan Nilai Kosong"):
            statuspinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-status']")))
            bunga = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='interest']")))
            clear_and_input(bunga, "")
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            browser.execute_script("arguments[0].scrollIntoView(true);", statuspinjaman)
            time.sleep(1)

            error_message = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi bunga!')]"))).text
            
            assert "Harap isi bunga!" in error_message, "Harus ada pesan kesalahan 'Harap isi bunga!' tetapi tidak ditemukan."
            
            allure.attach("", name="Input Bunga Kosong", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Bunga Kosong")
            
    except Exception as e:
        logging.error(f"Error dalam bunga_kosong_*Negatif*: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Bunga Invalid Format')
@allure.severity(allure.severity_level.NORMAL)
def testcase_037(browser):
    """Testcase *Negatif*: Input max bunga dengan format tidak valid

    expect : Range bunga adalah 0.01 - 99.99!
    result : 
    
    """

    try:
        with allure.step("Input Bunga dengan Format Tidak Valid"):
            statuspinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-status']")))
            bunga = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='interest']")))

            invalid_format_value = "100"
            clear_and_input(bunga, invalid_format_value)
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            browser.execute_script("arguments[0].scrollIntoView(true);", statuspinjaman)
            time.sleep(1)

            actual_value = bunga.get_attribute('value')
            expected_value = "99,99"  

            assert actual_value == expected_value, (
                f"Input dengan nilai format '{invalid_format_value}' seharusnya ditampilkan sebagai '{expected_value}', "
                f"tetapi ditemukan '{actual_value}'."
            )

            allure.attach(invalid_format_value, name="Input Bunga Format Tidak Valid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Bunga Format Tidak Valid")

        bunga.clear()

    except Exception as e:
        logging.error(f"Error dalam testcase_034: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Bunga Invalid Format')
@allure.severity(allure.severity_level.NORMAL)
def testcase_38(browser):
    """Testcase *Negatif*: Input minimal bunga dengan format tidak valid

    expect : Range bunga adalah 0.01 - 99.99!
    result : 
    
    """

    try:
        with allure.step("Input Bunga dengan Format Tidak Valid"): 
            statuspinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-status']")))

            browser.execute_script("arguments[0].scrollIntoView(true);", statuspinjaman)
            time.sleep(1)

            bunga = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='interest']")))

            invalid_format_value = "0"
            clear_and_input(bunga, invalid_format_value)
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            browser.execute_script("arguments[0].scrollIntoView(true);", statuspinjaman)
            time.sleep(1)

            error_message = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Range bunga adalah 0.01 - 99.99!')]")))
            error_message_text = error_message.text
            expected_error_message = "Range bunga adalah 0.01 - 99.99!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error minimal bunga")

            allure.attach(invalid_format_value, name="Input Bunga Format Tidak Valid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Bunga Format Tidak Valid")
            
        bunga.clear()

    except Exception as e:
        logging.error(f"Error dalam testcase_067: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Suku Bunga valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_039(browser):
    """Testcase *Positif* pilih Suku bunga dropdown valid.
    
    """
    
    with allure.step("Pilih Suku Bunga"):

        click_suku_bunga = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.XPATH, "//input[@id='interest-rate']")))
        click_suku_bunga.click()
        time.sleep(1)  
        
        suku_bunga_options = ["FLAT", "EFEKTIF"]
        selected_sukubunga = random.choice(suku_bunga_options)
        option_xpath = f'//div[@id="interest-rate-dropdown"]//button[text()="{selected_sukubunga}"]'
        
        option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        option.click()
        time.sleep(1) 
        
        selected_value = click_suku_bunga.get_attribute('value')
        assert selected_value == selected_sukubunga, f"Tenor yang dipilih seharusnya '{selected_sukubunga}', tetapi ditemukan '{selected_value}'."

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        allure.attach(selected_value, name="Input Suku Bunga", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pilih Tenor")
        
        click_suku_bunga.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Suku Bunga dan Input Tidak Valid')
@allure.severity(allure.severity_level.NORMAL)
def testcase_040(browser):
    """Testcase *Negatif* : mencoba input tidak valid setelah memilih suku bunga dari dropdown."""

    try:
        with allure.step("Pilih Suku Bunga dari Dropdown dan Input Tidak Valid"):
            statuspinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-status']")))

            click_suku_bunga = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='interest-rate']")))
            click_suku_bunga.click()
            time.sleep(1)

            suku_bunga_options = ["FLAT", "EFEKTIF"]
            selected_sukubunga = random.choice(suku_bunga_options)
            option_xpath = f'//div[@id="interest-rate-dropdown"]//button[text()="{selected_sukubunga}"]'
            
            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(1)

            selected_value = click_suku_bunga.get_attribute('value')
            assert selected_value == selected_sukubunga, f"Suku bunga yang dipilih seharusnya '{selected_sukubunga}', tetapi ditemukan '{selected_value}'."
            
            invalid_value = "INVALID_INPUT"
            click_suku_bunga.clear()
            slow_typing(click_suku_bunga, invalid_value)
            time.sleep(1)

            click_suku_bunga.send_keys(Keys.RETURN)
            time.sleep(1)
            
            browser.execute_script("arguments[0].scrollIntoView(true);", statuspinjaman)
            time.sleep(1)
            
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih suku bunga!')]")))
            error_message_text = error_message_element.text
            expected_error_message = "Harap pilih suku bunga!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan Input Tidak Valid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error Input Tidak Valid")
            
            click_suku_bunga.clear()

    except Exception as e:
        logging.error(f"Error dalam testcase_036: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Suku Bunga Kosong')
@allure.severity(allure.severity_level.NORMAL)
def testcase_041(browser):
    """Testcase *Negatif*: Pilih suku bunga dari dropdown, kosongkan field, dan verifikasi pesan kesalahan."""

    try:
        with allure.step("Pilih suku bunga dari dropdown dan kosongkan field"):
            statuspinjaman = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='loan-status']")))
            click_suku_bunga = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='interest-rate']")))
            click_suku_bunga.click()
            time.sleep(0.5)

            option_xpath = '//*[@id="interest-rate-dropdown"]/div[1]/button' #reset
            
            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)  

            browser.execute_script("arguments[0].scrollIntoView(true);", statuspinjaman)
            time.sleep(1)

            error_message_element = WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih suku bunga!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap pilih suku bunga!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach("", name="Input Suku Bunga (Kosong)", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Suku Bunga (Kosong)")

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

#----------- tanggal-----#

@allure.feature('Upload Loan Financing')
@allure.story('Input "Tanggal Akad Kredit" *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_042(browser):
    """Testcase *Positif* : input Tanggal Akad Kredit dengan tanggal yang valid.
    2024/09/06
    """
    # switch_to_modal_frame(browser)

    with allure.step("Input Tanggal Akad Kredit dengan Format yang Valid"):
        tanggal_akad_kredit = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='credit-aggrement-date']")))
        
        valid_date_format_1 = "2024/09/06"  # Format YYYY/MM/DD
        clear_and_input(tanggal_akad_kredit, valid_date_format_1)
        actual_value = tanggal_akad_kredit.get_attribute('value')
        allure.attach(actual_value, name="Actual Input Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)
        allure.attach(valid_date_format_1, name="Expected Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)

        klik_main = browser.find_element(By.XPATH, '//body/div[1]/main[1]')
        klik_main.click()
        time.sleep(1)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_akad_kredit)
        time.sleep(1)

        allure.attach(valid_date_format_1, name="Input Akad Kredit", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Akad Kredit Format *Positif*")
        assert actual_value == valid_date_format_1

        clear_and_input(tanggal_akad_kredit, valid_date_format_1)
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Akad Kredit Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_043(browser):
    """Testcase *Negatif* : input Tanggal Akad Kredit dengan tanggal yang tidak ada.

    Catatan: Validasi untuk tanggal yang tidak ada telah ditambahkan ke sistem.
    contoh input 32 sistem akan otomatis menjadi "2024-10-02"
    """

    with allure.step("Input Tanggal Akad Kredit dengan Tanggal Tidak Ada"):
        tanggal_akad_kredit = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='credit-aggrement-date']")))
        
        invalid_date_1 = "2024-09-32"  
        clear_and_input(tanggal_akad_kredit, invalid_date_1)
        time.sleep(1)  

        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)  

        actual_value = tanggal_akad_kredit.get_attribute('value')
        actual_value = actual_value.replace('/', '-')  

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_akad_kredit)
        time.sleep(1)

        allure.attach(invalid_date_1, name="Input Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Akad Kredit Tanggal Tidak Ada")

        expected_date = "2024-10-02"  
        assert actual_value == expected_date, f"Tanggal yang tidak ada seharusnya dikoreksi menjadi {expected_date}."

        clear_and_input(tanggal_akad_kredit, "")

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Akad Kredit Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_044(browser):
    """Testcase *Negatif* :  input Tanggal Akad Kredit dengan bulan yang tidak ada.

    Catatan: Validasi untuk bulan yang tidak ada telah ditambahkan ke sistem.
    contoh input bulan 13 sistem akan otomatis menjadi "bulan : 01"
    """
    with allure.step("Input Tanggal Akad Kredit dengan Bulan Tidak Ada"):
        tanggal_akad_kredit = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='credit-aggrement-date']")))
        
        invalid_date_2 = "2024-13-01"  # Bulan ke-13 tidak valid
        clear_and_input(tanggal_akad_kredit, invalid_date_2)
        time.sleep(1)
        
        actual_value = tanggal_akad_kredit.get_attribute('value')

        # Klik elemen lain untuk memicu validasi
        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_akad_kredit)
        time.sleep(1)

        allure.attach(invalid_date_2, name="Input Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Akad Kredit Bulan Tidak Ada")

#convert
        actual_value = tanggal_akad_kredit.get_attribute('value')
        actual_value = actual_value.replace('/', '-')  

        expected_date = "2024-01-01"  
        assert actual_value == expected_date, f"Bulan yang tidak ada seharusnya dikoreksi menjadi {expected_date}."

        # Clear input setelah verifikasi
        clear_and_input(tanggal_akad_kredit, "")
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Akad Kredit Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_045(browser):
    """Testcase *Negatif*: input Tanggal Akad Kredit dengan format yang salah.

    Catatan: Minor karena menggunakan datepicker.
    """
    try:
        with allure.step("Input Tanggal Akad Kredit dengan Format yang Salah"):
            tanggal_akad_kredit = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='credit-aggrement-date']")))
            
            invalid_date = "01/09/2024"  
            clear_and_input(tanggal_akad_kredit, invalid_date)
            
            browser.find_element(By.XPATH, '//body').click()
            time.sleep(1)

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)
            
            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_akad_kredit)
            time.sleep(1)


            actual_value = tanggal_akad_kredit.get_attribute('value')
            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_akad_kredit)

            allure.attach(invalid_date, name="Input Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Akad Kredit Format Salah")
            assert actual_value == "", "Format tanggal yang salah seharusnya tidak diterima dan input harus kosong."

            with allure.step("Verifikasi Pesan Kesalahan"):
                error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih tanggal akad kredit!')]")))
                error_message_text = error_message_element.text

                expected_error_message = "Harap pilih tanggal akad kredit!"
                assert expected_error_message in error_message_text, (
                    f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                    f"Pesan kesalahan yang ditemukan '{error_message_text}'."
                )

                allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
                allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

    except Exception as e:
        logging.error(f"Terjadi kesalahan dalam testcase_041: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Input Tanggal Akad Kredit Tidak Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_046(browser):
    """Testcase *Negatif* input Tanggal Akad Kredit yang kosong.

     """

    with allure.step("Input Tanggal Akad Kredit Kosong"):
        tanggal_akad_kredit = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='credit-aggrement-date']")))
        
        clear_and_input(tanggal_akad_kredit, "")
        time.sleep(1)
        
        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = tanggal_akad_kredit.get_attribute('value')

        browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_akad_kredit)
        time.sleep(1)

        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Akad Kredit Kosong")

        assert actual_value == "", "Tanggal batch yang kosong seharusnya tetap kosong."
        allure.attach(actual_value, name="Input Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)
        
        clear_and_input(tanggal_akad_kredit, "")

        browser.find_element(By.XPATH, '//body').click()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Tanggal Angsuran Valid Satu Digit *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_047(browser):
    """Testcase *Positif* : input Tanggal Angsuran dengan data valid satu digit"""
    
    with allure.step("Input Tanggal Angsuran Valid Satu Digit"):
        tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))
        valid_dates = ["1", "9"]
        input_tanggal_angsuran = random.choice(valid_dates)
        slow_typing(tanggal_angsuran, input_tanggal_angsuran)

        btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
        btn_validasi.click()
        time.sleep(1)

        actual_value = tanggal_angsuran.get_attribute('value')
        assert actual_value == input_tanggal_angsuran, f"Tanggal angsuran yang valid seharusnya '{input_tanggal_angsuran}', tetapi ditemukan '{actual_value}'."

        browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran)
        time.sleep(1)
        
        allure.attach(input_tanggal_angsuran, name="Input Tanggal Angsuran Valid Satu Digit", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Angsuran Valid Satu Digit")

        tanggal_angsuran.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Tanggal Angsuran Valid Dua Digit *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_048(browser):
    """Testcase *Positif* : input Tanggal Angsuran dengan data valid dua digit (10-31)"""
    
    with allure.step("Input Tanggal Angsuran Valid Dua Digit"):
        tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))
        valid_dates = ["10", "25", "31"]
        input_tanggal_angsuran = random.choice(valid_dates)
        slow_typing(tanggal_angsuran, input_tanggal_angsuran)

        btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
        btn_validasi.click()
        time.sleep(1)

        actual_value = tanggal_angsuran.get_attribute('value')
        assert actual_value == input_tanggal_angsuran, f"Tanggal angsuran yang valid seharusnya '{input_tanggal_angsuran}', tetapi ditemukan '{actual_value}'."
        
        browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran)
        time.sleep(1)

        allure.attach(input_tanggal_angsuran, name="Input Tanggal Angsuran Valid Dua Digit", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Angsuran Valid Dua Digit")
        tanggal_angsuran.clear()
        time.sleep(1)


@allure.feature('Upload Loan Financing')
@allure.story('Tanggal Angsuran Invalid Nilai Nol *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_049(browser):
    """Testcase *Negatif* : Input Tanggal Angsuran dengan nilai nol expect sistem akan otomatis kosong"""
    
    try:
        with allure.step("Input Tanggal Angsuran Dengan Nilai Nol"):
            tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))

            invalid_value = "0"
            tanggal_angsuran.clear()  # Pastikan field kosong sebelum mengetik
            tanggal_angsuran.send_keys(invalid_value)

            tanggal_angsuran.send_keys(Keys.RETURN)
            time.sleep(1)

            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi tanggal angsuran!')]")))
            error_message_text = error_message_element.text
            assert "Harap isi tanggal angsuran!" in error_message_text, (
                f"Pesan kesalahan yang diharapkan tidak ditemukan. Pesan yang ditemukan: {error_message_text}"
            )

            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran)
            time.sleep(1)

            allure.attach(invalid_value, name="Input Tanggal Angsuran Nilai Nol", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Angsuran Nilai Nol")

    except Exception as e:
        logging.error(f"Error dalam testcase_045: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Tanggal Angsuran Invalid Nilai Lebih Dari 31 *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_050(browser):
    """Testcase *Negatif* input Tanggal Angsuran dengan nilai lebih dari 31 yang otomatis menjadi 31"""
    
    try:
        with allure.step("Input Tanggal Angsuran Dengan Nilai Lebih Dari 31"):
            tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))
            invalid_value = "32"
            slow_typing(tanggal_angsuran, invalid_value)
            tanggal_angsuran.send_keys(Keys.RETURN)
            time.sleep(1)

            actual_value = tanggal_angsuran.get_attribute('value')
            assert actual_value == "31", "Input dengan nilai lebih dari 31 seharusnya otomatis menjadi 31."

            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran)
            time.sleep(1)
            
            allure.attach(invalid_value, name="Input Tanggal Angsuran Nilai Lebih Dari 31", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Angsuran Nilai Lebih Dari 31")
            tanggal_angsuran.clear()
            time.sleep(1)

    except Exception as e:
        logging.error(f"Error dalam tanggal_angsuran_*Negatif*_02: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Tanggal Angsuran Invalid Format *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_051(browser):
    """Testcase *Negatif* untuk input Tanggal Angsuran dengan format salah
    
    Contoh : input 01 akan otomatis menjadi 1
    """
    
    try:
        with allure.step("Input Tanggal Angsuran Dengan Format Salah"):
            tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))
            invalid_value = "01"  
            slow_typing(tanggal_angsuran, invalid_value)
            tanggal_angsuran.send_keys(Keys.RETURN)
            time.sleep(1)

            actual_value = tanggal_angsuran.get_attribute('value')
            assert actual_value == "1", "Input dengan format tanggal yang salah seharusnya dikoreksi menjadi format yang benar."

            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran)
            time.sleep(1)
            
            allure.attach(invalid_value, name="Input Tanggal Angsuran Format Salah", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tanggal Angsuran Format Salah")

            tanggal_angsuran.clear()
            time.sleep(1)

    except Exception as e:
        logging.error(f"Error dalam tanggal_angsuran_*Negatif*_03: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise  

@allure.feature('Upload Loan Financing')
@allure.story('Tanggal Angsuran Kosong Setelah Valid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_052(browser):
    """Testcase *Negatif*: Input Tanggal Angsuran dengan data valid, lalu kosongkan field dan verifikasi pesan kesalahan."""
    
    with allure.step("Input dan Kosongkan Tanggal Angsuran"):
        tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))
        tanggal_angsuran.clear()
        tanggal_angsuran.send_keys(Keys.RETURN)
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran)
        time.sleep(2)

        error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi tanggal angsuran!')]")))
        error_message_text = error_message_element.text

        # Pastikan pesan kesalahan sesuai dengan yang diharapkan
        expected_error_message = "Harap isi tanggal angsuran!"
        assert expected_error_message in error_message_text, (
            f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
            f"Pesan kesalahan yang ditemukan '{error_message_text}'."
        )

        allure.attach("", name="Input Tanggal Angsuran Valid", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Kosongkan Tanggal Angsuran")

        # Kosongkan field
        tanggal_angsuran.clear()
        time.sleep(1) 

#---------skenario tanggal angsuran-------------#

@allure.feature('Upload Loan Financing')
@allure.story('Skenario Tanggal Angsuran')
@allure.severity(allure.severity_level.NORMAL)
def testcase_053(browser):
    """
    * Data Uji:
    - Tenor: 3 bulan
    - Tanggal Akad Kredit: 2025/01/25
    - Tanggal Angsuran: 31

    Harapan: angsuran pertama 2025-02-28 dan angsuran terakhir dibayar 2025-05-31
    """
    try:
        with allure.step("Input Tenor"):
            # browser.execute_script("arguments[0].scrollIntoView(true);", click_tenor)
            # reset_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()=' -- Reset --']")))
            # reset_button.click()
            # time.sleep(1)

            click_tenor = WebDriverWait(browser, 10).until( EC.element_to_be_clickable((By.XPATH, "//input[@id='tenor']")))
            click_tenor.clear()
            click_tenor.click()
            time.sleep(0.5)  
            
            tenor_options = ["3 Bulan"]
            selected_tenor = random.choice(tenor_options)
            option_xpath = f'//div[@id="tenor-dropdown"]//button[text()="{selected_tenor}"]'
            
            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(1) 

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tenor", attachment_type=allure.attachment_type.PNG)

        with allure.step("Input Tanggal Akad Kredit"):
            tanggal_akad_kredit = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='credit-aggrement-date']")))
            valid_date_format_1 = "2025/01/25"
            clear_and_input(tanggal_akad_kredit, valid_date_format_1)

            actual_value = tanggal_akad_kredit.get_attribute('value')
            allure.attach(actual_value, name="Actual Input Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)
            allure.attach(valid_date_format_1, name="Expected Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)

            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//body/div[1]/main[1]'))).click()

            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_akad_kredit)
            time.sleep(2)

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Set Tanggal Akad Kredit", attachment_type=allure.attachment_type.PNG)

        with allure.step("Input Tanggal Angsuran"):
            tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))
            valid_dates = "31"
            slow_typing(tanggal_angsuran, valid_dates)
            tanggal_angsuran.send_keys(Keys.RETURN)
            time.sleep(1)

            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran)
            time.sleep(2)

            allure.attach(tanggal_angsuran.get_attribute('value'), name="Input Tanggal Angsuran", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Set Tanggal Angsuran", attachment_type=allure.attachment_type.PNG)

        with allure.step("Verifikasi Tanggal Angsuran Pertama Dibayar"):
            tanggal_angsuran_pertama = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='first-installment-date-paid']")))
            expected_first_installment_date = "2025/02/28"
            actual_first_installment_date = tanggal_angsuran_pertama.get_attribute('value')

            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran_pertama)
            time.sleep(2)

            logging.info(f"Actual Tanggal Angsuran Pertama Dibayar: '{actual_first_installment_date}'")
            allure.attach(actual_first_installment_date, name="Tanggal Angsuran Pertama Dibayar", attachment_type=allure.attachment_type.TEXT)

            assert actual_first_installment_date == expected_first_installment_date, \
                f"Harapan Tanggal Angsuran Pertama Dibayar '{expected_first_installment_date}', tetapi ditemukan '{actual_first_installment_date}'"

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Tanggal Angsuran Pertama Dibayar", attachment_type=allure.attachment_type.PNG)

        with allure.step("Verifikasi Tanggal Angsuran Terakhir Dibayar"):
            tanggal_angsuran_terakhir = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='last-installment-date-paid']")))
            expected_last_installment_date = "2025/05/31"
            actual_last_installment_date = tanggal_angsuran_terakhir.get_attribute('value')

            browser.execute_script("arguments[0].scrollIntoView(true);", tanggal_angsuran_terakhir)
            time.sleep(2)

            logging.info(f"Actual Tanggal Angsuran Terakhir Dibayar: '{actual_last_installment_date}'")
            allure.attach(actual_last_installment_date, name="Tanggal Angsuran Terakhir Dibayar", attachment_type=allure.attachment_type.TEXT)

            assert actual_last_installment_date == expected_last_installment_date, \
                f"Harapan Tanggal Angsuran Terakhir Dibayar '{expected_last_installment_date}', tetapi ditemukan '{actual_last_installment_date}'"

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Tanggal Angsuran Terakhir Dibayar", attachment_type=allure.attachment_type.PNG)

        click_tenor.clear()

    except Exception as e:
        logging.error(f"error: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Skenario Tanggal Angsuran Tahun Kabisat')
@allure.severity(allure.severity_level.NORMAL)
def testcase_054(browser):
    """
    * Data Uji:
    - Tenor: 3 bulan
    - Tanggal Akad Kredit: 2028/01/25
    - Tanggal Angsuran: 31

    Harapan: angsuran pertama 2028-02-29 dan angsuran terakhir dibayar 2028-05-31
    """
    try:
        with allure.step("Input Tenor"):
            click_tenor = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='tenor']")))
            click_tenor.click()

            tenor_options = ["3 Bulan"]
            selected_tenor = random.choice(tenor_options)
            option_xpath = f'//div[@id="tenor-dropdown"]//button[text()="{selected_tenor}"]'

            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Tenor", attachment_type=allure.attachment_type.PNG)

        with allure.step("Input Tanggal Akad Kredit"):
            tanggal_akad_kredit = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='credit-aggrement-date']")))
            valid_date_format_1 = "2028/01/25"
            clear_and_input(tanggal_akad_kredit, valid_date_format_1)

            actual_value = tanggal_akad_kredit.get_attribute('value')
            allure.attach(actual_value, name="Actual Input Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)
            allure.attach(valid_date_format_1, name="Expected Tanggal Akad Kredit", attachment_type=allure.attachment_type.TEXT)

            # Klik di luar elemen input untuk menyimpan perubahan
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//body/div[1]/main[1]'))).click()

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Set Tanggal Akad Kredit", attachment_type=allure.attachment_type.PNG)

        with allure.step("Input Tanggal Angsuran"):
            tanggal_angsuran = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='installment-date']")))
            valid_dates = "31"
            slow_typing(tanggal_angsuran, valid_dates)
            tanggal_angsuran.send_keys(Keys.RETURN)

            allure.attach(tanggal_angsuran.get_attribute('value'), name="Input Tanggal Angsuran", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Set Tanggal Angsuran", attachment_type=allure.attachment_type.PNG)

        with allure.step("Verifikasi Tanggal Angsuran Pertama Dibayar"):
            tanggal_angsuran_pertama = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='first-installment-date-paid']")))
            expected_first_installment_date = "2028/02/29"
            actual_first_installment_date = tanggal_angsuran_pertama.get_attribute('value')

            logging.info(f"Actual Tanggal Angsuran Pertama Dibayar: '{actual_first_installment_date}'")
            allure.attach(actual_first_installment_date, name="Tanggal Angsuran Pertama Dibayar", attachment_type=allure.attachment_type.TEXT)

            assert actual_first_installment_date == expected_first_installment_date, \
                f"Harapan Tanggal Angsuran Pertama Dibayar '{expected_first_installment_date}', tetapi ditemukan '{actual_first_installment_date}'"

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Tanggal Angsuran Pertama Dibayar", attachment_type=allure.attachment_type.PNG)

        with allure.step("Verifikasi Tanggal Angsuran Terakhir Dibayar"):
            tanggal_angsuran_terakhir = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='last-installment-date-paid']")))
            expected_last_installment_date = "2028/05/31"
            actual_last_installment_date = tanggal_angsuran_terakhir.get_attribute('value')

            logging.info(f"Actual Tanggal Angsuran Terakhir Dibayar: '{actual_last_installment_date}'")
            allure.attach(actual_last_installment_date, name="Tanggal Angsuran Terakhir Dibayar", attachment_type=allure.attachment_type.TEXT)

            assert actual_last_installment_date == expected_last_installment_date, \
                f"Harapan Tanggal Angsuran Terakhir Dibayar '{expected_last_installment_date}', tetapi ditemukan '{actual_last_installment_date}'"

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Tanggal Angsuran Terakhir Dibayar", attachment_type=allure.attachment_type.PNG)

    except Exception as e:
        logging.error(f"Terjadi kesalahan dalam skenario_054: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

#------------ Jaminan -------------#

@allure.feature('Upload Loan Financing')
@allure.story('Jenis Jaminan/Agunan invalid *Negatif*')
@allure.severity(allure.severity_level.CRITICAL)
def testcase_055(browser):

    """Testcase *Negatif*: tidak memilih Jenis Jaminan/Agunan dan mencoba submit."""
    
    try:
        with allure.step("Coba submit tanpa memilih Jenis Jaminan/Agunan"):
            Jenis_jaminan = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='collateral']")))
            Jenis_jaminan.clear()

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)


            browser.execute_script("arguments[0].scrollIntoView(true);", Jenis_jaminan)
            time.sleep(1)
            
  
            error_message = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih jenis jaminan/agunan!')]")))
            browser.execute_script("arguments[0].scrollIntoView(true);", Jenis_jaminan)
            assert "Harap pilih jenis jaminan/agunan!" in error_message.text, ("Pesan kesalahan yang diharapkan 'Harap pilih jenis jaminan/agunan!' tidak ditemukan.")
            
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error Pesan")
            Jenis_jaminan.clear()
            time.sleep(1)
    
    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Jenis Jaminan/Agunan Invalid *Negatif*')
@allure.severity(allure.severity_level.CRITICAL)
def testcase_056(browser):
    """Testcase *Negatif* : memilih Jenis Jaminan/Agunan valid dan input ke dalam textbox "invalid"."""

    try:
        with allure.step("Pilih Jenis Jaminan/Agunan yang valid, lalu coba input tidak valid dan submit"):

            click_Jenis_Jaminan = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='collateral']")))
            click_Jenis_Jaminan.click()
            time.sleep(0.5)
            
            JenisJaminan_options = ["BPKB", "SHGB", "Akta Jual Beli (AJB)", "SK Pensiun"]
            selected_Jenis_Jaminan = random.choice(JenisJaminan_options)
            option_xpath = f'//div[@id="collateral-dropdown"]//button[text()="{selected_Jenis_Jaminan}"]'
            
            option = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            time.sleep(1)

            invalid_input = "Invalid "
            click_Jenis_Jaminan.clear()
            click_Jenis_Jaminan.send_keys(invalid_input)
            click_Jenis_Jaminan.send_keys(Keys.RETURN)

            time.sleep(1)
            
            browser.execute_script("arguments[0].scrollIntoView(true);", click_Jenis_Jaminan)
            time.sleep(1)

            
            error_message = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap pilih jenis jaminan/agunan!')]"))).text
            assert "Harap pilih jenis jaminan/agunan!" in error_message, f"Pesan kesalahan yang diharapkan 'Harap pilih jenis jaminan/agunan!' tidak ditemukan. Pesan ditemukan: '{error_message}'"
            
            allure.attach(invalid_input, name="Input Jenis Jaminan invalid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error Pesan")

            click_Jenis_Jaminan.clear()
            time.sleep(1)

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise


@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_057(browser):
    """Testcase *Positif* : input Nilai Jaminan dengan data valid *Only Number"""
    # switch_to_modal_frame(browser)
    
    with allure.step("Input Nilai Jaminan"):
        nilai_jaminan = browser.find_element(By.XPATH, "//input[@id='collateral-value']")
        input_nilaijaminan = random.choice(["100000", "250000", "300000"])
        slow_typing(nilai_jaminan, input_nilaijaminan)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan)
        time.sleep(1)

        allure.attach(input_nilaijaminan, name="Input Nilai Jaminan", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan")
        nilai_jaminan.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_058(browser):
    """Testcase *Negatif*: tidak mengisi nilai jaminan.
    
    input nilai jaminan Kosong
    """

    try:
        with allure.step("Input Nilai Jaminan Kosong"):
            nilai_jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))
            
            clear_and_input(nilai_jaminan, "")
            time.sleep(1)  # Tunggu beberapa saat untuk memastikan perubahan diterapkan
            
            # Klik tombol validasi
            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)  # Tunggu beberapa saat untuk proses klik

            # Ambil nilai aktual dari elemen input
            actual_value = nilai_jaminan.get_attribute('value').strip()
            browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan)
            time.sleep(1) 

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan Kosong")
            
            assert actual_value == "", "Nilai Jaminan tidak boleh kosong."

    except Exception as e:
        logging.error(f"Error dalam testcase nilai_jaminan_invalid_*Negatif*: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_059(browser):
    """Testcase *Negatif* : input Nilai Jaminan dengan karakter non-numerik.
    
    Catatan: Sistem telah update untuk menolak karakter non-numerik dan input harus kosong.
    """
    
    with allure.step("Input Nilai Jaminan dengan Karakter Non-Numerik"):
        nilai_jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))
        invalid_value = "abc!@#"

        clear_and_input(nilai_jaminan, invalid_value)
        time.sleep(1)  

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = nilai_jaminan.get_attribute('value')

        browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan)
        time.sleep(1)
        allure.attach(invalid_value, name="input Nilai Jaminan", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan Non-Numerik")
        
        assert actual_value == "", "Nilai Jaminan dengan karakter non-numerik seharusnya tidak diterima dan input harus kosong."
        nilai_jaminan.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan Invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_060(browser):
    """Testcase *Negatif* : input Nilai Jaminan dengan angka *Negatif*.
    
    catatan : Sistem telah update untuk *Negatif* (-) tidak di terima.
    """

    with allure.step("Input Nilai Jaminan dengan Angka *Negatif*"):
        Nilai_jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))
        invalid_value = "-50000"
        clear_and_input(Nilai_jaminan, invalid_value)
        time.sleep(1) 

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)

        actual_value = Nilai_jaminan.get_attribute('value')

        browser.execute_script("arguments[0].scrollIntoView(true);", Nilai_jaminan)
        time.sleep(1)

        allure.attach(invalid_value, name="input Nilai Jaminan", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan *Negatif*")
        
        assert actual_value == "50.000", "Sistem menghilangkan (-) di depan angka"
        Nilai_jaminan.clear()

        time.sleep(1)
        print(f"Actual value: {actual_value}")

# @allure.feature('Upload Loan Financing')
# @allure.story('Nilai Jaminan Invalid *Negatif*')
# @allure.severity(allure.severity_level.NORMAL)
# def testcase_061(browser):
#     """Testcase *Negatif* input Nilai Jaminan dengan angka terlalu besar.
    
#     perlu di konfirmasi : Sistem belum ada validasi Max Nilai Jaminan.
#     """

#     with allure.step("Input Nilai Jaminan dengan Angka Terlalu Besar"):
#         Nilai_Jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))
#         invalid_value = "1000000000000000" 
#         clear_and_input(Nilai_Jaminan, invalid_value)
#         time.sleep(1) 

#         btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
#         btn_validasi.click()
#         time.sleep(1)

#         actual_value = Nilai_Jaminan.get_attribute('value')

#         browser.execute_script("arguments[0].scrollIntoView(true);", Nilai_Jaminan)
#         time.sleep(1)

#         allure.attach(invalid_value, name="input Nilai Jaminan", attachment_type=allure.attachment_type.TEXT)
#         allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan Terlalu Besar")
        
#         assert actual_value == "", "Nilai Jaminan dengan angka terlalu besar seharusnya tidak diterima."
#         print(f"Actual value: {actual_value}")
#         Nilai_Jaminan.clear()
#         time.sleep(1)
        

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan Invalid Format')
@allure.severity(allure.severity_level.NORMAL)
def testcase_061(browser):
    """Testcase *Negatif*: Input nilai jaminan dengan format tidak valid (contoh, koma berulang 20 kali)"""

    try:
        with allure.step("Input Nilai Jaminan dengan Format Tidak Valid"):
            nilai_jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))

            invalid_value = "," * 20  # koma berulang 20 kali
            clear_and_input(nilai_jaminan, invalid_value)
            time.sleep(2)  

            nilai_jaminan.send_keys(Keys.RETURN)
            time.sleep(1)

            browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan)
            time.sleep(2) 

            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nilai jaminan!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            time.sleep(1)
            allure.attach(invalid_value, name="Input Nilai Jaminan Format Tidak Valid", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan Format Tidak Valid")

            nilai_jaminan.clear()

    except Exception as e:
        logging.error(f"Error dalam testcase nilai_jaminan_format_invalid: {str(e)}")
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan di isi Nol Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_062(browser):
    """Testcase Negatif: mencoba Input Nilai Jaminan dengan "0" 
    
    kena validasi : "Harap isi Nilai Jaminan!"
    """
    
    with allure.step("Input Nilai Jaminan dengan nilai Nol"):
        nilai_jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))

        input_non_numerik = "0"
        nilai_jaminan.clear()
        slow_typing(nilai_jaminan, input_non_numerik)

        nilai_jaminan.send_keys(Keys.RETURN)
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan)
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nilai Jaminan Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nilai jaminan!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error : {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nilai_jaminan.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan di isi desimal Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_063(browser):
    """Testcase Negatif: mencoba Input Nilai Jaminan dengan angka desimal

    0,02
    
    kena validasi : "Harap isi Nilai Jaminan!"
    """
    
    with allure.step("Input Nilai Jaminan dengan nilai Desimal"):
        nilai_jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))

        input_non_numerik = "0,02"
        nilai_jaminan.clear()
        slow_typing(nilai_jaminan, input_non_numerik)

        nilai_jaminan.send_keys(Keys.RETURN)
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan)
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nilai Jaminan Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nilai jaminan!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error : {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nilai_jaminan.clear()
        time.sleep(1)



@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan Nol berulang Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_064(browser):
    """Testcase Negatif: mencoba Input Nilai Jaminan dengan "Nol" berulang dan verifikasi pesan kesalahan.
    
    """
    
    with allure.step("Input Nilai Jaminan dengan Karakter Non-Numerik"):
        nilai_jaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value']")))

        input_non_numerik = "0" * 20
        nilai_jaminan.clear()
        slow_typing(nilai_jaminan, input_non_numerik)

        nilai_jaminan.send_keys(Keys.RETURN)
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan)
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nilai Jaminan Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nilai jaminan!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error : {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nilai_jaminan.clear()
        time.sleep(1)


@allure.feature('Upload Loan Financing')
@allure.story('Nomor Jaminan Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_065(browser):
    """Testcase *Positif* input Nomor Jaminan valid
    
    catatan : only numeric
    """
    # switch_to_modal_frame(browser)
    
    with allure.step("Input Nomor Jaminan"):
        NomorJaminan = browser.find_element(By.XPATH, "//input[@id='collateral-number']")
        InputNomorJaminan = fake.numerify('05#########')
        slow_typing(NomorJaminan, InputNomorJaminan)

        btn_validasi = browser.find_element(By.XPATH, "//button[contains(text(),'AJUKAN')]")
        btn_validasi.click()
        time.sleep(1)
        
        browser.execute_script("arguments[0].scrollIntoView(true);", NomorJaminan)
        time.sleep(1)
                   
        allure.attach(InputNomorJaminan, name="Input Nomor Jaminan", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nomor Jaminan")
        NomorJaminan.clear()
        time.sleep(1)

@allure.feature('Upload Loan Financing')
@allure.story('Nomor Jaminan Invalid *Negatif*')
@allure.severity(allure.severity_level.CRITICAL)
def testcase_066(browser):
    """Testcase *Negatif* input Nomor Jaminan kosong"""
    try:
        with allure.step("Input Nomor Jaminan Kosong"):
            NomorJaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-number']")))

            NomorJaminan.clear()
            NomorJaminan.send_keys("")

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)

            browser.execute_script("arguments[0].scrollIntoView(true);", NomorJaminan)
            time.sleep(1)

            error_message = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan!')]")))
            assert "Harap isi nomor jaminan!" in error_message.text, "Pesan kesalahan untuk input kosong atau tidak ditemukan."

            input_value = NomorJaminan.get_attribute('value')
            allure.attach(f"Input value: '{input_value}'", name="Input Nomor Jaminan Value", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error Nomor Jaminan Kosong")

            NomorJaminan.clear()

    except Exception as e:
        browser.execute_script("arguments[0].scrollIntoView(true);", NomorJaminan)
        time.sleep(1)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise


# @allure.feature('Upload Loan Financing')
# @allure.story('Nomor Jaminan Invalid *Negatif*')
# @allure.severity(allure.severity_level.CRITICAL)
# def testcase_068(browser):
#     """Testcase *Negatif* input Nomor Jaminan dengan karakter non-numerik dan khusus,
#        Sistem memeriksa dan menghapus otomatis"""
#     try:
#         with allure.step("Input Nomor Jaminan dengan Karakter Tidak Valid"):
#             NomorJaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-number']")))

#             invalid_value = "abc!@#!$"

#             NomorJaminan.clear()
#             NomorJaminan.send_keys(invalid_value)
#             time.sleep(2)  # Tambah waktu tunggu untuk memastikan sistem memproses input

#             remaining_value = NomorJaminan.get_attribute('value')
#             assert remaining_value == '', f"Textbox harus kosong setelah mengisi selain angka otomatis untuk nilai '{invalid_value}'. validasi otomatis sistem: '{remaining_value}'."
    
#     except AssertionError as e:
#         allure.attach(browser.get_screenshot_as_png(), name="Screenshot", attachment_type=allure.attachment_type.PNG)
#         raise e

# @allure.feature('Upload Loan Financing')
# @allure.story('Nomor Jaminan Invalid *Negatif*')
# @allure.severity(allure.severity_level.CRITICAL)
# def testcase_069(browser):
#     """Testcase *Negatif* input Nomor Jaminan terlalu panjang
    
#     Catatan: Sistem tidak memiliki validasi min dan max untuk nomor jaminan.
#     """
#     try:
#         with allure.step("Input Nomor Jaminan Terlalu Panjang"):
#             NomorJaminan = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-number']")))

#             NomorJaminan.clear()
#             NomorJaminan.send_keys("12345678901234567890")  

#             btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
#             btn_validasi.click()
#             time.sleep(2)  

#             browser.execute_script("arguments[0].scrollIntoView(true);", NomorJaminan)
#             time.sleep(1)

#             # Jika tidak ada validasi panjang, mungkin tidak ada pesan kesalahan
#             # Cek kondisi atau log lainnya yang relevan dengan aplikasi
#             # Misalnya, memverifikasi apakah input masih ada atau sistem menerima input panjang
            
#             # Jika tidak ada pesan kesalahan, Anda bisa verifikasi kondisi lain seperti data berhasil diproses atau tidak
#             # Contoh:
#             # input_value = NomorJaminan.get_attribute('value')
#             # assert input_value == "12345678901234567890", "Input panjang tidak diterima oleh sistem."

#             allure.attach(f"Value entered: {'12345678901234567890'}", name="Input Nomor Jaminan", attachment_type=allure.attachment_type.TEXT) 
#             allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nomor Jaminan Panjang")

#             time.sleep(1)

#             NomorJaminan.clear()

#     except Exception as e:
#         allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
#         raise

@allure.feature('Upload Loan Financing')
@allure.story('Jenis Jaminan 2 dan Nilai Jaminan 2 Valid *Positif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_067(browser):
    """Testcase *Positif*: Jenis Jaminan 2 dan Nilai Jaminan 2 diisi dengan benar"""
    try:
        with allure.step("Pilih Jenis Jaminan 2 dari dropdown"):
            click_Jenis_Jaminan_2 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='collateral-2']")))
            click_Jenis_Jaminan_2.click()
            time.sleep(0.5)
            
            JenisJaminan_options_2 = ["BPKB", "SHGB", "Akta Jual Beli (AJB)", "SK Pensiun"]
            selected_Jenis_Jaminan_2 = random.choice(JenisJaminan_options_2)
            option_xpath_2 = f'//div[@id="collateral-2-dropdown"]//button[text()="{selected_Jenis_Jaminan_2}"]'
            
            option_2 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath_2)))
            option_2.click()
            time.sleep(1)
            
            selected_value_2 = click_Jenis_Jaminan_2.get_attribute('value')
            assert selected_value_2 == selected_Jenis_Jaminan_2, f"Jenis Jaminan yang dipilih seharusnya '{selected_Jenis_Jaminan_2}', tetapi ditemukan '{selected_value_2}'."

        with allure.step("Isi Nilai Jaminan 2"):
            nilai_jaminan_2 = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value-2']")))
            valid_nilai_jaminan_2 = "20000000"  
            nilai_jaminan_2.clear()
            
            nilai_jaminan_2.send_keys(valid_nilai_jaminan_2)
            time.sleep(1)

            nilai_jaminan_2.send_keys(Keys.RETURN)
            time.sleep(1)

            error_message_elements = browser.find_elements(By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan 2!')]")
            browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan_2)
            assert len(error_message_elements) == 0, "Pesan kesalahan untuk nilai jaminan yang valid muncul, padahal seharusnya tidak ada."

            browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan_2)
            time.sleep(1)

            allure.attach(nilai_jaminan_2.get_attribute('value'), name="Nilai Jaminan 2", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Validasi Jenis dan Nilai Jaminan 2")
            time.sleep(1)

            nilai_jaminan_2.clear()

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        raise

@allure.feature('Upload Loan Financing')
@allure.story('Jenis Jaminan 2 diisi dan Nilai Jaminan 2 tidak diisi invalid *Negatif*')
@allure.severity(allure.severity_level.NORMAL)
def testcase_068(browser):
    """Testcase *Negatif*: Jenis Jaminan 2 diisi dan Nilai Jaminan 2 tidak diisi"""
    try:
        with allure.step("Pilih Jenis Jaminan 2 dari dropdown"):
            click_Jenis_Jaminan_2 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='collateral-2']")))
            click_Jenis_Jaminan_2.click()

            JenisJaminan_options_2 = ["BPKB", "SHGB", "Akta Jual Beli (AJB)", "SK Pensiun"]
            selected_Jenis_Jaminan_2 = random.choice(JenisJaminan_options_2)
            option_xpath_2 = f'//div[@id="collateral-2-dropdown"]//button[text()="{selected_Jenis_Jaminan_2}"]'
            
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot dropdown Jenis Jaminan 2")

            option_2 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath_2)))
            option_2.click()


            time.sleep(1)

            selected_value_2 = click_Jenis_Jaminan_2.get_attribute('value')
            assert selected_value_2 == selected_Jenis_Jaminan_2, (
                f"Jenis Jaminan yang dipilih seharusnya '{selected_Jenis_Jaminan_2}', "
                f"tetapi ditemukan '{selected_value_2}'."
            )

        with allure.step("Validasi tanpa mengisi Nilai Jaminan 2"):

            btn_validasi = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'AJUKAN')]")))
            btn_validasi.click()
            time.sleep(1)
            browser.execute_script("arguments[0].scrollIntoView(true);", click_Jenis_Jaminan_2)
            time.sleep(1)
            
            error_message = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan 2!')]")))
            error_message_text = error_message.text
            expected_error_message = "Harap isi nilai jaminan 2!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error Nilai Jaminan 2 Kosong")

    except Exception as e:
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
        logging.error(f"Terjadi kesalahan dalam testcase_065: {str(e)}")
        raise


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

@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan 2 di isi desimal Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_071(browser):
    """Testcase Negatif: mencoba Input Nilai Jaminan 2 dengan angka desimal

    0,02
    
    kena validasi : "Harap isi Nilai Jaminan 2!"
    """
    
    with allure.step("Input Nilai Jaminan 2 dengan nilai Desimal"):
        nilai_jaminan2 = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value-2']")))
        
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='collateral-value-2']")))

        input_desimal = "0.02"
        
        nilai_jaminan2.clear()
        time.sleep(0.5)
        nilai_jaminan2.send_keys(input_desimal)

        nilai_jaminan2.send_keys(Keys.RETURN)
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan2)
        time.sleep(1)

        allure.attach(input_desimal, name="Input Nilai Jaminan 2 Desimal", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan 2 Desimal")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan 2!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nilai jaminan 2!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error : {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise
        
        nilai_jaminan2.clear()
        time.sleep(1)


@allure.feature('Upload Loan Financing')
@allure.story('Nilai Jaminan 2 Nol berulang Negatif')
@allure.severity(allure.severity_level.NORMAL)
def testcase_072(browser):

    """Testcase Negatif: mencoba Input Nilai Jaminan 2 dengan "Nol" berulang dan verifikasi pesan kesalahan.
    
    """
    
    with allure.step("Input Nilai Jaminan 2 dengan Karakter Non-Numerik"):
        nilai_jaminan2 = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='collateral-value-2']")))

        input_non_numerik = "0" * 20
        nilai_jaminan2.clear()
        slow_typing(nilai_jaminan2, input_non_numerik)

        nilai_jaminan2.send_keys(Keys.RETURN)
        time.sleep(1)

        browser.execute_script("arguments[0].scrollIntoView(true);", nilai_jaminan2)
        time.sleep(1)

        allure.attach(input_non_numerik, name="Input Nilai Jaminan 2 Non-Numerik", attachment_type=allure.attachment_type.TEXT)
        allure.attach(browser.get_screenshot_as_png(), name="Screenshot Input Nilai Jaminan 2 Non-Numerik")

        try:
            error_message_element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'Harap isi nilai jaminan 2!')]")))
            error_message_text = error_message_element.text

            expected_error_message = "Harap isi nilai jaminan 2!"
            assert expected_error_message in error_message_text, (
                f"Pesan kesalahan yang diharapkan '{expected_error_message}' tidak ditemukan. "
                f"Pesan kesalahan yang ditemukan '{error_message_text}'."
            )

            allure.attach(error_message_text, name="Pesan Kesalahan", attachment_type=allure.attachment_type.TEXT)
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Pesan Kesalahan")

        except Exception as e:
            logging.error(f"Error : {str(e)}")
            allure.attach(browser.get_screenshot_as_png(), name="Screenshot Error", attachment_type=allure.attachment_type.PNG)
            raise

        nilai_jaminan2.clear()
        time.sleep(1)