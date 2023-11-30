from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer
from transformers import pipeline

from token_classification.utilities import get_best_checkpoint
from token_classification.utilities import process_labels
from token_classification.utilities import reconstruct_text_from_labels
from token_classification.utilities import specs_to_text

checkpoint = get_best_checkpoint()
model = AutoModelForTokenClassification.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
token_classifier = pipeline(task="ner", model=model, tokenizer=tokenizer)

# Example 1
example_data = {"HDMI Eingänge": "3x", "HDMI Version": "2.0", "DisplayPort": "1x"}

res = token_classifier(specs_to_text(example_data))
print(res)

res2 = reconstruct_text_from_labels(res)
print(res2)

structured_res = process_labels(res)
print(structured_res)

# Example 2
text_input = "Bildschirmdiagonale/Zoll:21.5 Zoll;Auflösung:1920x1080 (16:9);Paneltyp:VA;Höhenverstellbarkeit:nein;Energieeffizienzklasse:E;VGA:1x;DVI:0x;DisplayPort:1x;HDMI:3x;VESA-Bohrung:100x100;Swivelfunktion:nein;Pivotfunktion:nein;Lautsprecher:nein;Reaktionszeit:4 Millisekunden;Helligkeit:250 cd/m2;Bildschirmdiagonale/cm:54.6 cm;Touch-Funktion:nein"
print(text_input)

res = token_classifier(text_input)
print(res)

res2 = reconstruct_text_from_labels(res)
print(res2)

structured_res = process_labels(res)
print(structured_res)
