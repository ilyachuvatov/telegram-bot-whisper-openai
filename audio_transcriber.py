from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

class HuggingFaceModel:
    def __init__(self):
        model_id = "openai/whisper-medium"
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.pipe = pipeline(
                    "automatic-speech-recognition",
                    model=self.model,
                    tokenizer=self.processor.tokenizer,
                    feature_extractor=self.processor.feature_extractor,
                    max_new_tokens=128,
                    chunk_length_s=30,
                    batch_size=16,
                    return_timestamps=True,
                    device='mps',
        )

    def transcribe(self, audio_data):
        return self.pipe(audio_data, generate_kwargs={'task':'transcribe'})
    

    



    

