# evaluate_neuralFakenewsDetectors
This text file summarizes the steps to reproduce our results in the paper.
We have also uploaded result logs produced by perturbations from our experiments.

Install the following:
- Required packages:
 - Download geckodriver for Linux: https://github.com/mozilla/geckodriver/releases
 - python >= 3.6, spacy, nltk
 - web query: selenium, seleniumrequests, urllib

- To run the script: source run.sh
The script runs 'entity_shuffle' perturbation for 1000 instances. It will take ~10hrs to run one type of perturbation for 1000 articles.
The following command line arguments are used. The available options are listed below:
file_name : processed_human.json for semantic, processed_machine.json for syntactic perturbations
trigger : entity_shuffle, sentence_shuffle, sentiment, alter_numbers, so_exchange, syntactic_MH
model : groverAI, gpt2, fakebox, all (To use fakebox, create a user account in https://docs.veritone.com/#/developer/machine-box/boxes/fakebox)
analyze : True (to get logs)
flip_size: 0 - 1.0 (level of perturbations)
sample_size : Number of articles subjected to perturbation (minimum:1)
