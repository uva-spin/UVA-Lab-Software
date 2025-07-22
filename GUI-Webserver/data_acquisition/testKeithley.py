from _KeithleyReader import KeithleyReader
import time

def quick_test():
    """Quick test of Keithley reader."""
    print("Keithley Quick Test")
    print("=" * 30)

    reader = KeithleyReader(port='COM6')
    
    if not reader.start():
        print("Failed to start Keithley reader!")
        return
    
    print("Keithley reader started successfully!")
    print("Reading data... (Press Ctrl+C to stop)")
    print("-" * 40)

    try:
        count = 0
        while True:
            data = reader.get_latest_data()
            count += 1
            
            if data is not None:
                print(f"Reading #{count}: {data}")
            else:
                print(f"Reading #{count}: No data available")
            
            time.sleep(1)  # Wait 1 second between readings
            
    except KeyboardInterrupt:
        print("\nStopping test...")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        reader.stop()
        print("Test completed.")

if __name__ == "__main__":
    quick_test()