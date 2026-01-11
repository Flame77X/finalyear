import subprocess
import time

print("🔥 STARTING 7x STRESS TEST VERIFICATION 🔥")
print("==========================================")

passes = 0
failures = 0
total_runs = 7

for i in range(1, total_runs + 1):
    print(f"\n🏃 RUN [{i}/{total_runs}] ... ", end="", flush=True)
    
    try:
        # Run the existing verification script
        result = subprocess.run(
            ["python", "verify_all_files.py"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("✅ PASS")
            passes += 1
        else:
            print("❌ FAIL")
            print(f"   Error Output:\n{result.stdout}\n{result.stderr}")
            failures += 1
            
    except Exception as e:
        print(f"❌ ERROR: Execution failed - {e}")
        failures += 1
    
    time.sleep(1) # Brief pause between runs

print("\n==========================================")
print(f"📊 SUMMARY: {passes}/{total_runs} PASSED")
if failures == 0:
    print("✨ SYSTEM IS STABLE (100% Success Rate) ✨")
else:
    print(f"⚠️ SYSTEM UNSTABLE ({failures} Failures Detected)")
