import numpy as np
import matplotlib.pyplot as plt
import csv
import os

def plot_signals_from_csv(filename):
    try:
        # Check if the file exists
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File '{filename}' does not exist.")
        
        # Open and read data from the .csv file
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            data = list(csvreader)
        
        # Extract sampling frequency (Fs) and signals from the data
        Fs = float(data[0][1])
        comment = data[1][1]
        
        # Process signals data, converting valid values to float
        signals = []
        for row in data[3:]:
            row_data = []
            for item in row:
                try:
                    row_data.append(float(item))
                except ValueError:
                    pass  # Ignore non-convertible values (like empty strings)
            signals.append(row_data)
        
        signals = np.array(signals).T  # Transpose signals array
    
        time = np.arange(signals.shape[1]) / Fs
    
        # Plot the signals
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ["b", "c"]
        for i, signal in enumerate(signals):
            ax.plot(time, signal, color=colors[i % len(colors)])
    
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Angle (Deg)')
        ax.grid(True, color="#FFE6E6")
        plt.show()
    
    except FileNotFoundError as e:
        raise e  # Rilancia l'eccezione per gestirla in enter_name()

def enter_name():
    while True:
        try:
            # Input the path of the .csv file from the user
            filename = input("Enter the path of the .csv file: ").strip('"')
            if ".csv" not in filename: raise Exception("Not a valid CSV file")
            plot_signals_from_csv(filename)
            break  # Exit loop if plotting succeeds
        
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == '__main__':
    enter_name()
