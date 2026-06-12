# Production Test Data & Asset Policy

## Objective

All production code, tests, benchmarks, training pipelines, and validation workflows must use realistic and valid data.

The system must never rely on fake, malformed, placeholder, or non-production-compatible assets.

---

## Allowed Test Assets

### Images

Allowed image sources:

* Real PNG images
* Real JPG/JPEG images
* Real WebP images
* Real screenshots captured from supported devices
* Real screenshots captured from emulators
* Generated valid images created using image libraries (PIL, OpenCV, etc.)
* Curated test datasets stored in `datasets/`
* Golden reference images stored in `tests/assets/`

Examples:

* Android screenshots
* Emulator screenshots
* Game screenshots
* UI screenshots
* OCR validation images

---

### Video

Allowed video sources:

* Real gameplay recordings
* Real screen recordings
* Generated valid video files
* Curated benchmark videos

Examples:

* MP4
* MKV
* AVI
* MOV

---

### Data

Allowed data sources:

* Real configuration files
* Real JSON payloads
* Real YAML files
* Generated valid test datasets
* Sanitized production samples

---

## Forbidden Assets

Never use:

* fake_screenshot_data
* dummy_image
* placeholder_image
* test_image_bytes
* invalid image payloads
* malformed PNG data
* malformed JPG data
* random binary blobs
* hardcoded fake screenshots
* empty image buffers
* corrupted image files

Examples of prohibited patterns:

```python
b"fake_screenshot_data"
b"dummy_image"
b"test_image"
b"placeholder"
```

---

## Mocking Policy

### Allowed

Mock:

* Network transport
* ADB communication
* REST APIs
* Database layers
* External services
* Device connectivity
* File system access
* Time-dependent operations

### Forbidden

Do not mock:

* Image contents
* OCR input images
* Vision processing images
* Frame payloads
* Detection input images
* Template matching images

Instead use valid test assets.

---

## Vision Engine Requirements

All vision-related tests must use:

* Valid image files
* Real screenshots
* Generated valid images

Vision tests must validate:

* Template matching
* OCR
* Object detection
* Image preprocessing
* Feature extraction

using actual image data.

---

## Capture Engine Requirements

Capture tests must validate:

* Real PNG decoding
* Real JPG decoding
* Frame serialization
* Frame conversion
* Image preprocessing

using valid image payloads only.

---

## Dataset Structure

datasets/
├── shadow_fight_3/
├── clash_of_clans/
├── hay_day/
├── generic_ui/
├── ocr/
└── templates/

tests/
└── assets/
├── screenshots/
├── templates/
├── ocr/
└── sample_frames/

---

## Validation Rule

Any test that processes images, screenshots, frames, OCR inputs, videos, or vision assets must use valid production-compatible assets.

Tests that use fake image bytes, placeholder image payloads, or malformed image data must be rejected during code review.
