from enrol import Enroll
import pyaudio
import wave
from rpi_rf import RFDevice
from gpiozero import Servo
import time
import logging

dir =  'test.wav'

while True:

    form_1 = pyaudio.paInt16  # 16-bit resolution
    chans = 1  # 1 channel
    samp_rate = 44100  # 44.1kHz sampling rate
    chunk = 4096  # 2^12 samples for buffer
    record_secs = 3  # seconds to record
    dev_index = 2  # device index found by p.get_device_info_by_index(ii)
    wav_output_filename = dir  # name of .wav file

    audio = pyaudio.PyAudio()  # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format=form_1, rate=samp_rate, channels=chans, \
                        input_device_index=dev_index, input=True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0, int((samp_rate / chunk) * record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    enrolled = Enroll(recordings=dir)
    predict = enrolled.verify()
    if predict[0] == 0:
        print("Please Try again")
    else:
        rfdevice = RFDevice()
        rfdevice.enable_tx()
        rfdevice.tx_code("1234")
        rfdevice.cleanup()

        rfdevice = RFDevice(args.gpio)
        rfdevice.enable_rx()
        timestamp = None
        logging.info("Listening for codes on GPIO " + str(args.gpio))
        for i in range(1,100):
            if rfdevice.rx_code_timestamp != timestamp:
                timestamp = rfdevice.rx_code_timestamp
                logging.info(str(rfdevice.rx_code) +
                             " [pulselength " + str(rfdevice.rx_pulselength) +
                             ", protocol " + str(rfdevice.rx_proto) + "]")
                result = str(rfdevice.rx_code)
            time.sleep(0.01)
        rfdevice.cleanup()

        if result == "1234":
            servo = Servo(25)

            servo.mid()
            time.sleep(0.5)

