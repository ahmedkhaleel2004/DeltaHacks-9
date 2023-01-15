from PyQt6 import QtWidgets, QtGui
from gingerit.gingerit import GingerIt
from PyQt6.QtCore import QMetaObject, QThread, QTimer
import sys
import time
import whisper
import cv2
import wave
import pyaudio

class MyApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.audio_transcript_box = QtWidgets.QTextEdit(self)
        self.audio_transcript_box.setReadOnly(True)
        self.audio_transcript_box.setStyleSheet("background-color: black; color: white;")
        
        # Create record audio button
        self.record_audio_button = QtWidgets.QPushButton("Record Audio", self)
        self.record_audio_button.clicked.connect(self.record_audio)

        # Create record video button
        self.record_video_button = QtWidgets.QPushButton("Record Video", self)
        self.record_video_button.clicked.connect(self.record_video)

        # Create a timer button
        self.timer_button = QtWidgets.QPushButton("Start Timer", self)
        self.timer_button.clicked.connect(self.start_timer)

        self.generate_button = QtWidgets.QPushButton("Generate Report", self)
        self.generate_button.clicked.connect(self.open_window)

        # Create export to pdf button
        self.export_pdf_button = QtWidgets.QPushButton("Export to PDF", self)
        self.export_pdf_button.clicked.connect(self.export_pdf)

        # Create a vertical layout for the audio transcript box and the timer and export buttons
        audio_transcript_layout = QtWidgets.QVBoxLayout()
        audio_transcript_layout.addWidget(self.audio_transcript_box)
        audio_transcript_layout.addWidget(self.timer_button)
        audio_transcript_layout.addWidget(self.export_pdf_button)

        # Create a horizontal layout to separate the button layout from the audio transcript layout
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.record_audio_button)
        main_layout.addWidget(self.record_video_button)
        main_layout.addLayout(audio_transcript_layout)

    def record_audio(self):
        # Code to record audio goes here
        self.audio_transcript_box.setReadOnly(False)
        self.audio_transcript_box.setStyleSheet("background-color: black; color: white;")
        self.audio_transcript_box.setText("Recording Audio")
        
        # Schedule the text box to be cleared after 3 seconds
        QTimer.singleShot(3000, self.start_recording)

    def start_recording(self):
        # Set audio recording parameters
        channels = 2
        sample_rate = 48000
        frames_per_buffer = 512

        # Create a PyAudio object
        p = pyaudio.PyAudio()

        # Open a stream for audio recording
        stream = p.open(format=p.get_format_from_width(3),
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=frames_per_buffer)

        # Create a wave file to save the audio data
        wave_file = wave.open("audio.wav", "wb")
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(p.get_sample_size(p.get_format_from_width(3)))
        wave_file.setframerate(sample_rate)

        # Start audio recording
        start_time = time.time()

        while True:
            data = stream.read(frames_per_buffer)
            wave_file.writeframes(data)
            if time.time() - start_time > 5:
                break

        # Stop audio recording
        stream.stop_stream()
        stream.close()
        wave_file.close()
        p.terminate()

        self.audio_transcript_box.setText("")

    def record_video(self):
        # Code to record video goes here
        self.audio_transcript_box.setText("Recording Video")
        # Create a VideoCapture object to record video
        cap = cv2.VideoCapture(0)

        # Set the video frame width and height
        cap.set(3, 640)
        cap.set(4, 480)

        #set the fps
        cap.set(cv2.CAP_PROP_FPS, 30)

        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter("video.avi", fourcc, 30.0, (640, 480))

        # Start video recording
        start_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            cv2.imshow("Recording", frame)
            if time.time() - start_time > 5:
                break

        # Stop video recording
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def start_timer(self):
        # Code to start timer goes here
        self.timer_button.setText("Stop Timer")
        self.timer_button.clicked.disconnect()
        self.timer_button.clicked.connect(self.stop_timer)
        self.start_time = time.time()

    def stop_timer(self):
        self.timer_button.setText("Start Timer")
        self.timer_button.clicked.disconnect()
        self.timer_button.clicked.connect(self.start_timer)
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        self.audio_transcript_box.append("Timer stopped, elapsed time: {:.2f} seconds".format(total_time))

    def export_pdf(self):
        # Code to export pdf goes here
        pass

    def open_window(self):
        # Create a new window
        report_window = QtWidgets.QMainWindow(self)
        report_window.setWindowTitle("Generate Report")

        old_textbox = QtWidgets.QTextEdit(report_window)
        new_textbox = QtWidgets.QTextEdit(report_window)
        report_window.setCentralWidget(old_textbox)
        report_window.setCentralWidget(new_textbox)
        
        report_window.show()

        model = whisper.load_model("base")
        result = model.transcribe("audio.wav")
        parser = GingerIt()

        original_text = result["text"]
        corrected = parser.parse(result["text"]).get("result")

        new_textbox.setPlainText("Original: " + original_text + "\nCorrected: " + corrected)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())