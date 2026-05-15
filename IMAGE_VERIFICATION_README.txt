BIORoute AI - Google Gemini Image Verification Version

This version is configured to use a Google Gemini API key for real image-based overflow verification.
It does not need OpenAI credits.

What changed:
1. Fake/random image verification has been removed.
2. /api/v1/detections/image calls Google Gemini Vision when GOOGLE_API_KEY is configured.
3. If GOOGLE_API_KEY is missing or invalid, the app returns "Needs manual review" instead of random values.
4. The image verification result includes:
   - overflowDetected
   - wasteVisible
   - estimatedFillLevelPercent
   - severityFromImage
   - confidenceScore
   - verificationStatus
   - detectedWasteType
   - imageReasoning
5. Existing route optimization, hotspot clearance, no-hotspot optimization fix, and repeat-hotspot penalty logic are unchanged.

Setup:
1. Go to backend folder.
2. Copy .env.example and rename the copy to .env.
3. Put your Google Gemini key in backend/.env:

   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_VISION_MODEL=gemini-1.5-flash
   USE_OSRM=true
   OSRM_BASE_URL=https://router.project-osrm.org

Important Google Cloud/API setting:
Your key must be allowed to use Gemini / Generative Language API.
If you restricted the key to Cloud Vision API only, Gemini image verification will fail.
For hackathon testing, use either:
- API restrictions: Generative Language API, or
- API restrictions: None

Run:
   cd backend
   npm install
   npm start

Open:
   http://localhost:3000

Login:
   admin / admin
   user / user

Test:
1. Login as user.
2. Fill a report.
3. Upload/capture a garbage photo.
4. Click Verify Overflow with Camera.
5. Submit report.
6. Login as admin.
7. Open Citizen Reports and verify report.
8. Run optimization and simulation.
