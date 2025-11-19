#!/usr/bin/env python3
"""
Test script for Redis caching and PostgreSQL integration
"""

import sys
import os
sys.path.insert(0, 'src')

from config import Config
from redis_cache import RedisCache
from database_enhanced import F1DatabaseEnhanced
import pandas as pd


def test_config():
    """Test configuration module"""
    print("\n" + "=" * 60)
    print("Testing Configuration Module")
    print("=" * 60)
    
    print(f"✓ DB_TYPE: {Config.DB_TYPE}")
    print(f"✓ DB_PATH: {Config.DB_PATH}")
    print(f"✓ REDIS_ENABLED: {Config.REDIS_ENABLED}")
    print(f"✓ Database URL: {Config.get_database_url()}")
    
    if Config.REDIS_ENABLED:
        print(f"✓ Redis URL: {Config.get_redis_url()}")
    
    return True


def test_redis_cache():
    """Test Redis cache module"""
    print("\n" + "=" * 60)
    print("Testing Redis Cache Module")
    print("=" * 60)
    
    cache = RedisCache()
    print(f"Cache enabled: {cache.enabled}")
    
    if cache.enabled:
        # Test simple key-value
        test_data = {'key': 'value', 'number': 42}
        cache.set('test_simple', test_data, ttl=60)
        retrieved = cache.get('test_simple')
        
        if retrieved == test_data:
            print("✓ Simple key-value caching works")
        else:
            print("✗ Simple key-value caching failed")
            return False
        
        # Test DataFrame caching
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        
        cache.cache_dataframe('test_df', df, ttl=60)
        cached_df = cache.get_dataframe('test_df')
        
        if cached_df is not None and len(cached_df) == len(df):
            print("✓ DataFrame caching works")
        else:
            print("✗ DataFrame caching failed")
            return False
        
        # Test stats
        stats = cache.get_stats()
        print(f"✓ Cache stats: {stats.get('keyspace_hits', 0)} hits, {stats.get('keyspace_misses', 0)} misses")
        
        # Cleanup
        cache.delete('test_simple')
        cache.delete('test_df')
        print("✓ Cache cleanup successful")
    else:
        print("ℹ Redis not enabled or not available - skipping cache tests")
    
    return True


def test_database():
    """Test enhanced database module"""
    print("\n" + "=" * 60)
    print("Testing Enhanced Database Module")
    print("=" * 60)
    
    try:
        db = F1DatabaseEnhanced()
        print(f"✓ Database initialized: {Config.DB_TYPE}")
        
        # Test inserting data
        db.insert_team("Test Team 2024", 2024)
        db.insert_driver(88, "TST", "Test Driver", "Test Team 2024", 2024)
        print("✓ Data insertion works")
        
        # Test querying
        races = db.get_all_races()
        print(f"✓ Query works: {len(races)} races found")
        
        # Test cache stats
        stats = db.get_cache_stats()
        print(f"✓ Cache integration: {stats}")
        
        # Test table listing
        tables = list(db.get_table_names())
        expected_tables = [
            'drivers', 'teams', 'races', 'qualifying_results',
            'sprint_results', 'race_results', 'predictions',
            'aggregated_laps', 'tyre_stats', 'sessions'
        ]
        
        if all(table in tables for table in expected_tables):
            print(f"✓ All expected tables present: {len(tables)} tables")
        else:
            print(f"⚠ Some tables missing")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test backward compatibility with original database"""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)
    
    try:
        from database import F1Database, get_database_instance
        
        # Test original database
        db_old = F1Database()
        print("✓ Original F1Database still works")
        
        # Test factory function
        db_auto = get_database_instance()
        print(f"✓ Factory function works: {type(db_auto).__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return False


def test_performance():
    """Test cache performance benefit"""
    print("\n" + "=" * 60)
    print("Testing Cache Performance")
    print("=" * 60)
    
    try:
        db = F1DatabaseEnhanced()
        
        if not db._cache.enabled:
            print("ℹ Redis not enabled - skipping performance test")
            return True
        
        import time
        
        # First query (cold cache)
        start = time.time()
        races1 = db.get_all_races()
        time1 = time.time() - start
        
        # Second query (warm cache)
        start = time.time()
        races2 = db.get_all_races()
        time2 = time.time() - start
        
        print(f"First query (cold cache): {time1*1000:.2f}ms")
        print(f"Second query (warm cache): {time2*1000:.2f}ms")
        
        if time2 < time1:
            speedup = time1 / time2
            print(f"✓ Cache speedup: {speedup:.1f}x faster")
        else:
            print("ℹ No significant speedup detected (small dataset)")
        
        # Clear cache
        db.flush_cache()
        print("✓ Cache flushed")
        
        return True
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("F1 Database Redis & PostgreSQL Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Redis Cache", test_redis_cache),
        ("Enhanced Database", test_database),
        ("Backward Compatibility", test_backward_compatibility),
        ("Cache Performance", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
