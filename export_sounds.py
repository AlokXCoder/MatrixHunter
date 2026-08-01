import numpy as np
import wave
import os

def _save_wav(filename, stereo_data, sample_rate=44100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_data.flatten().tobytes())

def _make_sound(frequency, duration, volume=0.5, wave_type="sine", decay=True, sample_rate=44100):
    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames, dtype=np.float32)

    if wave_type == "sine":
        data = np.sin(2 * np.pi * frequency * t)
    elif wave_type == "square":
        data = np.sign(np.sin(2 * np.pi * frequency * t)).astype(np.float32)
    elif wave_type == "sawtooth":
        data = (2 * (t * frequency - np.floor(t * frequency + 0.5))).astype(np.float32)
    elif wave_type == "noise":
        data = np.random.uniform(-1, 1, frames).astype(np.float32)
    else:
        data = np.sin(2 * np.pi * frequency * t)

    if decay:
        envelope = np.exp(-4.0 * t / duration).astype(np.float32)
        data = data * envelope

    data = (data * volume * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])
    return stereo

def _make_sweep(f_start, f_end, duration, volume=0.5, sample_rate=44100):
    frames = int(duration * sample_rate)
    t  = np.linspace(0, duration, frames, dtype=np.float32)
    f  = np.linspace(f_start, f_end, frames, dtype=np.float32)
    data = np.sin(2 * np.pi * np.cumsum(f) / sample_rate).astype(np.float32)
    envelope = np.exp(-2.0 * t / duration).astype(np.float32)
    data = (data * envelope * volume * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])
    return stereo

def _build_music_loop(bpm, duration_bars):
    sr      = 44100
    beat_s  = 60.0 / bpm
    frames  = int(beat_s * 4 * duration_bars * sr)   # 4 beats per bar
    data    = np.zeros(frames, dtype=np.float32)

    # place a kick every beat
    kick_len = int(0.18 * sr)
    t_kick   = np.linspace(0, 0.18, kick_len, dtype=np.float32)
    kick     = np.sin(2*np.pi*55*t_kick) * np.exp(-14*t_kick)

    beat_frames = int(beat_s * sr)
    for b in range(4):
        start = b * beat_frames
        end   = start + kick_len
        if end <= frames:
            data[start:end] += kick * 0.5

    # soft hi-hat every half-beat
    hat_len = int(0.04 * sr)
    t_hat   = np.linspace(0, 0.04, hat_len, dtype=np.float32)
    hat     = np.random.uniform(-1,1,hat_len).astype(np.float32) * np.exp(-40*t_hat)
    for b in range(8):
        start = int(b * beat_frames / 2)
        end   = start + hat_len
        if end <= frames:
            data[start:end] += hat * 0.15

    data = np.clip(data, -1, 1)
    data = (data * 0.4 * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])
    return stereo

sounds = {
    "menu_click": _make_sound(880,  0.08, 0.4, "sine",    decay=True),
    "menu_hover": _make_sound(440,  0.04, 0.2, "sine",    decay=True),
    "menu_back":  _make_sound(220,  0.12, 0.3, "sine",    decay=True),
    "pistol":     _make_sound(300,  0.10, 0.7, "square",  decay=True),
    "rifle":      _make_sound(180,  0.15, 0.8, "square",  decay=True),
    "shotgun":    _make_sound(120,  0.18, 0.9, "noise",   decay=True),
    "sniper_shot":_make_sound(600,  0.12, 0.7, "sine",    decay=True),
    "reload":     _make_sweep(400,  150,  0.25, 0.4),
    "empty_gun":  _make_sound(1200, 0.07, 0.3, "square",  decay=True),
    "footstep":   _make_sound(80,   0.06, 0.2, "noise",   decay=True),
    "key_pickup": _make_sweep(500,  1500, 0.2, 0.5),
    "door_open":  _make_sound(200,  0.3,  0.5, "sawtooth",decay=True),
    "alarm":      _make_sound(880,  0.5,  0.6, "square",  decay=False),
    "alarm_off":  _make_sound(440,  0.3,  0.4, "square",  decay=True),
    "stealth":    _make_sound(660,  0.1,  0.3, "sine",    decay=True),
    "spotted":    _make_sweep(300,  900,  0.3, 0.7),
    "laser":      _make_sweep(800,  200,  0.15, 0.6),
    "laser2":     _make_sweep(1200, 300,  0.12, 0.5),
    "explosion":  _make_sound(80,   0.35, 0.9, "noise",   decay=True),
    "big_explosion":_make_sound(50, 0.55, 1.0, "noise",   decay=True),
    "powerup":    _make_sweep(440,  1760, 0.3, 0.6),
    "shield_hit": _make_sound(600,  0.15, 0.5, "square",  decay=True),
    "warp":       _make_sweep(200,  2000, 0.4, 0.5),
    "jump":       _make_sweep(200,  600,  0.2, 0.5),
    "land":       _make_sound(100,  0.08, 0.4, "noise",   decay=True),
    "slide":      _make_sound(200,  0.15, 0.3, "sawtooth",decay=True),
    "coin":       _make_sweep(660,  1320, 0.1, 0.5),
    "crash":      _make_sound(100,  0.4,  0.8, "noise",   decay=True),
    "speed_up":   _make_sweep(300,  900,  0.25, 0.5),
    "hit":        _make_sound(150,  0.15, 0.6, "noise",   decay=True),
    "player_hit": _make_sound(200,  0.2,  0.7, "noise",   decay=True),
    "death":      _make_sweep(400,  50,   0.5, 0.8),
    "boss_roar":  _make_sound(60,   0.6,  0.9, "sawtooth",decay=True),
    "level_up":   _make_sweep(440,  880,  0.5, 0.6),
    "game_over":  _make_sweep(600,  100,  0.8, 0.7),
    "victory":    _make_sweep(440,  1760, 0.6, 0.7),
    "music_menu":     _build_music_loop(80, 1.0),
    "music_sniper":   _build_music_loop(120, 1.0),
    "music_assassin": _build_music_loop(60, 1.0),
    "music_space":    _build_music_loop(100, 1.0),
    "music_runner":   _build_music_loop(140, 1.0)
}

for name, data in sounds.items():
    _save_wav(f"assets/sounds/{name}.wav", data)
print("All sounds exported!")
