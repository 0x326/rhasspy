Profiles
==========

A Rhasspy profile contains all of the necessary files for wake word detection,
speech transcription, intent recognition, and training.

Each profile is a directory contained in the top-level `profiles` directory, The
`profiles/defaults.json` file contains the default configuration for all
profiles. The `profile.json` file *inside* each individual profile directory
(e.g., `profiles/en/profile.json`) **overrides** settings in `defaults.json`.

Settings
----------

Available profile sections and settings are:

* `rhasspy` - configuration for Rhasspy assistant
  * `preload_profile` - true if speech/intent recognizers for default profile
  * `listen_on_start` - true if Rhasspy should listen for wake word at startup
* `home_assistant` - how to communicate with Home Assistant/Hass.io
  * `url` - Base URL of Home Assistant server (no `/api`)
  * `api_password` - Password, if you have that enabled (Hass.io token is used automatically)
  * `event_type_format` - Python format string used to create event type from intent type (`{0}`)
* `speech_to_text` - transcribing speech to text commands
  * `system` - name of speech to text system (currently only `pocketsphinx`)
  * `pocketsphinx` - configuration for Pocketsphinx
    * `acoustic_model` - directory with CMU 16Khz acoustic model
    * `base_dictionary` - large text file with word pronunciations (read only)
    * `custom_words` - small text file with words/pronunciations added by user
    * `dictionary` - text file with all words/pronunciations needed for example sentences
    * `unknown_words` - small text file with guessed word pronunciations (from phonetisaurus)
    * `language_model` - text file with trigram ARPA language model built from example sentences
  * `sentences_yaml` - YAML file with example sentences/templates grouped by intent
  * `sentences_text` - text file with all example sentences expanded and repeated
  * `classes_yaml` - YAML file with expansions for all sentence templates
  * `g2p_model` - finite-state transducer for phonetisaurus to guess word pronunciations
* `intent` - transforming text commands to intents
  * `system` - intent recognition system (currently `fuzzywuzzy` or `rasa`)
  * `fuzzywuzzy` - configuration for simplistic [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) based intent recognizer
    * `examples_json` - JSON file with intents/example sentences
  * `rasa` - configuration for rasaNLU based intent recognizer
    * `examples_markdown` - Markdown file with intents/example sentences
    * `project_dir` - directory to store project files
    * `project_name` - name of project to generate during training
    * `config` - YAML configuration file for rasaNLU
* `text_to_speech` - pronouncing words
  * `system` - text to speech system (only `espeak` for now)
  * `espeak`
    * `phoneme_map` - text file mapping CMU phonemes to eSpeak phonemes
  * `phoneme_examples` - text file with examples for each CMU phoneme
* `training` - training speech/intent recognizers
  * `balance_sentences` - true if example sentences should be repeated to make all intents equally likely
  * `sentence_casing` - make all sentences `lower` or `upper` case (do nothing if not present)
  * `tokenizer` - system used to break sentences into words (`regex` or `spacy`)
    * `replace` - list of dictionaries with patterns/replacements used on each example sentence
    * `split` - pattern used to break sentences into words
* `wake` - waking Rhasspy up for speech input
  * `system` - wake word recognition system (only `snowboy` for now)
    * `snowboy` - configuration for Snowboy wake word recognizer
      * `model` - path to Snowboy model file (`.umdl` or `.pmdl`)
      * `sensitivity` - sensitivity of detection (range 0-1, defaults to 0.5)
      * `audio_gain` - amount of gain when recording (defaults to 1.0)