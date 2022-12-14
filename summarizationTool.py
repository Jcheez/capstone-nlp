import os
# from gensim.summarization import summarize
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
import nltk
nltk.download("punkt")
from nltk.tokenize import sent_tokenize
from summarizer import Summarizer
from transformers import BartForConditionalGeneration, BartTokenizer

def combine_string(sentences_list):
	combined = ""
	for i in sentences_list:
		combined += i
		combined += ". "
	return combined

def sentence_count(text): 
	return len(sent_tokenize(text))

def word_count(text):
	word_list = text.split()
	return len(word_list)

def sentence_chunks(text):
	sentences_list=text.split(".")
	chunks = []
	temp_chunk = ""
	for new_sentence in sentences_list:
		if word_count(temp_chunk) + word_count(new_sentence) < 512:
			temp_chunk += new_sentence
			temp_chunk += ". "
		else: 
			chunks += [temp_chunk]
			temp_chunk = ""
	chunks += [temp_chunk]
	return chunks

def summarize_chunks(original_text, tokenizer, my_model):
	summary = ""
	counter = 1
	chunks = sentence_chunks(original_text)
	for i in range(len(chunks)):
		print("Summarization Progress Bar: " + str(i+1) + "/" + str(len(chunks)))
		sentences = chunks[i]
		counter = counter + 1
		input_ids = tokenizer.encode("summarize:"+sentences, return_tensors='pt')
		summary_ids = my_model.generate(input_ids, early_stopping=True, min_length= int(0.3 * len(sentences.split(' '))), max_length = int(round(0.5 * len(sentences.split(' ')))))
		summary_indiv = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
		summary += summary_indiv.replace("<pad>", " ")
		summary += " "
	return summary

def run_summary(filepath):
	with open(filepath, encoding="utf8") as f:
		contents = f.read()
		f.close()

	bart_tokenizer=BartTokenizer.from_pretrained('facebook/bart-large-cnn')
	bart_model=BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

	text = contents.strip().replace("\n","")
	# extractive_summary = gensim.summarization.summarize(text, ratio=0.5)
	model = LexRankSummarizer()
	my_parser = PlaintextParser.from_string(text, Tokenizer("english"))
	lexrank_summary = model(my_parser.document, sentences_count = sentence_count(text)/2)
	extractive_summary = ""
	for sentence in lexrank_summary:
		extractive_summary = extractive_summary + str(sentence)
	# extractive_summary = model(text, ratio=0.5)
	summary = summarize_chunks(extractive_summary, bart_tokenizer, bart_model)

	basePath = "./assets/outputs/summarization/"
	basename = os.path.basename(filepath).split(".")[0]
	output_path = f"{basePath}{basename}_output.txt"

	with open(output_path,'w', encoding="utf8") as output_f:
		output_f.write(summary)
		output_f.close()
