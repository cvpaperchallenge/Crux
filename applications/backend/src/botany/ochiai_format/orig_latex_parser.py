import re


def parse_latex_text(latex_document):
    # titleを取得
    text_1 = latex_document.split("\\title{")[-1]
    raw_title, text_2 = text_1.split("\\author{")
    title = raw_title.rsplit("}", 1)[0]
    title_dict = {"content": title, "metadata": "title"}

    # authorを取得
    raw_author, text_3 = text_2.split("\\begin{abstract}")
    author = raw_author.rsplit("}", 1)[0]
    author_dict = {"content": author, "metadata": "author"}

    # abstractを取得
    abstract, text_4 = text_3.split("\n\\end{abstract}")

    # sectionを取得
    raw_section_list = text_4.lstrip("\n").split("\\section{")
    section_list = []
    section_id = 1
    for each_section in raw_section_list:
        if len(each_section) == 0:
            continue
        section_title, raw_section_text = each_section.split("}\n", 1)
        section_text = raw_section_text.lstrip("\n")
        section_dict = {
            "section_id": section_id,
            "section_title": section_title,
            "section_text": section_text,
        }
        section_list.append(section_dict)
        section_id += 1

    # subsectionを取得
    for each_section_dict in section_list:
        raw_subsection_list = each_section_dict["section_text"].split("\\subsection{")
        # subsectionを持たないsectionをはじく
        if len(raw_subsection_list) == 1:
            each_section_dict["subsection_list"] = []
            continue
        subsection_list = []
        subsection_id = 0
        for each_subsection in raw_subsection_list:
            # \section{}の後にすぐ\subsection{}が来る場合は、最初は空文字なので飛ばし、section_textは消す
            if len(each_subsection) == 0:
                subsection_id += 1
                each_section_dict["section_text"] = ""
                continue
            # \section{}の後に文章があってから\subsection{}が来る場合は、section_textを更新
            if subsection_id == 0 and len(each_subsection) != 0:
                each_section_dict["section_text"] = each_subsection
                subsection_id += 1
                continue

            subsection_title, raw_subsection_text = each_subsection.split("}\n", 1)
            subsection_text = raw_subsection_text.lstrip("\n")
            subsection_text = simple_figure_table_remover(subsection_text)
            subsection_dict = {
                "subsection_id": subsection_id,
                "subsection_title": subsection_title,
                "subsection_text": subsection_text,
            }
            subsection_list.append(subsection_dict)
            subsection_id += 1

        each_section_dict["subsection_list"] = subsection_list

    parsed_document = {
        "title": title,
        "author": author,
        "abstract": abstract,
        "section": section_list,
    }

    return parsed_document


def simple_figure_table_remover(text):
    wo_table_text = re.sub(
        r"\\begin{tabular}(.*?)\\end{tabular}", "", text, flags=re.DOTALL
    )
    wo_fig_table_text = re.sub(r"!\[\]\((.*?)\)\n", "", wo_table_text, flags=re.DOTALL)
    return wo_fig_table_text
