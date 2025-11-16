"""Audio analysis module for distinguishing modem from fax tones using FFT."""

import io
import logging
from concurrent.futures import Future, ThreadPoolExecutor

import numpy as np
import requests
from scipy import signal
from scipy.io import wavfile

logger = logging.getLogger(__name__)

# Define frequency ranges for different signal types
FAX_CNG_FREQUENCY = 1100  # Hz - Fax calling tone
FAX_CED_FREQUENCY = 2100  # Hz - Fax called station identification
MODEM_V22_ANSWER = 2400  # Hz - V.22 answer tone
MODEM_V22_ORIGINATE = 1200  # Hz - V.22 originate tone
MODEM_RANGE = (1650, 2400)  # Hz - General modem carrier range (excludes CED)

# Analysis parameters
FREQUENCY_TOLERANCE = 50  # Hz - tolerance for frequency matching
MIN_DURATION = 0.5  # seconds - minimum duration of tone to be considered valid
CONFIDENCE_THRESHOLD = 0.7  # minimum confidence for tone detection


def analyze_recording(recording_url: str, timeout: int = 30) -> dict[str, any]:
    """
    Analyze audio recording to determine tone type using FFT.

    Downloads the recording from the URL, performs FFT analysis to identify
    frequency peaks, and classifies the tone as modem, fax, voice, or unknown.

    Args:
        recording_url: URL to download the audio recording (.wav format)
        timeout: Download timeout in seconds

    Returns:
        Dictionary with:
            - tone_type: "modem", "fax", "voice", or "unknown"
            - peak_frequency: Primary detected frequency in Hz
            - confidence: Confidence score (0.0-1.0)
            - all_peaks: List of all significant frequency peaks
    """
    try:
        # Download the recording
        logger.info(f"Downloading recording from {recording_url}")
        response = requests.get(recording_url, timeout=timeout)
        response.raise_for_status()

        # Load audio data
        audio_data = io.BytesIO(response.content)
        sample_rate, audio = wavfile.read(audio_data)

        # Convert stereo to mono if needed
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)

        # Normalize audio
        audio = audio.astype(float)
        if audio.max() > 0:
            audio = audio / audio.max()

        # Perform FFT analysis
        fft_result = perform_fft_analysis(audio, sample_rate)

        return fft_result

    except requests.RequestException as e:
        logger.error(f"Failed to download recording: {e}")
        return {
            "tone_type": "unknown",
            "peak_frequency": None,
            "confidence": 0.0,
            "error": str(e),
        }
    except Exception as e:
        logger.error(f"Error analyzing recording: {e}")
        return {
            "tone_type": "unknown",
            "peak_frequency": None,
            "confidence": 0.0,
            "error": str(e),
        }


def perform_fft_analysis(audio: np.ndarray, sample_rate: int) -> dict[str, any]:
    """
    Perform FFT analysis on audio signal to detect frequency peaks.

    Args:
        audio: Audio signal as numpy array
        sample_rate: Sample rate in Hz

    Returns:
        Dictionary with tone analysis results
    """
    # Compute FFT
    fft = np.fft.fft(audio)
    freqs = np.fft.fftfreq(len(fft), 1 / sample_rate)

    # Only consider positive frequencies
    positive_freqs_mask = freqs > 0
    freqs = freqs[positive_freqs_mask]
    magnitudes = np.abs(fft[positive_freqs_mask])

    # Find peaks in the frequency spectrum
    # Use scipy.signal to find prominent peaks
    peak_indices, peak_properties = signal.find_peaks(
        magnitudes,
        height=magnitudes.max() * 0.1,  # At least 10% of max magnitude
        distance=int(100 * len(freqs) / (sample_rate / 2)),  # At least 100 Hz apart
    )

    if len(peak_indices) == 0:
        logger.warning("No significant frequency peaks found")
        return {
            "tone_type": "unknown",
            "peak_frequency": None,
            "confidence": 0.0,
            "all_peaks": [],
        }

    # Get peak frequencies and their magnitudes
    peak_freqs = freqs[peak_indices]
    peak_mags = magnitudes[peak_indices]

    # Sort by magnitude (strongest peaks first)
    sorted_indices = np.argsort(peak_mags)[::-1]
    peak_freqs = peak_freqs[sorted_indices]
    peak_mags = peak_mags[sorted_indices]

    # Take top 5 peaks
    top_peaks = list(zip(peak_freqs[:5], peak_mags[:5], strict=False))
    primary_freq = peak_freqs[0]

    # Classify tone based on primary frequency
    tone_type, confidence = classify_tone(primary_freq, peak_freqs, peak_mags)

    logger.info(
        f"FFT Analysis: primary_freq={primary_freq:.1f}Hz, "
        f"tone_type={tone_type}, confidence={confidence:.2f}"
    )

    return {
        "tone_type": tone_type,
        "peak_frequency": float(primary_freq),
        "confidence": float(confidence),
        "all_peaks": [(float(f), float(m)) for f, m in top_peaks],
    }


