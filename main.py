import logging
from examples import demo

def main():
    """
    Entry point for Postkasse Optimization MVP.
    Runs the example demo.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print("Welcome to Postkasse Optimization MVP")
    print("Running end-to-end demo...")
    demo.run_demo()

if __name__ == "__main__":
    main()
