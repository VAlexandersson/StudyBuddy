```python
import fitz
import pymupdf4llm

pdf_path = "./data/Distributed_Systems_4.pdf"

doc = fitz.open(pdf_path)

```


```python

import string
from pprint import pprint
from tqdm.auto import tqdm # for progress bars, requires !pip install tqdm

import fitz

if fitz.pymupdf_version_tuple < (1, 24, 0):
    raise NotImplementedError("PyMuPDF version 1.24.0 or later is needed.")


def to_markdown(doc: fitz.Document, pages: list = None) -> str:
    """Process the document and return the text of its selected pages."""
    if isinstance(doc, str):
        doc = fitz.open(doc)
    SPACES = set(string.whitespace)  # used to check relevance of text pieces
    if not pages:  # use all pages if argument not given
        pages = range(doc.page_count)

    class IdentifyHeaders:
        """Compute data for identifying header text."""

        def __init__(self, doc, pages: list = None, body_limit: float = None):
            """Read all text and make a dictionary of fontsizes.

            Args:
                pages: optional list of pages to consider
                body_limit: consider text with larger font size as some header
            """
            if pages is None:  # use all pages if omitted
                pages = range(doc.page_count)
            fontsizes = {}
            for pno in pages:
                page = doc[pno]
                blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_TEXT)["blocks"]
                for span in [  # look at all non-empty horizontal spans
                    s
                    for b in blocks
                    for l in b["lines"]
                    for s in l["spans"]
                    if not SPACES.issuperset(s["text"])
                ]:
                    fontsz = round(span["size"])
                    count = fontsizes.get(fontsz, 0) + len(span["text"].strip())
                    fontsizes[fontsz] = count

            # maps a fontsize to a string of multiple # header tag characters
            self.header_id = {}

            # If not provided, choose the most frequent font size as body text.
            # If no text at all on all pages, just use 12
            if body_limit is None:
                temp = sorted(
                    [(k, v) for k, v in fontsizes.items()],
                    key=lambda i: i[1],
                    reverse=True,
                )
                if temp:
                    body_limit = temp[0][0]
                else:
                    body_limit = 12

            sizes = sorted(
                [f for f in fontsizes.keys() if f > body_limit], reverse=True
            )

            # make the header tag dictionary
            for i, size in enumerate(sizes):
                self.header_id[size] = "#" * (i + 1) + " "

        def get_header_id(self, span):
            """Return appropriate markdown header prefix.

            Given a text span from a "dict"/"radict" extraction, determine the
            markdown header prefix string of 0 to many concatenated '#' characters.
            """
            fontsize = round(span["size"])  # compute fontsize
            hdr_id = self.header_id.get(fontsize, "")
            return hdr_id

    def resolve_links(links, span):
        """Accept a span bbox and return a markdown link string."""
        bbox = fitz.Rect(span["bbox"])  # span bbox
        # a link should overlap at least 70% of the span
        bbox_area = 0.7 * abs(bbox)
        for link in links:
            hot = link["from"]  # the hot area of the link
            if not abs(hot & bbox) >= bbox_area:
                continue  # does not touch the bbox
            text = f'[{span["text"].strip()}]({link["uri"]})'
            return text

    def write_text(page, clip, hdr_prefix):
        """Output the text found inside the given clip.

        This is an alternative for plain text in that it outputs
        text enriched with markdown styling.
        The logic is capable of recognizing headers, body text, code blocks,
        inline code, bold, italic and bold-italic styling.
        There is also some effort for list supported (ordered / unordered) in
        that typical characters are replaced by respective markdown characters.
        """
        out_string = ""
        code = False  # mode indicator: outputting code

        # extract URL type links on page
        links = [l for l in page.get_links() if l["kind"] == 2]

        blocks = page.get_text(
            "dict",
            clip=clip,
            flags=fitz.TEXTFLAGS_TEXT,
            sort=True,
        )["blocks"]

        for block in blocks:  # iterate textblocks
            previous_y = 0
            for line in block["lines"]:  # iterate lines in block
                if line["dir"][1] != 0:  # only consider horizontal lines
                    continue
                spans = [s for s in line["spans"]]

                this_y = line["bbox"][3]  # current bottom coord

                # check for still being on same line
                same_line = abs(this_y - previous_y) <= 3 and previous_y > 0

                if same_line and out_string.endswith("\n"):
                    out_string = out_string[:-1]

                # are all spans in line in a mono-spaced font?
                all_mono = all([s["flags"] & 8 for s in spans])

                # compute text of the line
                text = "".join([s["text"] for s in spans])
                if not same_line:
                    previous_y = this_y
                    if not out_string.endswith("\n"):
                        out_string += "\n"

                if all_mono:
                    # compute approx. distance from left - assuming a width
                    # of 0.5*fontsize.
                    delta = int(
                        (spans[0]["bbox"][0] - block["bbox"][0])
                        / (spans[0]["size"] * 0.5)
                    )
                    if not code:  # if not already in code output  mode:
                        out_string += "```"  # switch on "code" mode
                        code = True
                    if not same_line:  # new code line with left indentation
                        out_string += "\n" + " " * delta + text + " "
                        previous_y = this_y
                    else:  # same line, simply append
                        out_string += text + " "
                    continue  # done with this line

                for i, s in enumerate(spans):  # iterate spans of the line
                    # this line is not all-mono, so switch off "code" mode
                    if code:  # still in code output mode?
                        out_string += "```\n"  # switch of code mode
                        code = False
                    # decode font properties
                    mono = s["flags"] & 8
                    bold = s["flags"] & 16
                    italic = s["flags"] & 2

                    if mono:
                        # this is text in some monospaced font
                        out_string += f"`{s['text'].strip()}` "
                    else:  # not a mono text
                        # for first span, get header prefix string if present
                        if i == 0:
                            hdr_string = hdr_prefix.get_header_id(s)
                        else:
                            hdr_string = ""
                        prefix = ""
                        suffix = ""
                        if hdr_string == "":
                            if bold:
                                prefix = "**"
                                suffix += "**"
                            if italic:
                                prefix += "_"
                                suffix = "_" + suffix

                        ltext = resolve_links(links, s)
                        if ltext:
                            text = f"{hdr_string}{prefix}{ltext}{suffix} "
                        else:
                            text = f"{hdr_string}{prefix}{s['text'].strip()}{suffix} "
                        text = (
                            text.replace("<", "&lt;")
                            .replace(">", "&gt;")
                            .replace(chr(0xF0B7), "-")
                            .replace(chr(0xB7), "-")
                            .replace(chr(8226), "-")
                            .replace(chr(9679), "-")
                        )
                        out_string += text
                previous_y = this_y
                if not code:
                    out_string += "\n"
            out_string += "\n"
        if code:
            out_string += "```\n"  # switch of code mode
            code = False
        return out_string.replace(" \n", "\n")

    hdr_prefix = IdentifyHeaders(doc, pages=pages)
    md_string = ""
    md_pages = []  # list to hold text and metadata
    for pno in tqdm(pages):
        page = doc[pno]
        # 1. first locate all tables on page
        tabs = page.find_tables()
        md_page = ""  # string to hold markdown for this page

        # 2. make a list of table boundary boxes, sort by top-left corner.
        # Must include the header bbox, which may be external.
        tab_rects = sorted(
            [
                (fitz.Rect(t.bbox) | fitz.Rect(t.header.bbox), i)
                for i, t in enumerate(tabs.tables)
            ],
            key=lambda r: (r[0].y0, r[0].x0),
        )

        # 3. final list of all text and table rectangles
        text_rects = []
        # compute rectangles outside tables and fill final rect list
        for i, (r, idx) in enumerate(tab_rects):
            if i == 0:  # compute rect above all tables
                tr = page.rect
                tr.y1 = r.y0
                if not tr.is_empty:
                    text_rects.append(("text", tr, 0))
                text_rects.append(("table", r, idx))
                continue
            # read previous rectangle in final list: always a table!
            _, r0, idx0 = text_rects[-1]

            # check if a non-empty text rect is fitting in between tables
            tr = page.rect
            tr.y0 = r0.y1
            tr.y1 = r.y0
            if not tr.is_empty:  # empty if two tables overlap vertically!
                text_rects.append(("text", tr, 0))

            text_rects.append(("table", r, idx))

            # there may also be text below all tables
            if i == len(tab_rects) - 1:
                tr = page.rect
                tr.y0 = r.y1
                if not tr.is_empty:
                    text_rects.append(("text", tr, 0))

        if not text_rects:  # this will happen for table-free pages
            text_rects.append(("text", page.rect, 0))
        else:
            rtype, r, idx = text_rects[-1]
            if rtype == "table":
                tr = page.rect
                tr.y0 = r.y1
                if not tr.is_empty:
                    text_rects.append(("text", tr, 0))

        # we have all rectangles and can start outputting their contents
        for rtype, r, idx in text_rects:
            if rtype == "text":  # a text rectangle
                text = write_text(page, r, hdr_prefix)# write MD content
                text += "\n"
                md_page += text  
                md_string += text  # write MD content
            else:  # a table rect
                md_tab = tabs[idx].to_markdown(clean=False)
                
                md_page += md_tab
                md_string += md_tab
            
        md_string += "\n-----\n\n"
        
        # Split the page into blocks for further processing
        blocks = md_page.split("\n\n")
        for i, block in enumerate(blocks):
            text = block.replace("-\n", "")
            text = block.replace("-**\n**", "")
            
             
            text = text.replace("\n", " ").strip()
            
            if text == "":
                blocks.pop(i)
            else:
                blocks[i] = text
        md_pages.append({
            "document": md_page, 
            "page_number": pno+1, 
            "blocks": blocks
            })  
    return md_pages


