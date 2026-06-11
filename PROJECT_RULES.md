## Production Data Policy

Do not use:

- fake_screenshot_data
- dummy_image
- placeholder frames
- random mock screenshots

Tests must use:

- real PNG data
- real JPG data
- generated valid images
- captured screenshots stored in test assets

Mock transport layers only.

Do not mock image contents.

## Production Asset Rule

All vision tests must use:

- Real PNG images
- Real JPG images
- Real captured screenshots
- Generated valid images

Forbidden:

- fake_screenshot_data
- dummy_image
- placeholder image bytes
- invalid image payloads