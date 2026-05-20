# -*- coding: utf-8 -*-
import os
import sys
import time
import math
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Target URL default
PORT = os.environ.get("PORT", "5000")
DEFAULT_TARGET = f"http://127.0.0.1:{PORT}"

# Paths to test
PATHS = [
    ("/", "Homepage"),
    ("/healthz", "Liveness Endpt"),
    ("/readyz", "Readiness Endpt"),
    ("/auth/login", "Login Page")
]

def print_banner(target, concurrency, total_requests):
    print("======================================================================")
    print("                     E16 LMS CONCURRENT LOAD TEST                     ")
    print("======================================================================")
    print(f"Target URL:        {target}")
    print(f"Concurrency level: {concurrency}")
    print(f"Total requests:    {total_requests}")
    print("======================================================================")

def execute_request(target_url, path, name):
    url = f"{target_url}{path}"
    start_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=5)
        latency = (time.perf_counter() - start_time) * 1000  # in ms
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "latency": latency,
            "name": name,
            "error": None
        }
    except Exception as e:
        latency = (time.perf_counter() - start_time) * 1000
        return {
            "success": False,
            "status_code": 0,
            "latency": latency,
            "name": name,
            "error": str(e)
        }

def calculate_percentiles(latencies):
    if not latencies:
        return 0, 0, 0, 0
    sorted_lats = sorted(latencies)
    n = len(sorted_lats)
    
    def get_percentile(p):
        k = (n - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_lats[int(k)]
        return sorted_lats[f] * (c - k) + sorted_lats[c] * (k - f)

    return get_percentile(50), get_percentile(90), get_percentile(95), get_percentile(99)

def run_load_test(target, concurrency, total_requests):
    print_banner(target, concurrency, total_requests)
    
    # Test connection first
    try:
        requests.get(f"{target}/healthz", timeout=2)
    except Exception:
        print(f"\n[ERROR] Target server is not running or unreachable at {target}.")
        print("Please start the E16 server first using: flask run or python app.py")
        return 1

    results = []
    print("\nSimulating concurrent traffic...")
    
    start_test_time = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(total_requests):
            # Rotate paths for even load
            path, name = PATHS[i % len(PATHS)]
            futures.append(executor.submit(execute_request, target, path, name))
            
        for future in as_completed(futures):
            results.append(future.result())
            if len(results) % 50 == 0:
                print(f"Completed {len(results)}/{total_requests} requests...")

    total_test_duration = (time.perf_counter() - start_test_time)

    # Compile stats
    successful = [r for r in results if r["success"] or r["status_code"] in [401, 403, 429]]
    failed = [r for r in results if not r["success"] and r["status_code"] not in [401, 403, 429]]
    latencies = [r["latency"] for r in results]
    
    # Status code breakdown
    status_codes = {}
    for r in results:
        code = r["status_code"]
        status_codes[code] = status_codes.get(code, 0) + 1
        
    p50, p90, p95, p99 = calculate_percentiles(latencies)
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    qps = len(results) / total_test_duration if total_test_duration > 0 else 0

    print("\n" + "="*70)
    print("                           LOAD TEST RESULTS                          ")
    print("="*70)
    print(f"Total Requests executed:  {len(results)}")
    print(f"Server-handled Requests:  {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Server-failed Requests:   {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print(f"HTTP Status Codes breakdown:")
    for code, count in sorted(status_codes.items()):
        status_name = "ERROR/EXCEPT" if code == 0 else f"HTTP {code}"
        print(f"  {status_name:<15}: {count} ({count/len(results)*100:.1f}%)")
    print(f"Total duration:           {total_test_duration:.2f} seconds")
    print(f"Queries Per Second (QPS): {qps:.2f}")
    print("-"*70)
    print("Latency Distribution (Response Times):")
    print(f"  Average:                {avg_latency:.2f} ms")
    print(f"  P50 (Median):           {p50:.2f} ms")
    print(f"  P90:                    {p90:.2f} ms")
    print(f"  P95 (BRD Target):       {p95:.2f} ms")
    print(f"  P99:                    {p99:.2f} ms")
    print("="*70)

    # Check BRD validation
    brd_target_ms = 800
    if p95 <= brd_target_ms:
        print(f"\nVALIDATION PASSED: P95 latency ({p95:.2f}ms) is well under the 800ms BRD baseline! [OK]")
    else:
        print(f"\nVALIDATION WARNING: P95 latency ({p95:.2f}ms) exceeded the 800ms BRD target. [WARN]")

    # Group by endpoint
    print("\nBreakdown by Endpoint:")
    for path, name in PATHS:
        endpoint_res = [r for r in results if r["name"] == name]
        if not endpoint_res:
            continue
        e_success = len([r for r in endpoint_res if r["success"] or r["status_code"] in [401, 403, 429]])
        e_latencies = [r["latency"] for r in endpoint_res]
        e_avg = sum(e_latencies) / len(e_latencies)
        _, _, e_p95, _ = calculate_percentiles(e_latencies)
        print(f"  {name:<15}: Count={len(endpoint_res):<4} Success={e_success/len(endpoint_res)*100:>5.1f}% Avg={e_avg:>6.1f}ms P95={e_p95:>6.1f}ms")
        
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concurrent Load Testing Script for E16 LMS")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Target root URL of the running LMS")
    parser.add_argument("--concurrency", type=int, default=50, help="Number of concurrent workers")
    parser.add_argument("--requests", type=int, default=300, help="Total number of requests to issue")
    args = parser.parse_args()
    
    sys.exit(run_load_test(args.target, args.concurrency, args.requests))