```


```python
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def identify_potential_headers_or_footers(md_p, header: bool, threshold=0.8):
    # Extract first or last blocks
    blocks = [page["blocks"][0] if header else page["blocks"][-1] for page in md_p if page["blocks"]]

    # Identify potential headers or footers
    potential_blocks = []
    for i in tqdm(range(len(blocks))):
        similar_blocks = [j for j, similarity in enumerate([similar(blocks[i], blocks[j]) for j in range(len(blocks))]) if similarity > threshold]
        if len(similar_blocks) > 1:
            potential_blocks.append((i, similar_blocks))

    return potential_blocks

def has_header_or_footer(md_p, potential_blocks):
    # Convert potential_blocks to a set for faster lookup
    block_indices = set(index for index, _ in potential_blocks)

    # Create a list of booleans indicating whether each page has a potential header or footer
    has_block = [i in block_indices for i in range(len(md_p))]

    return has_block

def remove_headers_or_footers(md_p, header: bool, has_block):
    # Only keep blocks that are not potential headers or footers
    for i, page in enumerate(md_p):
        if has_block[i]:
            page["blocks"] = page["blocks"][1:] if header else page["blocks"][:-1]

    return md_p

def remove_headers_and_footers(md_p):
    header = [True, False]
    for bool_header in header:
        potential_blocks = identify_potential_headers_or_footers(md_p, header=bool_header)
        has_block = has_header_or_footer(md_p, potential_blocks)
        md_p = remove_headers_or_footers(md_p, header=bool_header, has_block=has_block)
    return md_p

