import os
import time
from datetime import datetime

import pygame
from decouple import config

from ai.eleven import Eleven
from ai.open_ai import ChatGPT, Whisper
from ai.play_ht import PlayHt
from pynput import keyboard
from utils.audio_player import AudioPlayer
from utils.logging import log
from utils.word_wrap import WordWrap


class Character:
    def __init__(self, yaml):
        self.name = yaml.get('name', None)
        self.chat_model_override = yaml.get('chat_model_override', None)
        self.motivation = yaml.get('motivation', None)
        self.rules = yaml.get('rules', None)
        self.voice = yaml.get('voice', None)
        self.max_angle = 35
        self.max_rotation = 3
        self.max_amplitude = 1000
        self.prev_angle = 0
        self.image = None
        self.speak_sound = None
        self.listener = None
        self.font = None

    def chat(self, messages):
        response, usage = ChatGPT.chat(messages, self.chat_model_override)

        log.info(f'Character ({self.name}): {response}')

        audio_file = None
        if config('ENABLE_SPEECH', cast=bool):
            audio_file = self.synthesize_speech(response)
        else:
            log.info('Speech synthesis is disabled. Skipping.')

        return response, usage, audio_file

    def synthesize_speech(self, text):
        tts_service = config('TTS_SERVICE')
        log.info(f'{tts_service}: Speech synthesis requested')
        if tts_service == 'PlayHT':
            audio_file = PlayHt.fetch_audio_file(text, self.voice)
        elif tts_service == 'ElevenLabs':
            audio_file = Eleven.speak(text, self.voice)
        else:
            audio_file = None
        if self.speak_sound is None:
            self.speak_sound = pygame.mixer.Sound("beep_basic_low.mp3")
            self.speak_sound.set_volume(0.1)

        return audio_file

    async def speak(self, ai_output, playback, screen):
        self.font = pygame.font.Font(config('SUBTITLE_FONT'), config('SUBTITLE_FONT_SIZE', cast=int))
        self.font.set_bold(config('SUBTITLE_FONT_BOLD', cast=bool))

        pygame.mixer.Sound.play(self.speak_sound)

        with (AudioPlayer(ai_output) as audio_player):
            text_renders = self.create_text_renders(ai_output.subtitles, 0)

            start_time = datetime.now()
            segment = 0
            for amplitude in audio_player.play_audio_chunk():
                while playback.paused:
                    time.sleep(1)
                screen.fill((0, 255, 0))
                self.animate_frame(amplitude, screen)
                if len(ai_output.subtitles["segments"]) > segment + 1 and ai_output.subtitles["segments"][segment + 1]["words"][0]["end"] < (datetime.now() - start_time).total_seconds():
                    segment = segment + 1
                    text_renders = self.create_text_renders(ai_output.subtitles, segment)
                text_offset = 0
                for text_render in text_renders:
                    text_rect = text_render.get_rect(center=((1920 // 2), 975 + text_offset))
                    screen.blit(text_render, text_rect)
                    text_offset += self.font.get_height() + 2
                pygame.display.update()
        screen.fill((0, 255, 0))
        pygame.display.update()

    def animate_frame(self, amplitude, screen):
        if self.image is None:
            file_name = f"config/characters/images/{self.name}.png"
            if os.path.isfile(file_name):
                self.image = pygame.image.load(file_name).convert_alpha()
        if amplitude > self.max_amplitude:
            self.max_amplitude = amplitude

        scaled_amplitude = min(amplitude, self.max_amplitude) / self.max_amplitude
        target_angle = scaled_amplitude * self.max_angle
        target_rotation_amount = target_angle - self.prev_angle
        actual_rotation_amount = max(-self.max_rotation, min(self.max_rotation, target_rotation_amount))
        new_angle = max(-self.max_angle, min(self.max_angle, actual_rotation_amount + self.prev_angle))
        rotated_image = pygame.transform.rotate(self.image, new_angle)
        rotated_rect = rotated_image.get_rect(center=(config('CHARACTER_CENTER_X', cast=int), config('CHARACTER_CENTER_Y', cast=int)))
        self.prev_angle = new_angle

        pygame.event.get()
        screen.blit(rotated_image, rotated_rect)


    def create_text_renders(self, text, segment_num):
        segment_words = text["segments"][segment_num]["text"]
        segment_words_lines = WordWrap.split_string_by_length(segment_words, config('SUBTITLE_MAX_CHARS_PER_LINE', cast=int))
        text_renders = []
        for segment_words_line in segment_words_lines:
            text_renders.append(self.font.render(segment_words_line, True, (255, 255, 0)))
        return text_renders
