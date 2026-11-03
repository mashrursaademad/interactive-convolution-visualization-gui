import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import threading
import time
import tkinter.font as tkfont

class ConvolutionVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Convolution Visualization GUI")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        # Variables
        self.mode = tk.StringVar(value="discrete")
        self.animation_speed = tk.DoubleVar(value=100)
        self.is_animating = False
        self.animation_thread = None
        
        # Signal data
        self.input_signal = []
        self.impulse_response = []
        self.output_signal = []
        self.time_axis = []
        self.current_shift = 0
        self.conv_time_axis = None 
        
        self.setup_gui()
        
    def setup_gui(self):
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=12)

        bold_large_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        bold_large_font2 = tkfont.Font(family="Helvetica", size=15, weight="bold")
        self.bold_large_font = bold_large_font
        self.bold_large_font2 = bold_large_font2

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        style = ttk.Style()
        style.theme_use('clam')  # Use a theme that allows customization

        # Dark BG & Fonts
        style.configure("DarkLabelFrame.TLabelframe", background="black", foreground="white")
        style.configure("DarkLabelFrame.TLabelframe.Label", background="black", foreground="white")
        style.configure("TFrame", background="black")
        style.configure("TLabelFrame", background="black", foreground="white")
        style.configure("TLabel", background="black", foreground="white")
        style.configure("TRadiobutton", background="black", foreground="white")
        style.configure("TButton", background="black", foreground="white")
        style.configure("TEntry", fieldbackground="gray20", foreground="white")
        style.configure("TScale", background="black")
        style.configure("TCombobox", fieldbackground="gray20", background="black", foreground="white")
        style.configure("DarkBoldLarge.TLabelframe", background="black", foreground="white")
        style.configure("DarkBoldLarge.TLabelframe.Label", font=self.bold_large_font, background="black", foreground="white")
        style.configure("DarkBoldLarge.TButton", background="black", foreground="white", font=self.bold_large_font2)
        
        # Left panel for controls
        control_frame = ttk.Frame(main_frame, width=500)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        control_frame.pack_propagate(False)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(control_frame, text="Select Signal Domain", style="DarkBoldLarge.TLabelframe")
        mode_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Radiobutton(mode_frame, text="Discrete-Time (DT)", variable=self.mode, value="discrete", command=self.on_mode_change, style="Dark.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Continuous-Time (CT)", variable=self.mode, value="continuous", command=self.on_mode_change, style="Dark.TRadiobutton").pack(side=tk.LEFT, padx=60)
        
        # Input signal frame
        self.input_frame = ttk.LabelFrame(control_frame, text="Input Signal Specifications", style="DarkBoldLarge.TLabelframe")
        self.input_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Impulse response frame
        self.impulse_frame = ttk.LabelFrame(control_frame, text="Impulse Response Specifications", style="DarkBoldLarge.TLabelframe")
        self.impulse_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Animation controls
        anim_frame = ttk.LabelFrame(control_frame, text="Animation Controls", style="DarkBoldLarge.TLabelframe")
        anim_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(anim_frame, text="Speed:", style="Dark.TLabel").pack(anchor=tk.W)
        speed_scale = tk.Scale(anim_frame, from_=200, to=1, variable=self.animation_speed, orient=tk.HORIZONTAL,bg='black', fg='white', troughcolor='gray20', highlightbackground='black')
        speed_scale.pack(fill=tk.X)

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        compute_frame = ttk.Frame(button_frame)
        compute_frame.pack(fill=tk.X)

        ttk.Button(compute_frame, text="Compute Convolution", command=self.compute_convolution, style="DarkBoldLarge.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(compute_frame, text="Compute Correlation", command=self.compute_correlation, style="DarkBoldLarge.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X)

        ttk.Button(button_frame, text="Reset", command=self.reset_all, width=25, style="DarkBoldLarge.TButton").pack(fill=tk.X)
        
        # Plot frame
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 6))
        self.fig.subplots_adjust(hspace=0.5)

        # Set background colors to black
        self.fig.patch.set_facecolor('black')
        for ax in (self.ax1, self.ax2, self.ax3):
            ax.set_facecolor('black')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.grid(color='gray')

        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize GUI elements
        self.on_mode_change()
        
    def on_mode_change(self):
        # Clear existing widgets
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        for widget in self.impulse_frame.winfo_children():
            widget.destroy()
            
        if self.mode.get() == "discrete":
            self.setup_discrete_inputs()
        else:
            self.setup_continuous_inputs()
    
    def setup_discrete_inputs(self):
        # Input signal
        ttk.Label(self.input_frame, text="Input Vector:").pack(anchor=tk.W)
        self.input_vector = tk.StringVar(value="[ ]")
        ttk.Entry(self.input_frame, textvariable=self.input_vector, width=30).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.input_frame, text="Start Index:").pack(anchor=tk.W)
        self.input_start = tk.StringVar(value="0")
        ttk.Entry(self.input_frame, textvariable=self.input_start, width=30).pack(fill=tk.X)
        
        # Impulse response
        ttk.Label(self.impulse_frame, text="Impulse Vector:").pack(anchor=tk.W)
        self.impulse_vector = tk.StringVar(value="[ ]")
        ttk.Entry(self.impulse_frame, textvariable=self.impulse_vector, width=30).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.impulse_frame, text="Start Index:").pack(anchor=tk.W)
        self.impulse_start = tk.StringVar(value="0")
        ttk.Entry(self.impulse_frame, textvariable=self.impulse_start, width=30).pack(fill=tk.X)
    
    def setup_continuous_inputs(self):
        # Input signal
        ttk.Label(self.input_frame, text="Signal Type:").pack(anchor=tk.W)
        self.input_type = tk.StringVar(value="Select One")
        input_combo = ttk.Combobox(self.input_frame, textvariable=self.input_type, width=27)
        input_combo['values'] = ("Impulse", "Step", "Triangular", "Rectangular", "Sawtooth")
        input_combo.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.input_frame, text="Start Time:").pack(anchor=tk.W)
        self.input_start_time = tk.StringVar(value="0")
        ttk.Entry(self.input_frame, textvariable=self.input_start_time, width=30).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.input_frame, text="End Time:").pack(anchor=tk.W)
        self.input_end_time = tk.StringVar(value="1")
        ttk.Entry(self.input_frame, textvariable=self.input_end_time, width=30).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.input_frame, text="Amplitude:").pack(anchor=tk.W)
        self.input_amplitude = tk.StringVar(value="1")
        ttk.Entry(self.input_frame, textvariable=self.input_amplitude, width=30).pack(fill=tk.X)
        
        # Impulse response
        ttk.Label(self.impulse_frame, text="Signal Type:").pack(anchor=tk.W)
        self.impulse_type = tk.StringVar(value="Select One")
        impulse_combo = ttk.Combobox(self.impulse_frame, textvariable=self.impulse_type, width=27)
        impulse_combo['values'] = ("Impulse", "Step", "Triangular", "Rectangular", "Sawtooth")
        impulse_combo.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.impulse_frame, text="Start Time:").pack(anchor=tk.W)
        self.impulse_start_time = tk.StringVar(value="0")
        ttk.Entry(self.impulse_frame, textvariable=self.impulse_start_time, width=30).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.impulse_frame, text="End Time:").pack(anchor=tk.W)
        self.impulse_end_time = tk.StringVar(value="1")
        ttk.Entry(self.impulse_frame, textvariable=self.impulse_end_time, width=30).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.impulse_frame, text="Amplitude:").pack(anchor=tk.W)
        self.impulse_amplitude = tk.StringVar(value="1")
        ttk.Entry(self.impulse_frame, textvariable=self.impulse_amplitude, width=30).pack(fill=tk.X)
    
    def validate_discrete_inputs(self):
        try:
            # Parse input vector
            input_vec = eval(self.input_vector.get())
            input_start = int(self.input_start.get())
            
            # Parse impulse vector
            impulse_vec = eval(self.impulse_vector.get())
            impulse_start = int(self.impulse_start.get())
            
            if not isinstance(input_vec, list) or not isinstance(impulse_vec, list):
                raise ValueError("Vectors must be lists")
                
            return input_vec, input_start, impulse_vec, impulse_start
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return None
    
    def validate_continuous_inputs(self):
        try:
            # Input signal parameters
            input_start = float(self.input_start_time.get())
            input_end = float(self.input_end_time.get())
            input_amp = float(self.input_amplitude.get())
            
            # Impulse response parameters
            impulse_start = float(self.impulse_start_time.get())
            impulse_end = float(self.impulse_end_time.get())
            impulse_amp = float(self.impulse_amplitude.get())
            
            if input_start >= input_end or impulse_start >= impulse_end:
                raise ValueError("End time must be greater than start time")
                
            return (input_start, input_end, input_amp, impulse_start, impulse_end, impulse_amp)
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return None
    
    def generate_continuous_signal(self, signal_type, start_time, end_time, amplitude, t):
        signal = np.zeros_like(t)
        mask = (t >= start_time) & (t <= end_time)
        
        if signal_type == "Impulse":
            # Approximate impulse as very narrow pulse
            impulse_width = (end_time - start_time) * 0.1
            impulse_mask = (t >= start_time) & (t <= start_time + impulse_width)
            signal[impulse_mask] = amplitude / impulse_width
        elif signal_type == "Step":
            signal[mask] = amplitude
        elif signal_type == "Rectangular":
            signal[mask] = amplitude
        elif signal_type == "Triangular":
            t_masked = t[mask]
            mid_point = (start_time + end_time) / 2
            signal[mask] = amplitude * (1 - 2 * np.abs(t_masked - mid_point) / (end_time - start_time))
        elif signal_type == "Sawtooth":
            t_masked = t[mask]
            signal[mask] = amplitude * 2 * (t_masked - start_time) / (end_time - start_time) - amplitude
            
        return signal
    
    def compute_convolution(self):
        if self.is_animating:
            return
            
        if self.mode.get() == "discrete":
            result = self.validate_discrete_inputs()
            if result is None:
                return
            input_vec, input_start, impulse_vec, impulse_start = result
            self.compute_discrete_convolution(input_vec, input_start, impulse_vec, impulse_start)
        else:
            result = self.validate_continuous_inputs()
            if result is None:
                return
            input_start, input_end, input_amp, impulse_start, impulse_end, impulse_amp = result
            self.compute_continuous_convolution(input_start, input_end, input_amp, impulse_start, impulse_end, impulse_amp)
    
    def compute_discrete_convolution(self, input_vec, input_start, impulse_vec, impulse_start):
        # Prepare data for animation
        self.input_signal = np.array(input_vec)
        self.impulse_response = np.array(impulse_vec)
        
        # Create time indices
        input_indices = np.arange(input_start, input_start + len(input_vec))
        impulse_indices = np.arange(impulse_start, impulse_start + len(impulse_vec))
        
        # Compute full convolution
        conv_result = np.convolve(self.input_signal, self.impulse_response, mode='full')
        conv_start = input_start + impulse_start
        conv_indices = np.arange(conv_start, conv_start + len(conv_result))
        
        # Set up animation parameters
        self.time_axis = np.arange(min(input_indices[0], impulse_indices[0]) - 2, max(conv_indices[-1], input_indices[-1]) + 2)
        self.output_signal = conv_result
        self.conv_indices = conv_indices
        self.input_indices = input_indices
        self.impulse_indices = impulse_indices
        
        # Start animation
        self.animate_discrete_convolution()
    
    def compute_continuous_convolution(self, input_start, input_end, input_amp, impulse_start, impulse_end, impulse_amp):
        # Create time axis
        total_start = - impulse_end - 1
        total_end = input_end + impulse_end + 1
        dt = 0.01
        self.time_axis = np.arange(total_start, total_end, dt)
        
        # Generate signals
        self.input_signal = self.generate_continuous_signal(self.input_type.get(), input_start, input_end, input_amp, self.time_axis)
        self.impulse_response = self.generate_continuous_signal(self.impulse_type.get(), impulse_start, impulse_end, impulse_amp, self.time_axis)
        
        # Compute convolution (numerical approximation)
        self.output_signal = np.zeros_like(self.time_axis)

        for i, t in enumerate(self.time_axis):
            shifted_h = np.zeros_like(self.time_axis)
            for j, tau in enumerate(self.time_axis):
                shifted_time = t - tau
                if self.time_axis[0] <= shifted_time <= self.time_axis[-1]:
                    idx = int((shifted_time - self.time_axis[0]) / (self.time_axis[1] - self.time_axis[0]))
                    if 0 <= idx < len(self.impulse_response):
                        shifted_h[j] = self.impulse_response[idx]
    
            product = self.input_signal * shifted_h
            self.output_signal[i] = np.trapz(product, self.time_axis)

        # Start animation
        self.animate_continuous_convolution()
    
    def animate_discrete_convolution(self):
        if self.is_animating:
            return
            
        self.is_animating = True
        
        def animation_worker():
            max_shift = len(self.time_axis) + len(self.impulse_response)
            
            for shift in range(max_shift):
                if not self.is_animating:
                    break
                    
                # Clear plots
                self.ax1.clear()
                self.ax2.clear()
                self.ax3.clear()
                
                # Plot input signal
                self.ax1.stem(self.input_indices, self.input_signal, basefmt=" ")
                self.ax1.set_title("Input Signal x[n]")
                self.ax1.grid(True)
                
                # Plot shifted and flipped impulse response
                shifted_impulse_indices = self.impulse_indices[::-1] + shift + self.time_axis[0]
                if len(shifted_impulse_indices) > 0:
                    self.ax2.stem(shifted_impulse_indices, self.impulse_response[::-1], basefmt=" ")
                    self.ax2.set_title("Shifted Impulse Response h[n-k]")
                    self.ax2.grid(True)
                
                # Plot convolution result up to current point
                if shift < len(self.conv_indices):
                    self.ax3.stem(self.conv_indices[:shift+1], self.output_signal[:shift+1], basefmt=" ")
                else:
                    self.ax3.stem(self.conv_indices, self.output_signal, basefmt=" ")
                    self.ax3.set_title("Convolution Output y[n]")
                    self.ax3.grid(True)
                
                # Update canvas
                self.canvas.draw()
                time.sleep(self.animation_speed.get() / 500)
            
            self.is_animating = False
        
        self.animation_thread = threading.Thread(target=animation_worker)
        self.animation_thread.start()
    
    def animate_continuous_convolution(self):
        if self.is_animating:
            return
            
        self.is_animating = True
        
        def animation_worker():
            # Get signal parameters from the GUI
            input_start = float(self.input_start_time.get())
            input_end = float(self.input_end_time.get())
            impulse_start = float(self.impulse_start_time.get())
            impulse_end = float(self.impulse_end_time.get())
            
            # Calculate when signals start and stop overlapping
            # For convolution y(t) = ∫ x(τ) * h(t-τ) dτ
            # Overlap starts when: t >= input_start + impulse_start
            # Overlap ends when: t <= input_end + impulse_end
            overlap_start = input_start + impulse_start
            overlap_end = input_end + impulse_end
            
            # Create animation time range with some padding
            anim_start = overlap_start - 1
            anim_end = overlap_end + 1
            
            # Create tau values for animation
            dt = self.time_axis[1] - self.time_axis[0]
            tau_values = np.arange(anim_start, anim_end, dt * 5)  # Every 5th point for smoother animation
            
            for tau in tau_values:
                if not self.is_animating:
                    break
                    
                # Clear plots
                self.ax1.clear()
                self.ax2.clear()
                self.ax3.clear()
                
                # Plot input signal
                self.ax1.plot(self.time_axis, self.input_signal, 'b-', linewidth=2)
                self.ax1.set_title("Input Signal x(t)")
                self.ax1.grid(True)
                self.ax1.set_xlabel("Time (s)")
                self.ax1.set_ylabel("Amplitude")
                
                # Create shifted and flipped impulse response h(tau-t)
                shifted_impulse = np.zeros_like(self.time_axis)
                
                # For each point in time axis, calculate h(tau-t)
                for i, t in enumerate(self.time_axis):
                    shifted_time = tau - t  # This is the argument for h(tau-t)
                    
                    # Find the corresponding index in the original impulse response
                    if self.time_axis[0] <= shifted_time <= self.time_axis[-1]:
                        shifted_idx = int((shifted_time - self.time_axis[0]) / dt)
                        if 0 <= shifted_idx < len(self.impulse_response):
                            shifted_impulse[i] = self.impulse_response[shifted_idx]
                
                # Plot shifted impulse response
                self.ax2.plot(self.time_axis, shifted_impulse, 'r-', linewidth=2)
                self.ax2.axvline(x=tau, color='g', linestyle='--', alpha=0.7, label=f'τ={tau:.2f}')
                self.ax2.set_title(f"Shifted & Flipped Impulse Response h(τ-t)")
                self.ax2.grid(True)
                self.ax2.legend()
                self.ax2.set_xlabel("Time (s)")
                self.ax2.set_ylabel("Amplitude")
                
                # Calculate convolution value at current tau
                product = self.input_signal * shifted_impulse
                convolution_value = np.trapz(product, self.time_axis)
                
                # Plot convolution result up to current point
                current_idx = np.searchsorted(self.time_axis, tau)
                if current_idx > 0:
                    self.ax3.plot(self.time_axis[:current_idx], self.output_signal[:current_idx], 'g-', linewidth=2)
                    
                # Mark current point
                if 0 <= current_idx < len(self.output_signal):
                    self.ax3.plot(tau, self.output_signal[current_idx], 'ro', markersize=6)
                    
                self.ax3.set_title("Convolution Output y(t)")
                self.ax3.grid(True)
                self.ax3.set_xlabel("Time (s)")
                self.ax3.set_ylabel("Amplitude")
                
                # Add overlap indication
                if overlap_start <= tau <= overlap_end:
                    self.ax1.axvspan(max(input_start, tau - (impulse_end - impulse_start)), 
                                   min(input_end, tau), alpha=0.3, color='yellow', label='Overlap')
                    self.ax2.axvspan(max(self.time_axis[0], tau - input_end), 
                                   min(self.time_axis[-1], tau - input_start), alpha=0.3, color='yellow')
                    self.ax1.legend()
                
                # Update canvas
                self.fig.tight_layout()
                self.canvas.draw()
                time.sleep(self.animation_speed.get() / 500)
            
            self.is_animating = False
        
        self.animation_thread = threading.Thread(target=animation_worker)
        self.animation_thread.start()
    
    def compute_correlation(self):
        """Modified to always animate correlation computation"""
        if self.is_animating:
            messagebox.showwarning("Warning", "Please wait for current animation to finish")
            return
            
        if self.mode.get() == "discrete":
            result = self.validate_discrete_inputs()
            if result is None:
                return
            input_vec, input_start, impulse_vec, impulse_start = result
            self.animate_discrete_correlation(input_vec, input_start, impulse_vec, impulse_start)
        else:
            result = self.validate_continuous_inputs()
            if result is None:
                return
            input_start, input_end, input_amp, impulse_start, impulse_end, impulse_amp = result
            self.animate_continuous_correlation(input_start, input_end, input_amp, impulse_start, impulse_end, impulse_amp)
    
    def animate_discrete_correlation(self, input_vec, input_start, impulse_vec, impulse_start):
        """Animate discrete correlation process"""
        self.is_animating = True
        
        def animation_worker():
            # Convert to numpy arrays
            signal1 = np.array(input_vec)
            signal2 = np.array(impulse_vec)
            
            # Create indices
            signal1_indices = np.arange(input_start, input_start + len(signal1))
            signal2_indices = np.arange(impulse_start, impulse_start + len(signal2))
            
            # Compute correlation for reference
            correlation = np.correlate(signal1, signal2, mode='full')
            
            # Create shift range for animation
            max_shift = len(signal1) + len(signal2) - 1
            correlation_result = []
            
            for shift in range(max_shift):
                if not self.is_animating:
                    break
                    
                # Clear plots
                self.ax1.clear()
                self.ax2.clear()
                self.ax3.clear()
                
                # Plot first signal
                self.ax1.stem(signal1_indices, signal1, basefmt=" ")
                self.ax1.set_title("Signal 1: x[n]")
                self.ax1.grid(True)
                
                # Plot shifted second signal (no flipping for correlation)
                lag = shift - len(signal2) + 1
                shifted_indices = signal2_indices + lag
                self.ax2.stem(shifted_indices, signal2, basefmt=" ")
                self.ax2.set_title(f"Shifted Signal 2: y[n-{lag}]")
                self.ax2.grid(True)
                
                # Calculate correlation value at current shift
                correlation_value = correlation[shift]
                correlation_result.append(correlation_value)
                
                # Plot correlation result up to current point
                lag_axis = np.arange(len(correlation_result)) - len(signal2) + 1
                self.ax3.stem(lag_axis, correlation_result, basefmt=" ")
                self.ax3.plot(lag, correlation_value, 'ro', markersize=8)
                self.ax3.set_title("Cross-Correlation R_xy[lag]")
                self.ax3.grid(True)
                
                # Update canvas
                self.fig.tight_layout()
                self.canvas.draw()
                time.sleep(self.animation_speed.get() / 500)
            
            self.is_animating = False
        
        self.animation_thread = threading.Thread(target=animation_worker)
        self.animation_thread.start()
    
    def animate_continuous_correlation(self, input_start, input_end, input_amp, impulse_start, impulse_end, impulse_amp):
        """Animate continuous correlation process with proper signal timing"""
        self.is_animating = True
        
        def animation_worker():
            # Create time axis
            total_start = min(input_start, impulse_start) - 2
            total_end = max(input_end, impulse_end) + 2
            dt = 0.01
            t = np.arange(total_start, total_end, dt)
            
            # Generate signals
            signal1 = self.generate_continuous_signal(self.input_type.get(), input_start, input_end, input_amp, t)
            signal2 = self.generate_continuous_signal(self.impulse_type.get(), impulse_start, impulse_end, impulse_amp, t)
            
            # Calculate correlation range based on signal overlaps
            # For correlation R_xy(τ) = ∫ x(t) * y(t-τ) dt
            # Overlap occurs when both signals are non-zero
            corr_start = input_start - impulse_end
            corr_end = input_end - impulse_start
            
            # Create tau values for animation with some padding
            tau_values = np.arange(corr_start - 1, corr_end + 1, dt * 8)  # Every 8th point
            correlation_result = []
            
            for tau in tau_values:
                if not self.is_animating:
                    break
                    
                # Clear plots
                self.ax1.clear()
                self.ax2.clear()
                self.ax3.clear()
                
                # Plot first signal
                self.ax1.plot(t, signal1, 'b-', linewidth=2, label='x(t)')
                self.ax1.set_title("Signal 1: x(t)")
                self.ax1.grid(True)
                self.ax1.set_xlabel("Time (s)")
                self.ax1.set_ylabel("Amplitude")
                self.ax1.legend()
                
                # Create shifted second signal y(t-τ)
                shifted_signal2 = np.zeros_like(t)
                for i, time_val in enumerate(t):
                    shifted_time = time_val - tau
                    if total_start <= shifted_time <= total_end:
                        shifted_idx = int((shifted_time - total_start) / dt)
                        if 0 <= shifted_idx < len(signal2):
                            shifted_signal2[i] = signal2[shifted_idx]
                
                self.ax2.plot(t, shifted_signal2, 'r-', linewidth=2, label=f'y(t-τ), τ={tau:.2f}')
                self.ax2.axvline(x=tau, color='g', linestyle='--', alpha=0.7, label=f'τ={tau:.2f}')
                self.ax2.set_title(f"Shifted Signal 2: y(t-τ)")
                self.ax2.grid(True)
                self.ax2.set_xlabel("Time (s)")
                self.ax2.set_ylabel("Amplitude")
                self.ax2.legend()
                
                # Show overlap region
                overlap_region = signal1 * shifted_signal2
                if np.any(overlap_region > 0):
                    self.ax1.fill_between(t, 0, overlap_region, alpha=0.3, color='yellow', label='Overlap')
                    self.ax2.fill_between(t, 0, overlap_region, alpha=0.3, color='yellow', label='Overlap')
                    self.ax1.legend()
                    self.ax2.legend()
                
                # Calculate correlation value at current tau
                correlation_value = np.trapz(overlap_region, t)
                correlation_result.append(correlation_value)
                
                # Plot correlation result up to current point
                current_taus = tau_values[:len(correlation_result)]
                self.ax3.plot(current_taus, correlation_result, 'g-', linewidth=2)
                self.ax3.plot(tau, correlation_value, 'ro', markersize=6, label=f'R({tau:.2f})={correlation_value:.3f}')
                self.ax3.set_title("Cross-Correlation R_xy(τ)")
                self.ax3.grid(True)
                self.ax3.set_xlabel("Lag τ (s)")
                self.ax3.set
                
                # Update canvas
                self.fig.tight_layout()
                self.canvas.draw()
                time.sleep(self.animation_speed.get() / 500)
            
            self.is_animating = False
        
        self.animation_thread = threading.Thread(target=animation_worker)
        self.animation_thread.start()
    
    def reset_all(self):
        self.is_animating = False
        
        # Clear plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.canvas.draw()
        
        # Reset to default values
        self.on_mode_change()

def main():
    root = tk.Tk()
    app = ConvolutionVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