def find_entities_by_page(paragraphs: list[dict], page_number: int):
    return [entity for entity in paragraphs if entity.get('pagenumber') == page_number]


def to_block_list(paragraphs: list[dict]):
    id_counter = 0
    new_dict = []
    for i in range(len(paragraphs)):
        for block in paragraphs[i]["blocks"]:
            new_dict.append({"id": id_counter, "block": block, "pagenumber": paragraphs[i]["page_number"]})
            id_counter += 1
    return new_dict


```


```python
doc = fitz.open(pdf_path)  # open input file
pages = range(18, 632)  
#pages = range(doc.page_count)  # default page range
md_paragraphs = to_markdown(doc, pages=pages) # dict_keys(['document', 'page_number', 'blocks'])
md_p = remove_headers_and_footers(md_paragraphs)
block_list = to_block_list(md_p)

entities_on_page = find_entities_by_page(block_list, 30)

for entity in entities_on_page:
    print(entity)
```

```python
import pandas as pd
from spacy.lang.en import English # see https://spacy.io/usage for install instructions

nlp = English()

# Add a sentencizer pipeline, see https://spacy.io/api/sentencizer/
nlp.add_pipe("sentencizer")

for item in tqdm(block_list):
    item["sentences"] = list(nlp(item["block"]).sents)

    # Make sure all sentences are strings
    item["sentences"] = [str(sentence) for sentence in item["sentences"]]

    # Count the sentences
    item["block_sentence_count_spacy"] = len(item["sentences"])
    
df = pd.DataFrame(block_list)
df['num_sentences'] = df['block'].apply(lambda x: x.count('.') + x.count('!') + x.count('?'))
df['num_words'] = df['block'].apply(lambda x: len(x.split()))
df['num_chars'] = df['block'].apply(len)
df['token_count'] = df['num_chars'].apply(lambda x: round(x/4))

df.describe().round(2)
```


```python
#df_f = df[(df["block"].str.startswith(("#", "-", "**")) | df["block"].str.match(r"^\d+\.")) | (df["num_words"] >= 20)]
df_f = df[(df["block"].str.startswith(("#", "-")) | df["block"].str.match(r"^\d+\.")) | (df["num_chars"] >= 10 )]

