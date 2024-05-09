import fitz
import string
from tqdm import tqdm


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

        def get_header_id(self, span, line_spans):
            """Return appropriate markdown header prefix.

            Given a text span from a "dict"/"radict" extraction, determine the
            markdown header prefix string of 0 to many concatenated '#' characters.
            """
            fontsize = round(span["size"])  # compute fontsize
            hdr_id = self.header_id.get(fontsize, "")

            bold = span["flags"] & 16
            standalone = len(line_spans) == 1 and not SPACES.issuperset(span["text"])
            if bold and standalone and not hdr_id:
                # If the span is bold and standalone, consider it as a heading
                if hdr_id == "":
                    smallest_heading = max(self.header_id.values(), default="")
                    hdr_id = "#" * (len(smallest_heading.strip()) + 1) + " "

                
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
                            hdr_string = hdr_prefix.get_header_id(s, line["spans"])
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