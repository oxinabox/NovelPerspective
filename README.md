
 - [Live WebApp](https://white.ucc.asn.au/tools/np)
 - [YouTube Demo](https://youtu.be/iu41pUF4wTY)
 
### Paper:

[NovelPerspective: Identifying Point of View Characters, 2018; Lyndon White, Roberto Togneri, Wei Liu, and Mohammed Bennamoun. 56th Annual Meeting of the Association for Computational Linguistics (ACL), System Demonstrations](https://white.ucc.asn.au/publications/White2018NovelPerspective.pdf)


## Details

A tool for modifying (transforming) ebooks, based on the point of view character. Epic fantasy novels are notable for their large cast of Point of View characters. Sometimes you just don’t care for some of them, or you want to read just a single characters story-line, for example on a second read through. NovelPerspectives uses machine learning to discover the main character of a chapter, and transforms the book to include or exclude characters.

 - The `serve` folder contrains the web-app code
 - The `proto` folder contained all our evaulations and the "brains" of our system.
     - We do not include any of the data used in the evaluations, as this would have obvious copyright issues
     - The ebooks that form the basis of our datasets are available from many online stores
     - All preprocessing to load them up and convert them to the exact form we used for processing is included.
 -  `results` contains the results from the evaluations reported in the paper, and implemented in `proto`.
 - The `trained_models` folder includes the pickled pretrained models
	 - The models were trained on first four books of George R. R. Martin's ''A Song of Ice and Fire'', the two books of Leigh Bardugo's ''Six of Crows'' duology, and the first 9 volumes of Robert Jordan's ''Wheel of Time''.
     - It is an interesting argument that one might say that these models are derived works from the books, however it is not possible to actually get back any of the book's text from them, so we are assuming the publishers will not have issue.