def classify_tone(
    primary_freq: float, all_freqs: np.ndarray, all_mags: np.ndarray
) -> tuple[str, float]:
    """
    Classify tone type based on frequency peaks.

    Args:
        primary_freq: Primary (strongest) frequency peak
        all_freqs: All detected frequency peaks
        all_mags: Magnitudes of all peaks

    Returns:
        Tuple of (tone_type, confidence)
    """
    # Check for fax CNG tone (1100 Hz)
    if abs(primary_freq - FAX_CNG_FREQUENCY) < FREQUENCY_TOLERANCE:
        # High confidence if frequency matches closely
        confidence = 1.0 - (abs(primary_freq - FAX_CNG_FREQUENCY) / FREQUENCY_TOLERANCE)
        return "fax", max(confidence, CONFIDENCE_THRESHOLD)

    # Check for fax CED tone (2100 Hz) - less common for initial detection
    if abs(primary_freq - FAX_CED_FREQUENCY) < FREQUENCY_TOLERANCE:
        # Could be modem or fax, check for additional fax indicators
        # If there's also a 1100 Hz component, likely fax
        has_cng = any(
            abs(f - FAX_CNG_FREQUENCY) < FREQUENCY_TOLERANCE for f in all_freqs
        )
        if has_cng:
            return "fax", 0.9
        # Otherwise might be modem V.22bis answer tone (2400 Hz is close)
        return "modem", 0.75

    # Check for V.22 modem originate tone (1200 Hz)
    if abs(primary_freq - MODEM_V22_ORIGINATE) < FREQUENCY_TOLERANCE:
        confidence = 1.0 - (
            abs(primary_freq - MODEM_V22_ORIGINATE) / FREQUENCY_TOLERANCE
        )
        return "modem", max(confidence, CONFIDENCE_THRESHOLD)

    # Check for V.22 modem answer tone (2400 Hz)
    if abs(primary_freq - MODEM_V22_ANSWER) < FREQUENCY_TOLERANCE:
        confidence = 1.0 - (abs(primary_freq - MODEM_V22_ANSWER) / FREQUENCY_TOLERANCE)
        return "modem", max(confidence, CONFIDENCE_THRESHOLD)

    # Check if in general modem range (1650-2400 Hz, excluding CED)
    if MODEM_RANGE[0] <= primary_freq <= MODEM_RANGE[1]:
        # Check it's not too close to CED
        if abs(primary_freq - FAX_CED_FREQUENCY) > FREQUENCY_TOLERANCE:
            # Confidence based on how centered it is in the range
            range_center = (MODEM_RANGE[0] + MODEM_RANGE[1]) / 2
            distance_from_center = abs(primary_freq - range_center)
            max_distance = (MODEM_RANGE[1] - MODEM_RANGE[0]) / 2
            confidence = 1.0 - (distance_from_center / max_distance) * 0.3
            return "modem", max(confidence, 0.7)

    # Check for voice patterns
    # Voice typically has multiple peaks across 300-3400 Hz range
    voice_range_freqs = [f for f in all_freqs if 300 <= f <= 3400]
    if len(voice_range_freqs) >= 3:
        # Multiple peaks suggest voice
        # Check if peaks are distributed (not concentrated in one frequency)
        freq_std = np.std(voice_range_freqs[:5])  # Standard deviation of top 5 peaks
        if freq_std > 300:  # Peaks spread across at least 300 Hz
            return "voice", 0.75

    # If primary frequency is in voice range but not classified as modem/fax
    if 300 <= primary_freq <= 3400:
        return "voice", 0.6

    # Unknown - frequency doesn't match known patterns
    return "unknown", 0.0


def analyze_recording_async(
    recording_url: str, executor: ThreadPoolExecutor, timeout: int = 30
) -> Future:
    """
    Analyze recording asynchronously using a thread pool.

    Args:
        recording_url: URL to the recording
        executor: ThreadPoolExecutor to run analysis
        timeout: Download timeout in seconds

    Returns:
        Future object that will contain the analysis result
    """
    return executor.submit(analyze_recording, recording_url, timeout)


def cleanup_recording(recording_sid: str, twilio_client) -> bool:
    """
    Delete a recording from Twilio.

    Args:
        recording_sid: Twilio recording SID (starts with RE)
        twilio_client: Initialized Twilio client

    Returns:
        True if deletion successful, False otherwise
    """
    try:
        twilio_client.recordings(recording_sid).delete()
        logger.info(f"Deleted recording {recording_sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete recording {recording_sid}: {e}")
        return False
