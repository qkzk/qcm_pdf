#! /usr/bin/python3

from random import sample
import argparse
import subprocess

from qcm_parser.parser import ParseQCM, QCM_Part, QCM_Question


class MarkdownExporter:
    """Export a QCM into a markdown file content"""

    NOCODE_HEADER = """
---
theme: "metropolis"
geometry: "margin=1.5cm"
header-includes:
- \\usepackage{{fancyhdr}} 
- \\pagestyle{{fancy}} 
- \\fancyhead[C]{{ {0} }}
- \\fancyhead[LE,LO,RE,RO]{{}} 
- \\fancyfoot[C]{{ }} 
- \\thispagestyle{{fancy}} 

---

"""

    CODE_HEADER = """
---
theme: "metropolis"
geometry: "margin=1.5cm"
header-includes:
- \\usepackage{{fancyhdr}} 
- \\pagestyle{{fancy}} 
- \\fancyhead[C]{{ {0} }}
- \\fancyhead[LE,LO,RE,RO]{{}} 
- \\fancyfoot[C]{{ }} 
- \\thispagestyle{{fancy}} 
- \\usepackage{{tcolorbox}} 
- \\newtcolorbox{{myquote}}{{colback=teal!10!white, colframe=teal!55!black}}
- \\renewenvironment{{Shaded}}{{\\begin{{myquote}}}}{{\\end{{myquote}}}}

---

"""

    def __init__(self, qcm: ParseQCM, code_present: bool = False):
        self.qcm = qcm
        self.header = self.pick_header(code_present)

    def pick_header(self, code_present: bool) -> str:
        """
        returns a header. With or without colored codeblocks
        This is necessary since providing a colored codeblock header without
        codeblock crashes pandoc
        """
        if code_present:
            return self.CODE_HEADER
        return self.NOCODE_HEADER

    def export(self, first: bool = False) -> str:
        """shuffle the questions and anwsers, creating a set new QCM page"""
        string = self.header_formater() if first else ""
        parts = sample(self.qcm.parts, len(self.qcm.parts))
        for part in parts:
            string += self.part_formater(part)
        string += "\n\n\\newpage\n\n"
        return string

    def header_formater(self) -> str:
        """Format the header of the first page"""
        return self.header.format(self.qcm.title)

    def part_formater(self, part: QCM_Part):
        """Format a part"""
        string = "## " + part.title + "\n\n"
        if part.text:
            string += part.text + "\n\n"
        questions = sample(part.questions, len(part.questions))
        for question in questions:
            string += self.question_formater(question)
        return string

    def question_formater(self, question: QCM_Question) -> str:
        """Format a question"""
        string = "### " + question.title + "\n\n"
        if question.text:
            string += question.text + "\n\n"
        string += self.answers_formater(question)
        return string

    @staticmethod
    def answers_formater(question: QCM_Question) -> str:
        """Format the answers"""
        string = ""
        answsers = sample(question.answers, len(question.answers))
        for answer in answsers:
            string += "- [ ] " + answer.title + "\n"
        string += "\n"
        return string

    def __repr__(self):
        return self.export()


class PDF_Exporter:
    """Export a markdown file into a pdf with a page per student"""

    def __init__(
        self,
        qcm_content: ParseQCM,
        nb_copy: int,
        input_filename: str,
        code_present: bool,
    ):
        self.qcm_content = qcm_content
        self.nb_copy = nb_copy
        self.input_filename = input_filename
        self.code_present = code_present
        self.file_content = self.__generate_qcm()

    def __generate_qcm(self) -> str:
        string = ""
        for copy_nb in range(self.nb_copy):
            string += MarkdownExporter(
                self.qcm_content, code_present=self.code_present
            ).export(copy_nb == 0)
        string = self.__prevent_gt_lt(string)
        return string

    def __prevent_gt_lt(self, string: str):
        return string.replace("&lt;", "<").replace("&gt;", ">")

    def write_qcm(self):
        """write the questions to a file and returns its filename"""
        output_filename = self.input_filename[:-3] + "_QUESTIONS.md"
        with open(output_filename, "w") as output_file:
            output_file.write(self.file_content)
        return output_filename


def convert_argument_parser():
    """Read command line arguments, returns a namespace of arguments"""
    parser = argparse.ArgumentParser(
        description="""Convert a QCM into different format: PDF or HTML.
I need a filepath a number of copy and the option -w or -p
        """
    )
    parser.add_argument(
        "filename",
        type=str,
    )

    parser.add_argument(
        "-n",
        "--nb_copy",
        type=int,
        default=35,
    )

    parser.add_argument(
        "-c",
        "--code_present",
        action="store_true",
        help="Do you have codeblocks ? Will crash if set to True and there's no code blocks",
        default=False,
    )

    arguments = parser.parse_args()

    return arguments


def parse_file(filename: str) -> ParseQCM:
    """
    Uses a Process to parse the file at `filename` into a QCM.
    """
    output_dict = {}
    ParseQCM.from_file_into_dict(filename, output_dict, mode="pdf")

    if "error" in output_dict:
        error = output_dict["error"]
        if isinstance(error, Exception):
            raise error
        else:
            raise ValueError(f"Parsing went wrong: {error}")
    if not "qcm" in output_dict:
        raise ValueError("Parser didn't terminate properly")

    return output_dict["qcm"]


def call_pandoc(output_filename: str) -> str:
    """call pandoc on the written file and convert it to pdf. Returns the output filename"""
    pdf_filename = output_filename[:-3] + ".pdf"
    args = ["pandoc", output_filename, "-o", pdf_filename]
    subprocess.check_call(args)
    return pdf_filename


def main():
    arguments = convert_argument_parser()
    output_markdown_filename = PDF_Exporter(
        qcm_content=parse_file(arguments.filename),
        nb_copy=arguments.nb_copy,
        input_filename=arguments.filename,
        code_present=arguments.code_present,
    ).write_qcm()
    output_pdf_filename = call_pandoc(output_filename=output_markdown_filename)
    print(output_pdf_filename)


if __name__ == "__main__":
    main()
