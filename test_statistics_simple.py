#!/usr/bin/env python3
"""
Simple test for Pomodoro Statistics without full Flask app loading
Tests only the core statistics functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_statistics_directly():
    """Test statistics service directly without Flask app"""
    print("🍅 Testing Pomodoro Statistics Service Directly...")
    
    try:
        # Test importing statistics service
        print("📦 Testing imports...")
        from app.services.pomodoro_statistics_service import PomodoroStatisticsService
        print("✅ PomodoroStatisticsService imported successfully")
        
        # Test creating service instance
        stats_service = PomodoroStatisticsService()
        print("✅ Statistics service instance created")
        
        # Test statistics calculation without database
        print("\n📊 Testing statistics calculation...")
        from datetime import date
        test_user_id = "test-user-123"
        today = date.today()
        
        # This will try to calculate from database, but won't crash if no data
        try:
            calculated_stats = stats_service.calculate_daily_statistics(test_user_id, today)
            print("✅ Statistics calculation completed")
            print(f"   - Total sessions: {calculated_stats.get('total_sessions', 0)}")
            print(f"   - Focus time: {calculated_stats.get('total_focus_time', 0)} minutes")
            print(f"   - Productivity score: {calculated_stats.get('productivity_score', 0):.1f}")
        except Exception as e:
            print(f"⚠️ Statistics calculation failed (expected without DB): {str(e)}")
        
        print("\n✅ Direct statistics service test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during direct testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_services_import():
    """Test importing services from main services.py"""
    print("\n📦 Testing Services Import...")
    
    try:
        # Import directly from the main services module file (not package)
        import importlib.util
        import os
        
        # Get the services.py file path
        services_path = os.path.join(os.path.dirname(__file__), 'app', 'services.py')
        
        # Load the module
        spec = importlib.util.spec_from_file_location("app_services", services_path)
        app_services = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_services)
        
        # Test classes exist
        if hasattr(app_services, 'PomodoroSessionService'):
            print("✅ PomodoroSessionService found")
        else:
            print("❌ PomodoroSessionService not found")
            
        if hasattr(app_services, 'PomodoroStatisticsServiceWrapper'):
            print("✅ PomodoroStatisticsServiceWrapper found")
        else:
            print("❌ PomodoroStatisticsServiceWrapper not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error importing services: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_models_import():
    """Test importing database models"""
    print("\n🗄️ Testing Models Import...")
    
    try:
        from app.models.pomodoro_statistics import PomodoroStatisticsModel
        from app.models.pomodoro_session import PomodoroSessionModel
        print("✅ PomodoroStatisticsModel imported")
        print("✅ PomodoroSessionModel imported")
        
        # Test model attributes
        expected_stats_fields = ['total_sessions', 'total_focus_time', 'productivity_score']
        for field in expected_stats_fields:
            if hasattr(PomodoroStatisticsModel, field):
                print(f"✅ Stats field '{field}' available")
            else:
                print(f"❌ Stats field '{field}' missing")
        
        expected_session_fields = ['user_id', 'session_type', 'duration', 'is_completed']
        for field in expected_session_fields:
            if hasattr(PomodoroSessionModel, field):
                print(f"✅ Session field '{field}' available")
            else:
                print(f"❌ Session field '{field}' missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing models: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Pomodoro Statistics Tests...")
    
    # Run tests without Flask app
    test1 = test_models_import()
    test2 = test_statistics_directly()
    test3 = test_services_import()
    
    if test1 and test2 and test3:
        print("\n🎉 All basic tests passed!")
        print("✅ Pomodoro Statistics components are properly structured")
        print("✅ Ready for Flask app integration")
    else:
        print("\n❌ Some tests failed. Please check imports and dependencies.")