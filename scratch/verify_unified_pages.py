import requests

API_BASE = "http://localhost:8000"
PAGES_TO_TEST = ["/", "/search", "/submit-claim", "/registry-portal", "/chatbot"]

print("🔍 Testing Unified Serviced Pages...")
all_passed = True

for page in PAGES_TO_TEST:
    url = f"{API_BASE}{page}"
    try:
        res = requests.get(url)
        print(f"\nTesting page: {page} ({url})")
        print(f"Status Code: {res.status_code}")

        has_root_div = '<div id="root"></div>' in res.text
        has_js_bundle = "/assets/index-" in res.text

        if res.status_code == 200 and has_root_div:
            print("✅ Status 200 & React Mount Element Detected!")
            if has_js_bundle:
                print("✅ High-Fidelity JS production bundle path verified!")
        else:
            print(
                "❌ Verification Failed: SPA routing failed or not serving index.html."
            )
            all_passed = False
    except Exception as e:
        print(f"❌ Failed to reach service: {e}")
        all_passed = False

if all_passed:
    print("\n🎉 ALL UNIFIED ROUTE TESTS PASSED!")
else:
    print("\n⚠️ SOME TESTS ENCOUNTERED ERRORS.")
