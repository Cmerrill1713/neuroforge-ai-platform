import re
from playwright.sync_api import Page, expect

def test_chat_interface_functionality(page: Page):
    # Navigate to the frontend application
    page.goto("http://localhost:3000/")

    # 1. Test Text-Only Chat
    # -----------------------
    page.get_by_placeholder("Ask anything...").click()
    page.get_by_placeholder("Ask anything...").fill("Hello, this is a test.")
    page.get_by_role("button", name="Send").click()

    # Verify user message and assistant response appear
    expect(page.get_by_text("Hello, this is a test.")).to_be_visible()
    expect(page.get_by_text("Text response to: Hello, this is a test.")).to_be_visible(timeout=5000)
    print("✅ Text-Only Chat Test Passed")

    # 2. Test Vision (Image Upload) Chat
    # ----------------------------------
    # Use set_input_files to upload the dummy image
    page.set_input_files('input[type="file"]', 'tests/fixtures/test_image.png')
    
    # Check if the attachment preview is visible
    expect(page.get_by_text("test_image.png")).to_be_visible()
    
    # Send a message with the attachment
    page.get_by_placeholder("Ask anything...").click()
    page.get_by_placeholder("Ask anything...").fill("What do you see in this image?")
    page.get_by_role("button", name="Send").click()
    
    # Verify the vision-specific response
    expect(page.get_by_text("Received image 'test_image.png' with your message.")).to_be_visible(timeout=5000)
    print("✅ Vision (Image Upload) Chat Test Passed")

    # 3. Test Voice (Transcription) Input
    # -----------------------------------
    # This part is tricky to test with Playwright as it involves browser permissions for microphone.
    # We will simulate the backend response and check if the UI updates correctly.
    
    # We can't actually record, so we will mock the API call and verify the UI behavior.
    # For this test, we'll just check if clicking the button populates the input field
    # based on the mock response we've set up in the backend.

    # Mock the transcription response
    page.route(
        "**/api/voice/transcribe",
        lambda route: route.fulfill(
            status=200,
            json={"transcription": "This is a mock transcription.", "confidence": 0.95, "duration": 2.5},
        )
    )
    
    mic_button = page.locator('button:has(svg[class*="lucide-mic"])')
    mic_off_button = page.locator('button:has(svg[class*="lucide-mic-off"])')

    # Click to "start recording"
    mic_button.click()
    
    # Click again to "stop recording" and trigger transcription
    # A brief wait may be needed for the state to update if the app has delays
    page.wait_for_timeout(500)
    mic_off_button.click()
    
    # Verify the input field is populated with the mock transcription
    expect(page.get_by_placeholder("Ask anything...")).to_have_value("This is a mock transcription.", timeout=5000)
    print("✅ Voice (Transcription) Input Test Passed")

    # Final check
    print("\n🎉 All functional tests passed!")
