#!/usr/bin/env python3
"""
Test script to verify HyperSpeed Optimization is working
"""

import os
import time
import json
from app1 import Roboto

def test_hyperspeed_optimization():
    """Test if HyperSpeed optimization is properly integrated"""
    print("=" * 60)
    print("🚀 TESTING HYPERSPEED OPTIMIZATION MODULE")
    print("=" * 60)
    
    # Create Roboto instance
    print("\n1. Creating Roboto instance...")
    roberto = Roboto()
    
    # Check if hyperspeed optimizer is loaded
    print("\n2. Checking HyperSpeed Optimizer status...")
    if hasattr(roberto, 'hyperspeed_optimizer') and roberto.hyperspeed_optimizer:
        print("✅ HyperSpeed Optimizer is ACTIVE!")
        
        # Get performance stats
        print("\n3. Getting performance statistics...")
        try:
            stats = roberto.get_performance_stats()
            print("\n📊 PERFORMANCE STATISTICS:")
            print(json.dumps(stats, indent=2))
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
        
        # Test response generation
        print("\n4. Testing optimized response generation...")
        test_queries = [
            "Hello, how are you?",
            "What is the meaning of life?",
            "Tell me about Roberto"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            start_time = time.time()
            
            try:
                response = roberto.chat(query)
                elapsed = time.time() - start_time
                
                print(f"   Response time: {elapsed:.3f}s")
                print(f"   Response preview: {response[:100]}...")
                
                # Check cache hit on second call
                start_time = time.time()
                response2 = roberto.chat(query)
                elapsed2 = time.time() - start_time
                
                if elapsed2 < elapsed * 0.5:
                    print(f"   ⚡ Cache hit! Second call: {elapsed2:.3f}s (speedup: {elapsed/elapsed2:.2f}x)")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Check optimizer features
        print("\n5. Checking optimizer features...")
        optimizer = roberto.hyperspeed_optimizer
        
        features = {
            "Memory Cache": hasattr(optimizer, 'memory_cache'),
            "Response Cache": hasattr(optimizer, 'response_cache'),
            "Embedding Cache": hasattr(optimizer, 'embedding_cache'),
            "Predictive Fetcher": hasattr(optimizer, 'predictive_fetcher'),
            "Async Manager": hasattr(optimizer, 'async_manager'),
            "DB Optimizer": hasattr(optimizer, 'db_optimizer'),
            "Performance Monitor": hasattr(optimizer, 'performance_monitor'),
            "Thread Pool": hasattr(optimizer, 'thread_pool'),
            "Process Pool": hasattr(optimizer, 'process_pool')
        }
        
        print("\n📋 OPTIMIZER FEATURES:")
        for feature, available in features.items():
            status = "✅" if available else "❌"
            print(f"   {status} {feature}: {'Available' if available else 'Not Available'}")
        
        # Final performance report
        print("\n6. Final Performance Report...")
        if hasattr(optimizer, 'performance_monitor'):
            report = optimizer.performance_monitor.get_report()
            print("\n📈 PERFORMANCE REPORT:")
            print(json.dumps(report, indent=2))
        
        print("\n" + "=" * 60)
        print("✨ HYPERSPEED OPTIMIZATION TEST COMPLETE!")
        print("=" * 60)
        
    else:
        print("❌ HyperSpeed Optimizer is NOT active")
        print("   Please check if dependencies are installed:")
        print("   - aiohttp")
        print("   - msgpack")
        print("   - numpy")
        print("   - psutil")
        
        # Check which dependencies are missing
        missing = []
        try:
            import aiohttp
        except ImportError:
            missing.append("aiohttp")
        
        try:
            import msgpack
        except ImportError:
            missing.append("msgpack")
        
        try:
            import numpy
        except ImportError:
            missing.append("numpy")
        
        try:
            import psutil
        except ImportError:
            missing.append("psutil")
        
        if missing:
            print(f"\n   Missing dependencies: {', '.join(missing)}")
            print("   Install with: pip install " + " ".join(missing))

if __name__ == "__main__":
    test_hyperspeed_optimization()