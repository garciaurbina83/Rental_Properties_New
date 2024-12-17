import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime

pytestmark = pytest.mark.e2e

def test_property_creation_flow(selenium_driver, test_data):
    """Test the complete flow of creating a new property"""
    driver = selenium_driver
    
    # Login (assuming we have a login page)
    driver.get("http://localhost:3000/login")
    
    # Wait for login form and fill credentials
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    password_input = driver.find_element(By.NAME, "password")
    
    email_input.send_keys("test@example.com")
    password_input.send_keys("password")
    password_input.send_keys(Keys.RETURN)
    
    # Wait for dashboard to load and click "Add Property" button
    add_property_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "add-property-btn"))
    )
    add_property_btn.click()
    
    # Fill property form
    property_data = test_data["property"]
    
    name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "name"))
    )
    name_input.send_keys(property_data["address"])
    
    driver.find_element(By.NAME, "type").send_keys(property_data["type"])
    driver.find_element(By.NAME, "rentAmount").send_keys(str(property_data["rentAmount"]))
    
    # Submit form
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()
    
    # Verify success message
    success_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
    )
    assert "Property created successfully" in success_message.text
    
    # Verify property appears in the list
    property_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "property-list"))
    )
    assert property_data["address"] in property_list.text

def test_property_rental_flow(selenium_driver, test_data):
    """Test the complete flow of renting out a property"""
    driver = selenium_driver
    
    # Login and navigate to properties
    driver.get("http://localhost:3000/login")
    # ... (login steps similar to previous test)
    
    # Find the property in the list
    property_item = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "property-item"))
    )
    property_item.click()
    
    # Click "Rent Out" button
    rent_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "rent-property-btn"))
    )
    rent_btn.click()
    
    # Fill tenant information
    tenant_data = test_data["tenant"]
    
    tenant_name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "tenantName"))
    )
    tenant_name.send_keys(tenant_data["name"])
    
    driver.find_element(By.NAME, "tenantEmail").send_keys(tenant_data["email"])
    driver.find_element(By.NAME, "tenantPhone").send_keys(tenant_data["phone"])
    
    # Set lease dates
    start_date = driver.find_element(By.NAME, "leaseStart")
    end_date = driver.find_element(By.NAME, "leaseEnd")
    
    today = datetime.now().strftime("%Y-%m-%d")
    next_year = str(int(today[:4]) + 1) + today[4:]
    
    start_date.send_keys(today)
    end_date.send_keys(next_year)
    
    # Submit rental form
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()
    
    # Verify success message
    success_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
    )
    assert "Rental agreement created successfully" in success_message.text
    
    # Verify property status changed to "Rented"
    property_status = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "property-status"))
    )
    assert "Rented" in property_status.text

def test_payment_recording_flow(selenium_driver, test_data):
    """Test the complete flow of recording a payment for a property"""
    driver = selenium_driver
    
    # Login and navigate to properties
    driver.get("http://localhost:3000/login")
    # ... (login steps similar to previous test)
    
    # Navigate to payments section
    payments_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "payments-nav"))
    )
    payments_link.click()
    
    # Click "Record Payment" button
    record_payment_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "record-payment-btn"))
    )
    record_payment_btn.click()
    
    # Fill payment information
    property_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "propertyId"))
    )
    property_select.click()
    # Select first property option
    property_option = driver.find_element(By.CSS_SELECTOR, "option:not([value=''])")
    property_option.click()
    
    # Fill payment details
    amount_input = driver.find_element(By.NAME, "amount")
    amount_input.send_keys("1500")
    
    payment_date = driver.find_element(By.NAME, "paymentDate")
    payment_date.send_keys(datetime.now().strftime("%Y-%m-%d"))
    
    payment_type = driver.find_element(By.NAME, "paymentType")
    payment_type.send_keys("Rent")
    
    # Submit payment
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()
    
    # Verify success message
    success_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
    )
    assert "Payment recorded successfully" in success_message.text
    
    # Verify payment appears in payment history
    payment_history = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "payment-history"))
    )
    assert "1500" in payment_history.text
