from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time

def renew(username, password):
    try:
        with sync_playwright() as p:
            # Launch browser with necessary arguments
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--remote-debugging-port=9222',
                    '--disable-gpu',
                    '--window-size=1920,1200',
                    '--ignore-certificate-errors',
                    '--disable-extensions'
                ]
            )
            
            page = browser.new_page()

            # Navigate to login page
            page.goto('https://licenseportal.it.chula.ac.th/')

            # Fill in login credentials
            page.fill('#UserName', username)
            page.fill('#Password', password)

            # Click the login button
            page.click('button')

            # After clicking login, some accounts redirect through Microsoft login.
            # Wait for either the Borrow page or a Microsoft login page and handle both.
            try:
                # short wait for direct redirect to Borrow
                page.wait_for_url("**/Home/Borrow", timeout=5000)
            except:
                # If MS login appears, handle it
                if ("login.microsoftonline.com" in page.url
                        or page.query_selector("input[name='loginfmt']")
                        or page.query_selector("input[type='email']")):
                    # Enter email/username
                    try:
                        if page.query_selector("input[name='loginfmt']"):
                            page.fill("input[name='loginfmt']", username)
                        elif page.query_selector("input[type='email']"):
                            page.fill("input[type='email']", username)
                        # click next/submit
                        if page.query_selector("#idSIButton9"):
                            page.click("#idSIButton9")
                        else:
                            # fallback to submit buttons
                            page.click("input[type='submit'], button[type='submit']")
                    except Exception:
                        pass

                    # Wait for password field
                    try:
                        page.wait_for_selector("input[name='passwd'], input[type='password']", timeout=7000)
                        if page.query_selector("input[name='passwd']"):
                            page.fill("input[name='passwd']", password)
                        else:
                            page.fill("input[type='password']", password)
                        # submit password
                        if page.query_selector("#idSIButton9"):
                            page.click("#idSIButton9")
                        else:
                            page.click("input[type='submit'], button[type='submit']")
                    except Exception:
                        pass

                    # Handle "Stay signed in?" prompt if it appears
                    try:
                        page.wait_for_selector("#idBtn_Back, #idBtn_Accept, button:text('Yes'), button:text('No')", timeout=5000)
                        if page.query_selector("#idBtn_Back"):
                            page.click("#idBtn_Back")  # usually "No"
                        elif page.query_selector("button:text('No')"):
                            page.click("button:text('No')")
                        elif page.query_selector("#idBtn_Accept"):
                            page.click("#idBtn_Accept")
                    except Exception:
                        pass

                    # Wait for redirect back to the license portal (give it some time)
                    try:
                        page.wait_for_url("**licenseportal.it.chula.ac.th**", timeout=15000)
                    except Exception:
                        pass

            # Ensure we are on the Borrow page (navigate if needed)
            if not page.url.endswith('/Home/Borrow'):
                page.goto('https://licenseportal.it.chula.ac.th/Home/Borrow')

            # Wait for expiry date field to load
            page.wait_for_selector('#ExpiryDateStr')

            # Set the expiry date to 7 days from today
            week = datetime.now() + timedelta(days=7)
            page.fill('#ExpiryDateStr', week.strftime('%d/%m/%Y'))

            # Remove any unnecessary datepicker elements ('.dtp') which may block the Save button
            time.sleep(0.5)
            for dtp in page.query_selector_all('.dtp'):
                page.evaluate('(element) => element.remove()', dtp)

            # Select value for 'ProgramLicenseID' dropdown
            page.select_option('#ProgramLicenseID', value='5')

            # Wait for the Save button and click it
            page.wait_for_selector("button:text('Save')")
            page.click("button:text('Save')")
            time.sleep(1)
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

        



import os
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

if renew(USERNAME, PASSWORD):
    print("Renewal process completed successfully.")
else:
    print("Renewal process failed.")
