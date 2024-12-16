import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver

pytestmark = pytest.mark.e2e

class TestPropertyManagement:
    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver: WebDriver, auth_headers: dict):
        self.driver = selenium_driver
        self.wait = WebDriverWait(self.driver, 10)
        # Navigate to the application
        self.driver.get("http://localhost:3000")
        # Add authentication headers
        for name, value in auth_headers.items():
            self.driver.add_cookie({"name": name, "value": value})
        self.driver.refresh()
    
    def test_create_new_property(self, test_property_data: dict):
        # Click on "Add Property" button
        add_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "add-property-button"))
        )
        add_button.click()
        
        # Fill in the form
        self.driver.find_element(By.NAME, "address").send_keys(test_property_data["address"])
        self.driver.find_element(By.NAME, "type").send_keys(test_property_data["type"])
        self.driver.find_element(By.NAME, "rentAmount").send_keys(str(test_property_data["rentAmount"]))
        
        # Submit the form
        submit_button = self.driver.find_element(By.ID, "submit-property")
        submit_button.click()
        
        # Verify the property was created
        success_message = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "Property created successfully" in success_message.text
        
        # Verify property appears in the list
        property_list = self.wait.until(
            EC.presence_of_element_located((By.ID, "property-list"))
        )
        assert test_property_data["address"] in property_list.text
    
    def test_search_property(self, test_property_data: dict):
        # Enter search term
        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "property-search"))
        )
        search_input.send_keys(test_property_data["address"])
        
        # Click search button
        search_button = self.driver.find_element(By.ID, "search-button")
        search_button.click()
        
        # Verify search results
        search_results = self.wait.until(
            EC.presence_of_element_located((By.ID, "search-results"))
        )
        assert test_property_data["address"] in search_results.text
    
    def test_update_property(self, test_property_data: dict):
        # Find and click edit button for the property
        edit_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='edit-property']"))
        )
        edit_button.click()
        
        # Update rent amount
        rent_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "rentAmount"))
        )
        rent_input.clear()
        new_rent = test_property_data["rentAmount"] + 200
        rent_input.send_keys(str(new_rent))
        
        # Save changes
        save_button = self.driver.find_element(By.ID, "save-changes")
        save_button.click()
        
        # Verify update success
        success_message = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        assert "Property updated successfully" in success_message.text
        
        # Verify updated value is displayed
        property_details = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-details"))
        )
        assert f"${new_rent:,}" in property_details.text
