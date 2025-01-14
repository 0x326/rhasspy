import os
import sys
import json
import tempfile
import unittest
import logging
import argparse

logging.basicConfig(level=logging.DEBUG)

from rhasspy.core import RhasspyCore


class RhasspyTestCore:
    def __init__(self, profile_name, train=True):
        self.profile_name = profile_name
        self.system_profiles_dir = os.path.join(os.getcwd(), "profiles")
        self.train = train

    def __enter__(self):
        self.user_profiles_dir = tempfile.TemporaryDirectory()
        self.core = RhasspyCore(
            self.profile_name, self.system_profiles_dir, self.user_profiles_dir.name
        )
        self.core.profile.set("wake.system", "dummy")
        self.core.start(preload=False)

        if self.train:
            self.core.train()

        return self.core

    def __exit__(self, *args):
        self.core.shutdown()

        try:
            self.user_profiles_dir.cleanup()
        except:
            pass


# -----------------------------------------------------------------------------


class RhasspyTestCase(unittest.TestCase):
    PROFILES = ["en", "de", "es", "fr", "it", "nl", "ru", "pt"]
    # Not passing: vi, el (bad transcriptions)
    # Not tested: hi, zh

    # -------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        self.profiles = RhasspyTestCase.PROFILES
        self.test_wav_path = {
            p: os.path.join("etc", "test", p, "test.wav") for p in self.profiles
        }
        self.test_json = {
            p: json.load(open(os.path.join("etc", "test", p, "test.json")))
            for p in self.profiles
        }

        unittest.TestCase.__init__(self, *args, **kwargs)

    # -------------------------------------------------------------------------

    def test_transcribe(self):
        """speech -> text"""
        for profile_name in self.profiles:
            with RhasspyTestCore(profile_name) as core:
                wav_path = self.test_wav_path[profile_name]
                test_info = self.test_json[profile_name]

                with open(wav_path, "rb") as wav_file:
                    text = core.transcribe_wav(wav_file.read()).text
                    self.assertEqual(text, test_info["text"])

    # -------------------------------------------------------------------------

    def test_recognize(self):
        """text -> intent"""
        for profile_name in self.profiles:
            with RhasspyTestCore(profile_name) as core:
                test_info = self.test_json[profile_name]
                intent = core.recognize_intent(test_info["text"]).intent
                self.assertEqual(intent["intent"]["name"], test_info["intent"]["name"])

                expected_entities = test_info["entities"]
                for ev in intent["entities"]:
                    entity = ev["entity"]
                    if (entity in expected_entities) and (
                        ev["value"] == expected_entities[entity]
                    ):
                        expected_entities.pop(entity)

                self.assertEqual(expected_entities, {})

    # -------------------------------------------------------------------------

    def test_training(self):
        """Test training"""
        for profile_name in self.profiles:
            with RhasspyTestCore(profile_name, train=False) as core:
                wav_path = self.test_wav_path[profile_name]
                test_info = self.test_json[profile_name]

                old_sentences_path = core.profile.read_path(
                    core.profile.get("speech_to_text.sentences_ini")
                )

                new_sentences_path = core.profile.write_path(
                    core.profile.get("speech_to_text.sentences_ini")
                )

                # Remove intent
                expected_intent = test_info["intent"]["name"]
                with open(old_sentences_path, "r") as old_sentences_file:
                    with open(new_sentences_path, "w") as new_sentences_file:
                        in_intent = False
                        for line in old_sentences_file:
                            line = line.strip()

                            if not in_intent and (line == f"[{expected_intent}]"):
                                in_intent = True
                            elif in_intent and line.startswith("["):
                                # On to next intent
                                in_intent = False

                            if not in_intent:
                                print(line, file=new_sentences_file)

                # Train without target intent
                core.train()
                expected_text = test_info["text"]
                with open(wav_path, "rb") as wav_file:
                    text = core.transcribe_wav(wav_file.read()).text

                    # Should fail to match
                    self.assertNotEqual(text, expected_text)

                # Delete changes
                os.unlink(new_sentences_path)

                core.train()
                with open(wav_path, "rb") as wav_file:
                    text = core.transcribe_wav(wav_file.read()).text

                    # Should match now
                    self.assertEqual(text, expected_text)

    # -------------------------------------------------------------------------

    def test_pronounce(self):
        for profile_name in self.profiles:
            with RhasspyTestCore(profile_name) as core:
                test_info = self.test_json[profile_name]

                # Known word
                known_word = test_info["words"]["known"]["word"]
                pronunciations = core.get_word_pronunciations(
                    [known_word]
                ).pronunciations
                self.assertIn(
                    test_info["words"]["known"]["phonemes"],
                    pronunciations[known_word]["pronunciations"],
                )

                # Unknown word
                known_word = test_info["words"]["known"]["word"]
                unknown_word = test_info["words"]["unknown"]["word"]
                pronunciations = core.get_word_pronunciations(
                    [unknown_word], n=5
                ).pronunciations
                self.assertIn(
                    test_info["words"]["unknown"]["phonemes"],
                    pronunciations[unknown_word]["pronunciations"],
                )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile", "-p", default=None, help="Only run tests for the given profile"
    )
    prog_name = sys.argv[0]
    args, rest = parser.parse_known_args()

    if args.profile:
        logging.debug(f"Only running tests for {args.profile}")
        RhasspyTestCase.PROFILES = [args.profile]

    argv = [prog_name] + rest
    unittest.main(argv=argv)