df_sentence = df.explode("sentences")
df_sentence = df_sentence.rename(columns={"sentences": "sentence"})
df_sentence = df_sentence.rename(columns={"pagenumber": "page"})
df_sentence = df_sentence[["id", "page", "sentence"]]
df_sentence['num_words'] = df_sentence['sentence'].apply(lambda x: len(x.split()))
df_sentence['num_chars'] = df_sentence['sentence'].apply(len)
df_sentence['token_count'] = df_sentence['num_chars'].apply(lambda x: round(x/4))
df_sentence = df_sentence[(df_sentence["sentence"].str.startswith("#") | (df["num_chars"] >= 10 )]
df_sentence = df_sentence[(df_sentence["sentence"].str.startswith("#", "-") | (df["num_chars"] >= 20 )]
df_sentence = df_sentence[(df_sentence["sentence"].str.startswith("#", "-", "**") | df["block"].str.match(r"^\d+\.")) | (df["num_chars"] >= 30 )]

```


```python
df_sentence
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>page</th>
      <th>sentence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>18</td>
      <td>The pace at which computer systems change was,...</td>
    </tr>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>18</td>
      <td>From 1945, when the modern computer era began,...</td>
    </tr>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>18</td>
      <td>Moreover, lacking a way to connect them, these...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>18</td>
      <td>Starting in the mid-1980s, however, two advanc...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>18</td>
      <td>The first was the development of powerful micr...</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>3831</th>
      <td>3831</td>
      <td>631</td>
      <td>Access point, 9 Access transparency, _see_ Dis...</td>
    </tr>
    <tr>
      <th>3833</th>
      <td>3833</td>
      <td>631</td>
      <td>Application-layer switch, 163 Architectural pe...</td>
    </tr>
    <tr>
      <th>3839</th>
      <td>3839</td>
      <td>632</td>
      <td>Causal history, 267 Causality, 267 CDN, _see_ ...</td>
    </tr>
    <tr>
      <th>3854</th>
      <td>3854</td>
      <td>632</td>
      <td>Client stub, 148 , 194 Client-server computing...</td>
    </tr>
    <tr>
      <th>3855</th>
      <td>3855</td>
      <td>632</td>
      <td>cache hit, 429 coherence detection, 443 cohere...</td>
    </tr>
  </tbody>
</table>
<p>13643 rows × 3 columns</p>
</div>




```python
len(df), len(df[df["block"].str.startswith("#")]), len(df[~df["block"].str.startswith(("#", "**"))])
```




    (3861, 217, 3020)




```python
df_f = df[(df["block"].str.startswith(("#", "-")) | df["block"].str.match(r"^\d+\.")) | (df["num_words"] >= 20)]
```


```python
import spacy

blocks = df[df["block"].str.startswith("#")]["block"]

data = {
    "heading": ["# Introduction", "# Methodology", "# Results"],
    "non-heading": ["This is some text.", "Here are some results.", "This is a conclusion."]
}

nlp = spacy.load('en_core_web_md')
nlp.add_pipe("classy_classification", 
    config={
        "data": data,
        "model": "spacy"
    }
)
print(nlp("Is this a heading?")._.cats)
```


```python
blocks = df["block"]

blocks.dtypes
print(blocks)
```

    0       The pace at which computer systems change was,...
    1       Starting in the mid-1980s, however, two advanc...
    2       The second development was the invention of hi...
    3       Parallel to the development of increasingly po...
    4       And the story continues. As digitalization of ...
                                  ...                        
    3856                               Closure mechanism, 348
    3857                                       container, 348
    3858       Callback, 205 CAP theorem, 506 Capability, 596
    3859                             Cloud computing, 12 , 98
    3860    DS 4.02 downloaded by VIKTOR.ALEXAND **@** GMA...
    Name: block, Length: 3861, dtype: object



```python
df.describe().round(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>page</th>
      <th>char_count</th>
      <th>word_count</th>
      <th>sentence_count</th>
      <th>token_count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>686.00</td>
      <td>686.00</td>
      <td>686.00</td>
      <td>686.00</td>
      <td>686.00</td>
      <td>686.00</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>342.50</td>
      <td>343.50</td>
      <td>2592.11</td>
      <td>428.92</td>
      <td>30.45</td>
      <td>648.03</td>
    </tr>
    <tr>
      <th>std</th>
      <td>198.18</td>
      <td>198.18</td>
      <td>712.89</td>
      <td>132.26</td>
      <td>64.93</td>
      <td>178.22</td>
    </tr>
    <tr>
      <th>min</th>
      <td>0.00</td>
      <td>1.00</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>1.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>171.25</td>
      <td>172.25</td>
      <td>2285.75</td>
      <td>367.25</td>
      <td>18.00</td>
      <td>571.44</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>342.50</td>
      <td>343.50</td>
      <td>2782.50</td>
      <td>452.00</td>
      <td>23.00</td>
      <td>695.62</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>513.75</td>
      <td>514.75</td>
      <td>3093.25</td>
      <td>503.00</td>
      <td>26.00</td>
      <td>773.31</td>
    </tr>
    <tr>
      <th>max</th>
      <td>685.00</td>
      <td>686.00</td>
      <td>3724.00</td>
      <td>1033.00</td>
      <td>819.00</td>
      <td>931.00</td>
    </tr>
  </tbody>
</table>
</div>




```python
df.dtypes
```




    id                             int64
    block                         object
    pagenumber                     int64
    sentences                     object
    block_sentence_count_spacy     int64
    num_sentences                  int64
    num_words                      int64
    num_chars                      int64
    token_count                    int64
    dtype: object


