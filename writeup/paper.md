# A Open Source Method for Seperating Book Chapters by Main Character



## Abstract


## Introduction
Many books have multiple main characters, often each character is written from the perspective of a different main character.
Different sections are written from the perspective of different characters. Generally, these books are written in limitted third-person point of view (POV); that is to say the reader has little or or more knowledge of the situtation described than the main character does. Having a large cast of character, in particular POV characters, is a hallmark of the epic fantasy genre.

We propose a method here to detect the main/POV character for each section of the book. Detecting the main character is not a difficult task, as the strong baseline result shows. However to our knowledge there does not exist any current software to do this. We attribute this lack to its irelivent until recent times.

The surge in popularity of fiction ebooks has openned a new niche for consumer discourse processing. Tools such as the one present here, give the reader new fredoms in controling how they consume their media. 


Across its 15 books, Robert Jordan's "Wheel of Time" series had 146 POV characters (http://wot.wikia.com/w3iki/Statistical_analysis). Only about one fifth of the total word count was from the POV of the ``main character''.
George R.R. Martin's "A Song of Ice and Fire",  have over 30 in the books published so far (http://awoiaf.westeros.org/index.php/POV_character).

## Corpus Construction

## Methods

### Baseline: Most Common Named Entity 
We propose as a baseline method simply counting the named entities in each section and selecting the named entity that occurs the most as the POV character.
As shall be shown in the next section, this is a very strong baseline.

As a method it has a key advantage in that it is resistent to noise in the NER step.
With current NER methods mistakes are common. Both false positives: where non-entities being mistakenly identified as name entities; and False Negatives where a named entitites occurances being skipped. 
{TODO: CITE and Details HERE)
Simply counting the portion of occurances of each named entity is robust. False Positives will occur very few times in a given document segement, and False Negitives will not substantially decrease the over count. This same property also makes it ideal as a feature in feature combining approach.

### Feature Vectors + Machine Learning

### Reference  Counting
Using coreference resultution we can extent the most common named entity approach.
Counting each time the Named entity is referenced.



## Results 

## Conclusion

A method was shown to ...

We suggest there is a bright future for consumer facing discourse processing.
With other tools offering different enhancements allowing the reader to control their own reading.
Other useful tasks may include: timeline reordering for books with many flashbacks; untrustworthy narrator detection; event/timeline cross-referencing (and hyperlinking).
