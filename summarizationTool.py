# import glob, os
import gensim
from gensim.summarization import summarize
from transformers import BartForConditionalGeneration, BartTokenizer

################# FILE PATH SET UP #################
input_dir = R"C:\Users\limji\OneDrive - National University of Singapore\Y4S1\BT4103"
input_file = "TextData.txt"
output_dir = R"C:\Users\limji\OneDrive - National University of Singapore\Y4S1\BT4103\Summary"
input_path = input_dir + "\\" + input_file
output_path = output_dir + "\\" + input_file[:-4] + " Output" + input_file[-4:]

################# SUMMARIZATIN TOOL #################
with open(input_path, encoding="utf8") as f:
    contents = f.read()
    f.close()

bart_tokenizer=BartTokenizer.from_pretrained('facebook/bart-large-cnn')
bart_model=BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

def combine_string(sentences_list):
	combined = ""
	for i in sentences_list:
		combined += i
		combined += ". "
	return combined

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


def summarise(raw_text):
	text = raw_text.strip().replace("\n","")
	extractive_summary = gensim.summarization.summarize(text, ratio=0.5)
	return summarize_chunks(extractive_summary, bart_tokenizer, bart_model)


summary = summarise(contents)
print(summary)

with open(output_path,'w', encoding="utf8") as new_f:
    new_f.write(summary)
    new_f.close()