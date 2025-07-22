from _KeithleyReader import KeithleyReader

def quick_test():
    """Quick test of Keithley reader."""
    print("Keithley Quick Test")
    print("=" * 30)

    reader = KeithleyReader(port='COM6')
    reader.start()

    while True:
        data = reader.get_latest_data()