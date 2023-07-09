from typing import Final, List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl


class Paper(BaseModel):
    """

    Pydantic model which stores single paper infomation.

    """

    title: str
    author: str
    abstract: str
    cvf: HttpUrl
    pdf: HttpUrl


def get_paper_page_urls() -> List[str]:
    """

    Return a list of CVF page URL. The list includes all 2,359 papers
    accepted by CVPR 2023.

    """

    cvf_root_url: Final = "https://openaccess.thecvf.com"
    cvf_all_paper_url: Final = cvf_root_url + "/CVPR2023?day=all"

    html: Final = requests.get(cvf_all_paper_url).text
    bs: Final = BeautifulSoup(html, "html.parser")
    parsed_tags = bs.select(".ptitle > a")
    return [cvf_root_url + parsed_tag.get("href") for parsed_tag in parsed_tags]


def parse_paper_page(page_url: str) -> Paper:
    """

    Parse a paper page and return Paper object.

    """

    html: Final = requests.get(page_url).text
    bs: Final = BeautifulSoup(html, "html.parser")

    title: Final = bs.select_one("#papertitle").text.strip()
    author: Final = bs.select_one("#authors b").text.strip()
    abstract: Final = bs.select_one("#abstract").text.strip()
    cvf: Final = page_url
    pdf: Final = (
        "https://openaccess.thecvf.com/content/CVPR2023/papers/"
        + page_url.removesuffix(".html").split("/")[-1]
        + (".pdf")
    )

    return Paper(
        title=title,
        author=author,
        abstract=abstract,
        cvf=cvf,  # type: ignore
        pdf=pdf,  # type: ignore
    )


if __name__ == "__main__":
    paper = parse_paper_page(
        "https://openaccess.thecvf.com/content/CVPR2023/html/Ci_GFPose_Learning_3D_Human_Pose_Prior_With_Gradient_Fields_CVPR_2023_paper.html"
    )
    print(paper.json())
