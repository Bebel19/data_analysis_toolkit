# scripts/emotion_analysis.py

import pandas as pd
import time
import json
import http.client
import urllib.parse
from scripts import ScriptInterface
from utils.secrets import TWINWORD_API_KEY
from utils.logger import logger


class EmotionAnalysis(ScriptInterface):
    def run(self, input_file=None, output_file=None, **kwargs):
        data = pd.read_csv(input_file, encoding='utf-8')
        max_requests = int(kwargs.get("max_requests", 1000))
        request_count = 0
        results = []

        for index, row in data.iterrows():
            if request_count >= max_requests:
                logger.info("Quota atteint. Arrêt du traitement.")
                break

            text = str(row.get("TEXT_ENGLISH", ""))
            if len(text) > 14336:
                text = text[:14336]

            result = self.call_twinword_api(text)
            scores = result.get("emotion_scores", {}) if result else {}

            results.append({
                'TEXT_ENGLISH': text,
                'Anger': scores.get('anger', 0),
                'Disgust': scores.get('disgust', 0),
                'Fear': scores.get('fear', 0),
                'Joy': scores.get('joy', 0),
                'Sadness': scores.get('sadness', 0),
                'Surprise': scores.get('surprise', 0)
            })

            request_count += 1
            if request_count % 6 == 0:
                time.sleep(1)

        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Analyse terminée. Fichier écrit : {output_file}")

    def call_twinword_api(self, text):
        try:
            conn = http.client.HTTPSConnection("twinword-emotion-analysis-v1.p.rapidapi.com")
            payload = urllib.parse.urlencode({"text": text})
            headers = {
                'x-rapidapi-key': TWINWORD_API_KEY,
                'x-rapidapi-host': "twinword-emotion-analysis-v1.p.rapidapi.com",
                'Content-Type': "application/x-www-form-urlencoded"
            }

            conn.request("POST", "/analyze/", payload, headers)
            res = conn.getresponse()
            response = res.read().decode("utf-8")
            return json.loads(response)
        except Exception as e:
            logger.error(f"Erreur API Twinword : {e}")
            return None

    def get_metadata(self):
        return {
            "name": "Analyse d'Émotion",
            "input_required": True,
            "parameters": {
                "max_requests": {
                    "type": "int",
                    "default": 1000,
                    "help": "Nombre maximum de requêtes API à effectuer"
                }
            }
        }
